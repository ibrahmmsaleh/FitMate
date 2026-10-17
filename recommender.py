"""Rekomendasi program latihan berbasis aturan (tanpa AI).

Alur:
 1. Jumlah hari latihan -> pola split (full body / upper-lower / push-pull-legs).
 2. Tiap sesi punya "slot" kelompok gerak (push, pull, legs, core).
 3. Slot diisi latihan yang cocok dengan alat dan level pengguna.
 4. Set, repetisi, dan istirahat ditentukan dari tujuan dan level.

Semua angka ada di konstanta di bawah supaya mudah dibaca dan diubah.
Angka-angka ini adalah PRAKTIK UMUM, belum diverifikasi ke sumber kepelatihan
atau ahli. Tinjau sebelum dipakai di luar tugas.
"""

LEVEL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}

# Alat bersifat bertingkat: gym mencakup dumbbell, dumbbell mencakup tanpa alat.
EQUIPMENT_RANK = {"bodyweight": 0, "dumbbell": 1, "gym": 2}

# Jumlah hari -> urutan jenis sesi dalam seminggu.
SPLITS = {
    2: ["full", "full"],
    3: ["full", "full", "full"],
    4: ["upper", "lower", "upper", "lower"],
    5: ["push", "pull", "legs", "upper", "lower"],
    6: ["push", "pull", "legs", "push", "pull", "legs"],
}

# Jumlah hari -> hari dalam minggu (0 = Senin). Disebar agar ada hari istirahat.
WEEKDAYS = {
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 4, 5],
    6: [0, 1, 2, 3, 4, 5],
}

# Slot per jenis sesi (7 slot; dipotong sesuai durasi sesi).
SLOTS = {
    "full": ["legs", "push", "pull", "core", "legs", "push", "pull"],
    "upper": ["push", "pull", "push", "pull", "push", "pull", "core"],
    "lower": ["legs", "legs", "legs", "legs", "core", "legs", "legs"],
    "push": ["push", "push", "push", "push", "push", "core", "push"],
    "pull": ["pull", "pull", "pull", "pull", "pull", "core", "pull"],
    "legs": ["legs", "legs", "legs", "legs", "legs", "core", "legs"],
}

# Durasi sesi (menit) -> jumlah latihan.
EXERCISES_PER_SESSION = {30: 4, 45: 5, 60: 6, 90: 7}

# Repetisi: (jenis latihan, tujuan) -> rentang. Pemula yang memilih "strength" lebih konservatif.
REPS_COMPOUND = {"strength": "4–6", "muscle": "8–12", "lose_fat": "12–15", "fitness": "10–12"}
REPS_ISOLATION = {"strength": "8–12", "muscle": "10–15", "lose_fat": "12–15", "fitness": "12–15"}
REPS_STRENGTH_BEGINNER = "6–8"
REPS_CORE = "12–15"
SECONDS_BY_LEVEL = {"beginner": "20–30", "intermediate": "30–45", "advanced": "45–60"}

REST_COMPOUND = {"strength": 150, "muscle": 90, "lose_fat": 45, "fitness": 60}
REST_ISOLATION = {"strength": 60, "muscle": 60, "lose_fat": 45, "fitness": 45}

SETS_COMPOUND = {"beginner": 3, "intermediate": 3, "advanced": 4}
SETS_OTHER = {"beginner": 2, "intermediate": 3, "advanced": 3}


def allowed_exercises(exercises, equipment, level):
    """Latihan yang boleh dipakai pengguna dengan alat dan level tersebut."""
    max_eq = EQUIPMENT_RANK[equipment]
    max_level = LEVEL_RANK[level]
    return [
        ex for ex in exercises
        if EQUIPMENT_RANK[ex["equipment"]] <= max_eq and LEVEL_RANK[ex["level"]] <= max_level
    ]


def prescribe(ex, goal, level):
    """Set, repetisi (atau detik), dan istirahat untuk satu latihan."""
    if ex["timed"]:
        return {"sets": SETS_OTHER[level], "reps": SECONDS_BY_LEVEL[level], "unit": "sec", "rest": 45}
    if ex["category"] == "core":
        return {"sets": SETS_OTHER[level], "reps": REPS_CORE, "unit": "reps", "rest": 45}
    if ex["kind"] == "compound":
        reps = REPS_COMPOUND[goal]
        if goal == "strength" and level == "beginner":
            reps = REPS_STRENGTH_BEGINNER
        return {"sets": SETS_COMPOUND[level], "reps": reps, "unit": "reps", "rest": REST_COMPOUND[goal]}
    return {"sets": SETS_OTHER[level], "reps": REPS_ISOLATION[goal], "unit": "reps", "rest": REST_ISOLATION[goal]}


def _pick(candidates, session_muscles, usage):
    """Pilih satu latihan. Urutan prioritas (yang lebih atas lebih penting):
      1. otot yang belum dipakai di sesi ini (agar sesi seimbang),
      2. alat paling lengkap yang dimiliki pengguna (mesin > dumbbell > tanpa alat),
      3. latihan yang belum sering dipakai minggu ini (variasi),
      4. level tertinggi yang masih diizinkan,
      5. id (supaya hasil selalu sama untuk input yang sama).
    """
    return min(
        candidates,
        key=lambda ex: (
            session_muscles.count(ex["muscle"]),
            -EQUIPMENT_RANK[ex["equipment"]],
            usage.get(ex["id"], 0),
            -LEVEL_RANK[ex["level"]],
            ex["id"],
        ),
    )


def build_program(profile, exercises):
    """Susun program mingguan.

    Mengembalikan {"days": [7 hari]}; tiap hari berisi:
      index (0=Senin), session (None bila istirahat), entries (daftar latihan).
    """
    days_per_week = profile["days"]
    pool = allowed_exercises(exercises, profile["equipment"], profile["level"])
    per_session = EXERCISES_PER_SESSION[profile["minutes"]]
    usage = {}

    sessions_by_weekday = {}
    for weekday, session_type in zip(WEEKDAYS[days_per_week], SPLITS[days_per_week]):
        chosen = []
        muscles = []
        for slot in SLOTS[session_type]:
            if len(chosen) >= per_session:
                break
            candidates = [ex for ex in pool if ex["category"] == slot and ex not in chosen]
            if not candidates:
                continue  # slot tidak bisa diisi dengan alat/level ini, lewati
            ex = _pick(candidates, muscles, usage)
            chosen.append(ex)
            muscles.append(ex["muscle"])
            usage[ex["id"]] = usage.get(ex["id"], 0) + 1
        # Urutan: gerakan majemuk dulu, isolasi kemudian, core terakhir.
        chosen.sort(key=lambda ex: (ex["category"] == "core", ex["kind"] == "isolation"))
        entries = [{"exercise": ex, **prescribe(ex, profile["goal"], profile["level"])} for ex in chosen]
        sessions_by_weekday[weekday] = {"session": session_type, "entries": entries}

    days = []
    for index in range(7):
        entry = sessions_by_weekday.get(index, {"session": None, "entries": []})
        days.append({"index": index, **entry})
    return {"days": days}
