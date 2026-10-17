"""FitMate: asisten latihan pribadi berbasis web (Flask + data JSON).

Cara menjalankan lokal:   python app.py
Vercel mencari variabel `app` di file ini (lihat README.md untuk deployment).
"""
import hmac
import os
import secrets
from datetime import date, datetime, timedelta, timezone
from functools import wraps
from urllib.parse import urlparse

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import charts
import repository as repo
import storage
import validators
from i18n import normalize_lang, translate
from recommender import EXERCISES_PER_SESSION, build_program

ON_VERCEL = bool(os.environ.get("VERCEL"))

# Di Vercel, file statis dilayani dari folder public/ oleh CDN Vercel.
# Secara lokal, Flask melayani folder yang sama supaya /style.css juga jalan.
app = Flask(
    __name__,
    static_folder=None if ON_VERCEL else "public",
    static_url_path="",
)
app.config.update(
    # Set SECRET_KEY di environment (lihat README). Tanpa itu di Vercel, kunci acak dipakai
    # dan semua sesi login hilang tiap instance restart.
    SECRET_KEY=os.environ.get("SECRET_KEY") or (secrets.token_hex(32) if ON_VERCEL else "dev-only-secret-key"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=ON_VERCEL,
    PERMANENT_SESSION_LIFETIME=timedelta(days=14),
)

EXERCISES = storage.load_seed("exercises")
EXERCISE_BY_ID = {ex["id"]: ex for ex in EXERCISES}

MUSCLES = ["chest", "shoulders", "triceps", "back", "biceps", "quads", "hamstrings", "glutes", "calves", "core"]
EQUIPMENT = ["bodyweight", "dumbbell", "gym"]
LEVELS = ["beginner", "intermediate", "advanced"]
GOALS = ["lose_fat", "muscle", "strength", "fitness"]
MINUTES = sorted(EXERCISES_PER_SESSION)
GROUPS = [("session.push", "push"), ("session.pull", "pull"), ("session.legs", "legs"), ("muscle.core", "core")]


# ---------------------------------------------------------------- utilitas
def today():
    """Tanggal hari ini menurut zona waktu pengguna (default UTC+7). Server Vercel memakai UTC."""
    offset = float(os.environ.get("FITMATE_UTC_OFFSET", "7"))
    return (datetime.now(timezone.utc) + timedelta(hours=offset)).date()


def safe_next(target):
    """Hanya izinkan redirect ke path di situs ini (cegah open redirect)."""
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return None
    return target if not urlparse(target).netloc else None


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def start_session(user):
    """Mulai sesi login baru. Sesi lama dibuang (cegah session fixation)."""
    lang = session.get("lang")
    session.clear()
    if lang:
        session["lang"] = lang
    session["uid"] = user["id"]
    session.permanent = True


def notify(key, category="info"):
    flash(translate(g.lang, key), category)


# ---------------------------------------------------------------- hooks
@app.before_request
def prepare_request():
    g.lang = normalize_lang(session.get("lang"))
    g.user = None
    g.profile = None
    g.session_lost = False
    if request.endpoint == "static":
        return
    uid = session.get("uid")
    if uid:
        g.user = repo.get_user(uid)
        if g.user is None:
            # Akun tidak ada lagi (mis. data sementara di server terhapus).
            session.pop("uid", None)
            g.session_lost = True
        else:
            g.profile = repo.get_profile(uid)
    if request.method == "POST":
        sent = request.form.get("csrf_token", "")
        expected = session.get("csrf", "")
        if not expected or not hmac.compare_digest(sent, expected):
            abort(400)


@app.after_request
def security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response


@app.context_processor
def template_helpers():
    lang = g.get("lang", "id")

    def t(key, **values):
        return translate(lang, key, **values)

    def fmt_short(iso):
        d = date.fromisoformat(iso)
        month = translate(lang, f"month.{d.month}")
        return f"{d.day} {month}" if lang == "id" else f"{month} {d.day}"

    def fmt_date(iso):
        d = date.fromisoformat(iso)
        month = translate(lang, f"month.{d.month}")
        return f"{d.day} {month} {d.year}" if lang == "id" else f"{month} {d.day}, {d.year}"

    def exercise_label(exercise_id):
        ex = EXERCISE_BY_ID.get(exercise_id)
        return ex["name"][lang] if ex else exercise_id

    return {
        "t": t,
        "lang": lang,
        "user": g.get("user"),
        "profile": g.get("profile"),
        "csrf_token": csrf_token,
        "ephemeral": ON_VERCEL or bool(os.environ.get("FITMATE_EPHEMERAL")),
        "fmt_short": fmt_short,
        "fmt_date": fmt_date,
        "exercise_label": exercise_label,
        "today_iso": today().isoformat(),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            notify("flash.session_lost" if g.session_lost else "flash.need_login", "error")
            return redirect(url_for("login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)

    return wrapped


def profile_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.profile is None:
            notify("flash.need_profile", "info")
            return redirect(url_for("profile"))
        return view(*args, **kwargs)

    return wrapped


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", title_key="err.404.title", text_key="err.404.text"), 404


@app.errorhandler(400)
def bad_request(_error):
    return render_template("error.html", title_key="err.400.title", text_key="err.400.text"), 400


# ---------------------------------------------------------------- halaman publik
@app.get("/")
def index():
    sample = build_program(
        {"days": 3, "equipment": "bodyweight", "level": "beginner", "minutes": 30, "goal": "fitness"},
        EXERCISES,
    )
    first_session = next(day for day in sample["days"] if day["session"])
    return render_template("index.html", sample=sample, first_session=first_session)


@app.get("/lang/<code>")
def set_language(code):
    if code in ("id", "en"):
        session["lang"] = code
    ref = urlparse(request.referrer or "")
    if ref.netloc == request.host and ref.path:
        return redirect(ref.path + (f"?{ref.query}" if ref.query else ""))
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))
    errors, values = {}, {}
    if request.method == "POST":
        data, errors = validators.validate_register(request.form)
        values = {"name": data["name"], "email": data["email"]}
        if not errors:
            password_hash = generate_password_hash(data["password"], method="pbkdf2:sha256")
            user = repo.create_user(data["name"], data["email"], password_hash)
            if user is None:
                errors["email"] = "err.email_taken"
            else:
                start_session(user)
                notify("flash.registered", "success")
                return redirect(url_for("profile"))
        notify("flash.form_errors", "error")
    return render_template("register.html", errors=errors, values=values)


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))
    email = ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        user = repo.get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], request.form.get("password") or ""):
            start_session(user)
            target = safe_next(request.form.get("next"))
            if target:
                return redirect(target)
            return redirect(url_for("dashboard" if repo.get_profile(user["id"]) else "profile"))
        notify("flash.login_failed", "error")
    return render_template("login.html", email=email, next_url=request.args.get("next", ""))


