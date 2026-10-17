"""Penyimpanan data berbasis file JSON.

Setiap "koleksi" (users, profiles, ...) adalah satu file JSON.
Modul ini hanya mengurus baca/tulis file; aturan bisnis ada di repository.py.

PENTING untuk deployment Vercel:
- Filesystem proyek di Vercel bersifat read-only. Hanya /tmp yang bisa ditulis,
  dan isinya SEMENTARA (bisa hilang saat instance berganti / cold start).
- Karena itu data pengguna di Vercel TIDAK permanen. Cukup untuk demo tugas,
  tidak cukup untuk produksi. Lihat README.md bagian "Keterbatasan penyimpanan".
"""
import json
import os
import tempfile
import threading
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SEED_DIR = BASE_DIR / "data"  # data bawaan yang ikut di repo (hanya dibaca)

# Satu kunci untuk semua operasi baca-ubah-tulis dalam satu proses.
# Tidak melindungi dari banyak proses/instance sekaligus (batasan JSON).
lock = threading.RLock()


def data_dir() -> Path:
    """Folder untuk data pengguna. Dibaca ulang tiap pemanggilan agar mudah dites."""
    custom = os.environ.get("FITMATE_DATA_DIR")
    if custom:
        return Path(custom)
    if os.environ.get("VERCEL"):
        return Path("/tmp/fitmate_data")
    return SEED_DIR / "runtime"


def _path(name: str) -> Path:
    return data_dir() / f"{name}.json"


def load(name: str, default):
    """Baca koleksi. `default` dipakai bila file belum ada."""
    with lock:
        path = _path(name)
        if not path.exists():
            return default
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # File rusak: simpan salinan agar tidak hilang, lalu mulai bersih.
            path.replace(path.with_suffix(".json.corrupt"))
            return default


def save(name: str, data) -> None:
    """Tulis koleksi secara atomik (tulis ke file sementara, lalu ganti)."""
    with lock:
        folder = data_dir()
        folder.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=folder, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_name, _path(name))
        except BaseException:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
            raise


def load_seed(name: str):
    """Baca data bawaan (mis. exercises.json) dari folder data/."""
    with open(SEED_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def new_id() -> str:
    return uuid.uuid4().hex[:12]
