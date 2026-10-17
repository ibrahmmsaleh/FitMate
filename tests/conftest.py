import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    """Setiap tes memakai folder data sendiri, jadi tidak saling mengganggu."""
    monkeypatch.setenv("FITMATE_DATA_DIR", str(tmp_path / "data"))


@pytest.fixture
def client():
    import app as app_module

    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.fixture
def exercises():
    import storage

    return storage.load_seed("exercises")


def csrf(client, path="/register"):
    """Ambil token CSRF dari sesi setelah membuka halaman berformulir."""
    client.get(path)
    with client.session_transaction() as sess:
        return sess["csrf"]


def register(client, email="rina@example.com", name="Rina", password="rahasia123"):
    token = csrf(client)
    return client.post(
        "/register",
        data={"csrf_token": token, "name": name, "email": email, "password": password, "password2": password},
    )


PROFILE = {
    "age": "22", "height_cm": "160", "weight_kg": "62,5", "goal": "lose_fat", "level": "beginner",
    "equipment": "bodyweight", "days": "3", "minutes": "30",
}


def save_profile(client, **overrides):
    token = csrf(client, "/profile")
    return client.post("/profile", data={"csrf_token": token, **PROFILE, **overrides})
