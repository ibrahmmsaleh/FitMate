"""Validasi input formulir. Setiap fungsi mengembalikan (data_bersih, errors).

`errors` berisi {nama_field: kunci_terjemahan}. Teks pesan dibuat di template
lewat t(kunci), sehingga otomatis mengikuti bahasa yang dipilih.
"""
import re
from datetime import date

from recommender import EQUIPMENT_RANK, EXERCISES_PER_SESSION, LEVEL_RANK

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
GOALS = ("lose_fat", "muscle", "strength", "fitness")


def _number(raw, low, high, integer=False):
    """Ubah teks jadi angka. Menerima koma desimal ("62,5"). Mengembalikan None bila tidak valid."""
    text = (raw or "").strip().replace(",", ".")
    try:
        value = int(text) if integer else float(text)
    except ValueError:
        return None
    if value != value or not (low <= value <= high):  # value != value -> NaN
        return None
    return value if integer else round(value, 1)


def validate_register(form):
    data = {
        "name": (form.get("name") or "").strip(),
        "email": (form.get("email") or "").strip().lower(),
        "password": form.get("password") or "",
    }
    errors = {}
    if not 1 <= len(data["name"]) <= 60:
        errors["name"] = "err.name"
    if len(data["email"]) > 120 or not EMAIL_RE.match(data["email"]):
        errors["email"] = "err.email"
    if len(data["password"]) < 8 or len(data["password"]) > 128:
        errors["password"] = "err.password_length"
    elif data["password"] != (form.get("password2") or ""):
        errors["password2"] = "err.password_match"
    return data, errors


def validate_profile(form):
    errors = {}
    data = {
        "age": _number(form.get("age"), 15, 80, integer=True),
        "height_cm": _number(form.get("height_cm"), 120, 230),
        "weight_kg": _number(form.get("weight_kg"), 30, 250),
        "goal": form.get("goal"),
        "level": form.get("level"),
        "days": _number(form.get("days"), 2, 6, integer=True),
        "equipment": form.get("equipment"),
        "minutes": _number(form.get("minutes"), 1, 1000, integer=True),
        "has_condition": form.get("has_condition") == "on",
    }
    for field in ("age", "height_cm", "weight_kg", "days"):
        if data[field] is None:
            errors[field] = f"err.{field}"
    if data["goal"] not in GOALS:
        errors["goal"] = "err.choice"
    if data["level"] not in LEVEL_RANK:
        errors["level"] = "err.choice"
    if data["equipment"] not in EQUIPMENT_RANK:
        errors["equipment"] = "err.choice"
    if data["minutes"] not in EXERCISES_PER_SESSION:
        errors["minutes"] = "err.choice"
    return data, errors


def validate_workout(form, exercise_ids, today):
    errors = {}
    try:
        day = date.fromisoformat((form.get("date") or "").strip())
    except ValueError:
        day = None
    if day is None or day > today:
        errors["date"] = "err.date"
    exercise_id = form.get("exercise_id")
    if exercise_id not in exercise_ids:
        errors["exercise_id"] = "err.choice"
    sets = _number(form.get("sets"), 1, 20, integer=True)
    reps = _number(form.get("reps"), 1, 600, integer=True)
    weight = _number(form.get("weight_kg") or "0", 0, 500)
    if sets is None:
        errors["sets"] = "err.sets"
    if reps is None:
        errors["reps"] = "err.reps"
    if weight is None:
        errors["weight_kg"] = "err.weight_load"
    note = (form.get("note") or "").strip()
    if len(note) > 200:
        errors["note"] = "err.note"
    data = {
        "date": day.isoformat() if day else None,
        "exercise_id": exercise_id,
        "sets": sets,
        "reps": reps,
        "weight_kg": weight,
        "note": note,
    }
    return data, errors


def validate_body_weight(form, today):
    errors = {}
    try:
        day = date.fromisoformat((form.get("date") or "").strip())
    except ValueError:
        day = None
    if day is None or day > today:
        errors["date"] = "err.date"
    weight = _number(form.get("weight_kg"), 30, 250)
    if weight is None:
        errors["weight_kg"] = "err.weight_kg"
    return {"date": day.isoformat() if day else None, "weight_kg": weight}, errors
