"""Fungsi data tingkat aplikasi: pengguna, profil, catatan latihan, catatan berat.

Semua fungsi memakai storage.py. Satu pengguna hanya bisa menyentuh datanya
sendiri: setiap fungsi yang mengubah/menghapus catatan menerima user_id.
"""
from datetime import datetime, timezone

import storage


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------- Pengguna ----------
def get_user(user_id):
    for user in storage.load("users", []):
        if user["id"] == user_id:
            return user
    return None


def get_user_by_email(email):
    email = email.strip().lower()
    for user in storage.load("users", []):
        if user["email"] == email:
            return user
    return None


def create_user(name, email, password_hash):
    """Buat pengguna. Mengembalikan None bila email sudah terpakai."""
    with storage.lock:
        users = storage.load("users", [])
        email = email.strip().lower()
        if any(u["email"] == email for u in users):
            return None
        user = {
            "id": storage.new_id(),
            "name": name.strip(),
            "email": email,
            "password_hash": password_hash,
            "created_at": _now(),
        }
        users.append(user)
        storage.save("users", users)
        return user


def delete_user_and_data(user_id):
    """Hapus akun beserta profil dan semua catatan (hak hapus data)."""
    with storage.lock:
        storage.save("users", [u for u in storage.load("users", []) if u["id"] != user_id])
        profiles = storage.load("profiles", {})
        profiles.pop(user_id, None)
        storage.save("profiles", profiles)
        for name in ("workout_logs", "weight_logs"):
            storage.save(name, [r for r in storage.load(name, []) if r["user_id"] != user_id])


# ---------- Profil ----------
def get_profile(user_id):
    return storage.load("profiles", {}).get(user_id)


def save_profile(user_id, profile):
    with storage.lock:
        profiles = storage.load("profiles", {})
        profiles[user_id] = profile
        storage.save("profiles", profiles)


# ---------- Catatan latihan ----------
def list_workouts(user_id):
    """Terbaru dulu."""
    rows = [r for r in storage.load("workout_logs", []) if r["user_id"] == user_id]
    return sorted(rows, key=lambda r: (r["date"], r["created_at"]), reverse=True)


def get_workout(user_id, log_id):
    for row in storage.load("workout_logs", []):
        if row["id"] == log_id and row["user_id"] == user_id:
            return row
    return None


def add_workout(user_id, data):
    with storage.lock:
        rows = storage.load("workout_logs", [])
        row = {"id": storage.new_id(), "user_id": user_id, "created_at": _now(), **data}
        rows.append(row)
        storage.save("workout_logs", rows)
        return row


def update_workout(user_id, log_id, data):
    with storage.lock:
        rows = storage.load("workout_logs", [])
        for row in rows:
            if row["id"] == log_id and row["user_id"] == user_id:
                row.update(data)
                storage.save("workout_logs", rows)
                return row
    return None


def delete_workout(user_id, log_id):
    with storage.lock:
        rows = storage.load("workout_logs", [])
        kept = [r for r in rows if not (r["id"] == log_id and r["user_id"] == user_id)]
        if len(kept) == len(rows):
            return False
        storage.save("workout_logs", kept)
        return True


# ---------- Catatan berat badan ----------
def list_weights(user_id):
    """Terlama dulu (cocok untuk grafik)."""
    rows = [r for r in storage.load("weight_logs", []) if r["user_id"] == user_id]
    return sorted(rows, key=lambda r: (r["date"], r["created_at"]))


def add_weight(user_id, date_iso, weight_kg):
    """Satu entri per tanggal: menulis ulang tanggal yang sama akan mengganti nilainya."""
    with storage.lock:
        rows = storage.load("weight_logs", [])
        for row in rows:
            if row["user_id"] == user_id and row["date"] == date_iso:
                row["weight_kg"] = weight_kg
                storage.save("weight_logs", rows)
                return row
        row = {
            "id": storage.new_id(),
            "user_id": user_id,
            "date": date_iso,
            "weight_kg": weight_kg,
            "created_at": _now(),
        }
        rows.append(row)
        storage.save("weight_logs", rows)
        return row


def delete_weight(user_id, log_id):
    with storage.lock:
        rows = storage.load("weight_logs", [])
        kept = [r for r in rows if not (r["id"] == log_id and r["user_id"] == user_id)]
        if len(kept) == len(rows):
            return False
        storage.save("weight_logs", kept)
        return True
