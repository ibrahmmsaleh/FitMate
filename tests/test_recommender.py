import itertools

import pytest

import recommender as r


def profile(**kw):
    base = {"days": 3, "equipment": "bodyweight", "level": "beginner", "minutes": 45, "goal": "muscle"}
    return {**base, **kw}


def test_training_days_match_request(exercises):
    for days in range(2, 7):
        program = r.build_program(profile(days=days), exercises)
        assert len(program["days"]) == 7
        assert sum(1 for d in program["days"] if d["session"]) == days


def test_every_combination_builds_a_usable_program(exercises):
    combos = itertools.product(range(2, 7), r.EQUIPMENT_RANK, r.LEVEL_RANK, r.EXERCISES_PER_SESSION, ("lose_fat", "muscle", "strength", "fitness"))
    for days, equipment, level, minutes, goal in combos:
        program = r.build_program(
            {"days": days, "equipment": equipment, "level": level, "minutes": minutes, "goal": goal}, exercises
        )
        for day in program["days"]:
            if day["session"]:
                assert day["entries"], (days, equipment, level, minutes, goal, day["session"])
                assert len(day["entries"]) <= r.EXERCISES_PER_SESSION[minutes]


def test_only_allowed_equipment_and_level(exercises):
    for equipment, level in itertools.product(r.EQUIPMENT_RANK, r.LEVEL_RANK):
        program = r.build_program(profile(days=6, equipment=equipment, level=level, minutes=90), exercises)
        for day in program["days"]:
            for entry in day["entries"]:
                ex = entry["exercise"]
                assert r.EQUIPMENT_RANK[ex["equipment"]] <= r.EQUIPMENT_RANK[equipment]
                assert r.LEVEL_RANK[ex["level"]] <= r.LEVEL_RANK[level]


def test_no_duplicate_exercise_within_a_session(exercises):
    program = r.build_program(profile(days=6, equipment="gym", level="advanced", minutes=90), exercises)
    for day in program["days"]:
        ids = [e["exercise"]["id"] for e in day["entries"]]
        assert len(ids) == len(set(ids))


def test_same_input_gives_same_program(exercises):
    a = r.build_program(profile(days=4), exercises)
    b = r.build_program(profile(days=4), exercises)
    ids = lambda p: [[e["exercise"]["id"] for e in d["entries"]] for d in p["days"]]
    assert ids(a) == ids(b)


def test_core_is_last_and_best_equipment_is_preferred(exercises):
    program = r.build_program(profile(days=3, equipment="gym", level="beginner", minutes=60), exercises)
    day = next(d for d in program["days"] if d["session"])
    categories = [e["exercise"]["category"] for e in day["entries"]]
    assert "core" in categories and categories[-1] == "core"
    equipment_used = {e["exercise"]["equipment"] for e in day["entries"]}
    assert "gym" in equipment_used


def test_prescription_rules(exercises):
    by_id = {e["id"]: e for e in exercises}
    plank = r.prescribe(by_id["plank"], "muscle", "beginner")
    assert plank["unit"] == "sec" and plank["reps"] == r.SECONDS_BY_LEVEL["beginner"]
    squat_b = r.prescribe(by_id["back_squat"], "strength", "beginner")
    squat_i = r.prescribe(by_id["back_squat"], "strength", "intermediate")
    assert squat_b["reps"] == r.REPS_STRENGTH_BEGINNER
    assert squat_i["reps"] == r.REPS_COMPOUND["strength"]
    assert squat_i["rest"] > r.prescribe(by_id["back_squat"], "lose_fat", "intermediate")["rest"]
    curl = r.prescribe(by_id["db_curl"], "strength", "intermediate")
    assert curl["reps"] == r.REPS_ISOLATION["strength"]


def test_exercise_data_is_consistent(exercises):
    ids = [e["id"] for e in exercises]
    assert len(ids) == len(set(ids))
    for e in exercises:
        assert e["category"] in {"push", "pull", "legs", "core"}
        assert e["equipment"] in r.EQUIPMENT_RANK and e["level"] in r.LEVEL_RANK
        assert e["kind"] in {"compound", "isolation"}
        for field in ("name", "desc"):
            assert e[field]["id"].strip() and e[field]["en"].strip()
