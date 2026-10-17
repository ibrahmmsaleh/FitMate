import re
from datetime import timedelta

import app as app_module
import repository as repo
from conftest import PROFILE, csrf, register, save_profile


def test_home_page_is_public_and_shows_sample_week(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "FitMate" in html and 'class="week"' in html


def test_protected_pages_redirect_to_login(client):
    for path in ("/dashboard", "/program", "/exercises", "/log", "/progress", "/profile"):
        r = client.get(path)
        assert r.status_code == 302 and "/login" in r.headers["Location"], path


def test_post_without_csrf_token_is_rejected(client):
    r = client.post("/register", data={"name": "A", "email": "a@b.co", "password": "panjang123", "password2": "panjang123"})
    assert r.status_code == 400


def test_register_hashes_password_and_rejects_duplicate_email(client):
    r = register(client)
    assert r.status_code == 302 and r.headers["Location"].endswith("/profile")
    user = repo.get_user_by_email("rina@example.com")
    assert user["password_hash"] != "rahasia123" and user["password_hash"].startswith("pbkdf2:")
    other = client.application.test_client()
    r2 = register(other)
    assert r2.status_code == 200 and "sudah terdaftar" in r2.get_data(as_text=True)


def test_login_logout_and_wrong_password(client):
    register(client)
    token = csrf(client, "/profile")
    client.post("/logout", data={"csrf_token": token})
    assert client.get("/dashboard").status_code == 302
    token = csrf(client, "/login")
    bad = client.post("/login", data={"csrf_token": token, "email": "rina@example.com", "password": "salah-salah"})
    assert bad.status_code == 200 and "salah" in bad.get_data(as_text=True)
    ok = client.post("/login", data={"csrf_token": token, "email": "rina@example.com", "password": "rahasia123"})
    assert ok.status_code == 302 and ok.headers["Location"].endswith("/profile")


def test_login_next_blocks_open_redirect(client):
    register(client)
    token = csrf(client, "/profile")
    client.post("/logout", data={"csrf_token": token})
    token = csrf(client, "/login")
    for evil in ("https://evil.example", "//evil.example", "/\\evil.example"):
        r = client.post("/login", data={"csrf_token": token, "email": "rina@example.com", "password": "rahasia123", "next": evil})
        assert "evil" not in r.headers["Location"]
        token = csrf(client, "/profile")
        client.post("/logout", data={"csrf_token": token})
        token = csrf(client, "/login")


def test_full_flow_profile_program_log_progress(client):
    register(client)
    r = save_profile(client)
    assert r.status_code == 302 and r.headers["Location"].endswith("/program")

    program = client.get("/program").get_data(as_text=True)
    assert "FitMate memberi saran umum" in program and 'id="day-0"' in program

    # profil menyimpan berat awal sebagai catatan berat pertama
    user = repo.get_user_by_email("rina@example.com")
    assert [w["weight_kg"] for w in repo.list_weights(user["id"])] == [62.5]

    token = csrf(client, "/log")
    today = app_module.today().isoformat()
    r = client.post("/log", data={"csrf_token": token, "date": today, "exercise_id": "plank", "sets": "3", "reps": "40", "weight_kg": "0"})
    assert r.status_code == 302
    r = client.post("/log", data={"csrf_token": token, "date": today, "exercise_id": "goblet_squat", "sets": "3", "reps": "10", "weight_kg": "12,5"})
    assert r.status_code == 302
    page = client.get("/log").get_data(as_text=True)
    assert "Plank" in page and "12.5 kg" in page

    progress = client.get("/progress").get_data(as_text=True)
    assert "<svg" in progress and "Goblet squat" in progress and "12.5 kg" in progress

    dash = client.get("/dashboard").get_data(as_text=True)
    assert "Halo, Rina" in dash and "1/3" in dash


def test_invalid_log_keeps_input_and_shows_errors(client):
    register(client)
    save_profile(client)
    token = csrf(client, "/log")
    r = client.post("/log", data={"csrf_token": token, "date": "2999-01-01", "exercise_id": "plank", "sets": "0", "reps": "10", "weight_kg": "0"})
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "Set harus 1–20" in html and "di masa depan" in html


def test_edit_and_delete_log(client):
    register(client)
    save_profile(client)
    token = csrf(client, "/log")
    today = app_module.today().isoformat()
    client.post("/log", data={"csrf_token": token, "date": today, "exercise_id": "plank", "sets": "3", "reps": "30", "weight_kg": "0"})
    user = repo.get_user_by_email("rina@example.com")
    log_id = repo.list_workouts(user["id"])[0]["id"]
    r = client.post(f"/log/{log_id}/edit", data={"csrf_token": token, "date": today, "exercise_id": "plank", "sets": "4", "reps": "45", "weight_kg": "0"})
    assert r.status_code == 302 and repo.get_workout(user["id"], log_id)["reps"] == 45
    assert client.post(f"/log/{log_id}/delete", data={"csrf_token": token}).status_code == 302
    assert repo.list_workouts(user["id"]) == []


def test_users_cannot_touch_each_others_logs(client):
    register(client)
    save_profile(client)
    token = csrf(client, "/log")
    client.post("/log", data={"csrf_token": token, "date": app_module.today().isoformat(), "exercise_id": "plank", "sets": "3", "reps": "30", "weight_kg": "0"})
    rina = repo.get_user_by_email("rina@example.com")
    log_id = repo.list_workouts(rina["id"])[0]["id"]

    intruder = client.application.test_client()
    register(intruder, email="dimas@example.com", name="Dimas")
    token = csrf(intruder, "/profile")
    assert intruder.get(f"/log/{log_id}/edit").status_code == 404
    assert intruder.post(f"/log/{log_id}/delete", data={"csrf_token": token}).status_code == 404
    assert repo.get_workout(rina["id"], log_id) is not None


def test_weight_logging_replaces_same_day_and_validates(client):
    register(client)
    save_profile(client)
    token = csrf(client, "/progress")
    today = app_module.today().isoformat()
    client.post("/weight", data={"csrf_token": token, "date": today, "weight_kg": "61,8"})
    user = repo.get_user_by_email("rina@example.com")
    assert [w["weight_kg"] for w in repo.list_weights(user["id"])] == [61.8]
    bad = client.post("/weight", data={"csrf_token": token, "date": today, "weight_kg": "5"})
    assert bad.status_code == 200 and "Berat harus 30–250 kg" in bad.get_data(as_text=True)


def test_language_switch_changes_interface_and_exercise_names(client):
    register(client)
    save_profile(client)
    client.get("/lang/en", headers={"Referer": "http://localhost/program"})
    html = client.get("/program").get_data(as_text=True)
    assert "Weekly program" in html and "Rest" in html and "Program mingguan" not in html
    detail = client.get("/exercises/wall_push_up").get_data(as_text=True)
    assert "Wall push-up" in detail and "Stand facing a wall" in detail
    client.get("/lang/id")
    assert "Push-up di dinding" in client.get("/exercises/wall_push_up").get_data(as_text=True)


def test_language_switch_ignores_foreign_referrer(client):
    r = client.get("/lang/en", headers={"Referer": "https://evil.example/path"})
    assert r.headers["Location"].endswith("/") and "evil" not in r.headers["Location"]


def test_exercise_filters(client):
    register(client)
    html = client.get("/exercises?equipment=gym&muscle=chest").get_data(as_text=True)
    assert "Bench press barbel" in html and "Push-up lutut" not in html
    assert "Tidak ada latihan" in client.get("/exercises?q=zzzzz").get_data(as_text=True)
    assert client.get("/exercises/tidak-ada").status_code == 404


def test_condition_flag_shows_doctor_warning(client):
    register(client)
    save_profile(client, has_condition="on")
    assert "Periksakan program ini ke dokter" in client.get("/program").get_data(as_text=True)


def test_invalid_profile_is_rejected_without_saving(client):
    register(client)
    r = save_profile(client, age="3", days="9")
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "Usia harus 15–80" in html and "Pilih 2–6 hari" in html
    user = repo.get_user_by_email("rina@example.com")
    assert repo.get_profile(user["id"]) is None


def test_delete_account_removes_everything(client):
    register(client)
    save_profile(client)
    token = csrf(client, "/log")
    client.post("/log", data={"csrf_token": token, "date": app_module.today().isoformat(), "exercise_id": "plank", "sets": "3", "reps": "30", "weight_kg": "0"})
    user = repo.get_user_by_email("rina@example.com")
    assert client.post("/account/delete", data={"csrf_token": token}).status_code == 302
    assert repo.get_user(user["id"]) is None
    assert repo.get_profile(user["id"]) is None
    assert repo.list_workouts(user["id"]) == [] and repo.list_weights(user["id"]) == []


def test_session_for_missing_user_is_cleared(client):
    register(client)
    user = repo.get_user_by_email("rina@example.com")
    repo.delete_user_and_data(user["id"])   # mensimulasikan data /tmp Vercel yang hilang
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/login" in r.headers["Location"]
    assert "Sesi Anda berakhir" in client.get("/login").get_data(as_text=True)


def test_today_uses_configured_offset(monkeypatch):
    monkeypatch.setenv("FITMATE_UTC_OFFSET", "7")
    a = app_module.today()
    monkeypatch.setenv("FITMATE_UTC_OFFSET", "-12")
    b = app_module.today()
    assert abs((a - b).days) <= 1


def test_security_headers_and_404(client):
    r = client.get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff" and r.headers["X-Frame-Options"] == "DENY"
    assert client.get("/halaman-hilang").status_code == 404


def test_stylesheet_served_locally(client):
    r = client.get("/style.css")
    assert r.status_code == 200 and b"--cobalt" in r.data
