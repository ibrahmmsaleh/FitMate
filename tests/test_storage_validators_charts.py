from datetime import date

import charts
import storage
import validators


def test_storage_roundtrip_and_default():
    assert storage.load("things", []) == []
    storage.save("things", [{"a": 1, "teks": "Ünïcode"}])
    assert storage.load("things", []) == [{"a": 1, "teks": "Ünïcode"}]


def test_storage_keeps_corrupt_file_and_starts_clean():
    storage.save("things", [1])
    (storage.data_dir() / "things.json").write_text("{rusak", encoding="utf-8")
    assert storage.load("things", []) == []
    assert (storage.data_dir() / "things.json.corrupt").exists()


def test_vercel_uses_tmp(monkeypatch):
    monkeypatch.delenv("FITMATE_DATA_DIR")
    monkeypatch.setenv("VERCEL", "1")
    assert str(storage.data_dir()) == "/tmp/fitmate_data"


def test_profile_validation_accepts_decimal_comma():
    data, errors = validators.validate_profile({
        "age": "22", "height_cm": "160", "weight_kg": "62,5", "goal": "muscle", "level": "beginner",
        "days": "3", "equipment": "gym", "minutes": "45",
    })
    assert not errors and data["weight_kg"] == 62.5


def test_profile_validation_rejects_bad_values():
    _, errors = validators.validate_profile({
        "age": "5", "height_cm": "abc", "weight_kg": "nan", "goal": "x", "level": "", "days": "9",
        "equipment": "robot", "minutes": "20",
    })
    assert set(errors) == {"age", "height_cm", "weight_kg", "goal", "level", "days", "equipment", "minutes"}


def test_register_validation():
    _, errors = validators.validate_register({"name": "", "email": "bukan-email", "password": "pendek", "password2": "pendek"})
    assert set(errors) == {"name", "email", "password"}
    _, errors = validators.validate_register({"name": "A", "email": "a@b.co", "password": "panjang123", "password2": "beda12345"})
    assert errors == {"password2": "err.password_match"}


def test_workout_validation_rejects_future_date_and_unknown_exercise():
    form = {"date": "2030-01-01", "exercise_id": "nope", "sets": "3", "reps": "10", "weight_kg": "0"}
    _, errors = validators.validate_workout(form, {"plank": {}}, date(2026, 10, 11))
    assert set(errors) == {"date", "exercise_id"}


def test_chart_escapes_labels_and_handles_flat_data():
    svg = str(charts.line_chart([("<b>x</b>", 60), ("y", 60)], "aria", " kg"))
    assert "<b>" not in svg and "&lt;b&gt;" in svg
    assert "<svg" in str(charts.bar_chart([("a", 0), ("b", 0)], "aria"))
    assert str(charts.line_chart([], "aria")) == ""


def test_chart_axes_use_round_numbers():
    import re

    svg = str(charts.bar_chart([("a", 9), ("b", 9), ("c", 0)], "x"))
    assert re.findall(r'text-anchor="end">([^<]+)<', svg) == ["0", "5", "10"]
    svg = str(charts.line_chart([("a", 62.5), ("b", 60.9)], "x"))
    labels = [float(v) for v in re.findall(r'text-anchor="end">([\d.]+)<', svg)]
    assert labels == sorted(labels) and labels[0] <= 60.9 and labels[-1] >= 62.5