@app.post("/logout")
def logout():
    lang = session.get("lang")
    session.clear()
    if lang:
        session["lang"] = lang
    notify("flash.logged_out", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------- profil
PROFILE_DEFAULTS = {"goal": "fitness", "level": "beginner", "equipment": "bodyweight", "days": 3, "minutes": 45}


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    errors = {}
    values = g.profile or PROFILE_DEFAULTS
    if request.method == "POST":
        data, errors = validators.validate_profile(request.form)
        if errors:
            values = {key: request.form.get(key, "") for key in ("age", "height_cm", "weight_kg", "goal", "level", "days", "equipment", "minutes")}
            values["has_condition"] = data["has_condition"]
            notify("flash.form_errors", "error")
        else:
            uid = g.user["id"]
            repo.save_profile(uid, data)
            weights = repo.list_weights(uid)
            if not weights or weights[-1]["weight_kg"] != data["weight_kg"]:
                repo.add_weight(uid, today().isoformat(), data["weight_kg"])
            notify("flash.profile_saved", "success")
            return redirect(url_for("program"))
    return render_template(
        "profile.html", errors=errors, values=values,
        goals=GOALS, levels=LEVELS, equipment=EQUIPMENT, minutes=MINUTES,
    )


@app.post("/account/delete")
@login_required
def delete_account():
    repo.delete_user_and_data(g.user["id"])
    lang = session.get("lang")
    session.clear()
    if lang:
        session["lang"] = lang
    notify("flash.account_deleted", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------- dashboard dan program
@app.get("/dashboard")
@profile_required
def dashboard():
    uid = g.user["id"]
    now = today()
    program = build_program(g.profile, EXERCISES)
    today_day = program["days"][now.weekday()]
    week_start = now - timedelta(days=now.weekday())

    logs = repo.list_workouts(uid)
    done_days = {r["date"] for r in logs if week_start.isoformat() <= r["date"] <= now.isoformat()}
    planned = g.profile["days"]

    weights = repo.list_weights(uid)
    weight_info = None
    if weights:
        delta = weights[-1]["weight_kg"] - weights[0]["weight_kg"]
        weight_info = {
            "latest": weights[-1],
            "first_date": weights[0]["date"],
            "delta": f"{delta:+.1f}" if len(weights) > 1 else None,
        }

    return render_template(
        "dashboard.html",
        program=program, today_day=today_day, today_index=now.weekday(),
        done=len(done_days), planned=planned,
        percent=min(100, round(len(done_days) / planned * 100)),
        weight_info=weight_info, last_log=logs[0] if logs else None,
    )


@app.get("/program")
@profile_required
def program():
    built = build_program(g.profile, EXERCISES)
    return render_template(
        "program.html", program=built, today_index=today().weekday(),
        expected=EXERCISES_PER_SESSION[g.profile["minutes"]],
    )


# ---------------------------------------------------------------- pustaka latihan
@app.get("/exercises")
@login_required
def exercises():
    q = (request.args.get("q") or "").strip().lower()
    muscle = request.args.get("muscle", "")
    equip = request.args.get("equipment", "")
    level = request.args.get("level", "")
    items = [
        ex for ex in EXERCISES
        if (not q or q in ex["name"]["id"].lower() or q in ex["name"]["en"].lower())
        and (not muscle or ex["muscle"] == muscle)
        and (not equip or ex["equipment"] == equip)
        and (not level or ex["level"] == level)
    ]
    items.sort(key=lambda ex: ex["name"][g.lang].lower())
    return render_template(
        "exercises.html", items=items, q=request.args.get("q", ""), muscle=muscle, equip=equip, level=level,
        muscles=MUSCLES, equipment=EQUIPMENT, levels=LEVELS,
    )


@app.get("/exercises/<exercise_id>")
@login_required
def exercise_detail(exercise_id):
    ex = EXERCISE_BY_ID.get(exercise_id)
    if ex is None:
        abort(404)
    history = [r for r in repo.list_workouts(g.user["id"]) if r["exercise_id"] == exercise_id]
    loads = [r["weight_kg"] for r in history if r["weight_kg"] > 0]
    return render_template("exercise_detail.html", ex=ex, history=history[:5], best=max(loads) if loads else None)


# ---------------------------------------------------------------- catat latihan
def exercise_groups():
    groups = []
    for label_key, category in GROUPS:
        items = sorted((e for e in EXERCISES if e["category"] == category), key=lambda e: e["name"][g.lang].lower())
        groups.append((label_key, items))
    return groups


@app.route("/log", methods=["GET", "POST"])
@login_required
def log():
    uid = g.user["id"]
    errors = {}
    values = {"date": today().isoformat(), "exercise_id": request.args.get("exercise", ""), "sets": "", "reps": "", "weight_kg": "0", "note": ""}
    if request.method == "POST":
        data, errors = validators.validate_workout(request.form, EXERCISE_BY_ID, today())
        if errors:
            values = {k: request.form.get(k, "") for k in values}
            notify("flash.form_errors", "error")
        else:
            repo.add_workout(uid, data)
            notify("flash.log_saved", "success")
            return redirect(url_for("log"))
    return render_template(
        "log.html", errors=errors, values=values, groups=exercise_groups(),
        history=repo.list_workouts(uid)[:50], editing=False,
    )


@app.route("/log/<log_id>/edit", methods=["GET", "POST"])
@login_required
def edit_log(log_id):
    uid = g.user["id"]
    row = repo.get_workout(uid, log_id)
    if row is None:
        abort(404)
    errors = {}
    values = row
    if request.method == "POST":
        data, errors = validators.validate_workout(request.form, EXERCISE_BY_ID, today())
        if errors:
            values = {k: request.form.get(k, "") for k in ("date", "exercise_id", "sets", "reps", "weight_kg", "note")}
            notify("flash.form_errors", "error")
        else:
            repo.update_workout(uid, log_id, data)
            notify("flash.log_updated", "success")
            return redirect(url_for("log"))
    return render_template("log.html", errors=errors, values=values, groups=exercise_groups(), history=[], editing=True, log_id=log_id)


@app.post("/log/<log_id>/delete")
@login_required
def delete_log(log_id):
    if not repo.delete_workout(g.user["id"], log_id):
        abort(404)
    notify("flash.log_deleted", "info")
    return redirect(url_for("log"))


# ---------------------------------------------------------------- progres
def _short(iso):
    d = date.fromisoformat(iso)
    month = translate(g.lang, f"month.{d.month}")
    return f"{d.day} {month}" if g.lang == "id" else f"{month} {d.day}"


def render_progress(errors=None, values=None):
    """Halaman progres lengkap. Dipakai juga saat formulir berat badan salah isi."""
    uid = g.user["id"]
    now = today()
    weights = repo.list_weights(uid)
    logs = repo.list_workouts(uid)

    weight_chart = charts.line_chart(
        [(_short(w["date"]), w["weight_kg"]) for w in weights],
        translate(g.lang, "progress.weight_aria"), " kg",
    )

    # Total set per minggu untuk 8 minggu terakhir (minggu mulai hari Senin).
    this_monday = now - timedelta(days=now.weekday())
    mondays = [this_monday - timedelta(weeks=i) for i in range(7, -1, -1)]
    totals = {m.isoformat(): 0 for m in mondays}
    for row in logs:
        d = date.fromisoformat(row["date"])
        key = (d - timedelta(days=d.weekday())).isoformat()
        if key in totals:
            totals[key] += row["sets"]
    sets_chart = ""
    if any(totals.values()):
        sets_chart = charts.bar_chart(
            [(_short(k), v) for k, v in totals.items()], translate(g.lang, "progress.sets_aria"), " set",
        )

    best = {}
    for row in logs:
        if row["weight_kg"] > best.get(row["exercise_id"], 0):
            best[row["exercise_id"]] = row["weight_kg"]
    records = sorted(best.items(), key=lambda kv: kv[1], reverse=True)[:5]

    return render_template(
        "progress.html", weight_chart=weight_chart, sets_chart=sets_chart, records=records,
        weights=list(reversed(weights)), errors=errors or {},
        values=values or {"date": now.isoformat(), "weight_kg": ""},
    )


@app.get("/progress")
@profile_required
def progress():
    return render_progress()


@app.post("/weight")
@profile_required
def add_weight():
    data, errors = validators.validate_body_weight(request.form, today())
    if errors:
        notify("flash.form_errors", "error")
        return render_progress(errors, {"date": request.form.get("date", ""), "weight_kg": request.form.get("weight_kg", "")})
    repo.add_weight(g.user["id"], data["date"], data["weight_kg"])
    notify("flash.weight_saved", "success")
    return redirect(url_for("progress"))


@app.post("/weight/<log_id>/delete")
@login_required
def delete_weight(log_id):
    if not repo.delete_weight(g.user["id"], log_id):
        abort(404)
    notify("flash.weight_deleted", "info")
    return redirect(url_for("progress"))


if __name__ == "__main__":
    app.run(debug=True)
