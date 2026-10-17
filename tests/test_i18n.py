import re
from pathlib import Path

import i18n
import storage

ROOT = Path(__file__).resolve().parent.parent


def test_every_key_has_both_languages():
    for key, pair in i18n.S.items():
        assert len(pair) == 2 and all(isinstance(p, str) and p.strip() for p in pair), key


def test_placeholders_match_between_languages():
    for key, (id_text, en_text) in i18n.S.items():
        assert set(re.findall(r"{(\w+)}", id_text)) == set(re.findall(r"{(\w+)}", en_text)), key


def test_all_literal_keys_used_in_code_exist():
    sources = [ROOT / "app.py", ROOT / "validators.py"] + list((ROOT / "templates").glob("*.html"))
    # Hanya kunci utuh: t('kunci') atau t('kunci', ...). Awalan dinamis seperti t('muscle.' ~ x) dites terpisah.
    pattern = re.compile(r"""(?:\bt|notify|translate)\(\s*(?:g\.lang,\s*)?['"]([a-z0-9_.]+)['"]\s*[,)]""")
    missing = set()
    for path in sources:
        for key in pattern.findall(path.read_text(encoding="utf-8")):
            if key not in i18n.S:
                missing.add((path.name, key))
    assert not missing, missing


def test_error_keys_from_validators_exist():
    text = (ROOT / "validators.py").read_text(encoding="utf-8")
    keys = set(re.findall(r'"(err\.[a-z_]+)"', text)) | {f"err.{f}" for f in ("age", "height_cm", "weight_kg", "days")}
    assert keys and all(k in i18n.S for k in keys), [k for k in keys if k not in i18n.S]


def test_dynamic_key_families_are_complete():
    exercises = storage.load_seed("exercises")
    needed = {f"muscle.{e['muscle']}" for e in exercises}
    needed |= {f"equip.{e['equipment']}" for e in exercises} | {f"level.{e['level']}" for e in exercises}
    needed |= {f"kind.{e['kind']}" for e in exercises}
    needed |= {f"weekday.{i}" for i in range(7)} | {f"weekday.short.{i}" for i in range(7)}
    needed |= {f"month.{i}" for i in range(1, 13)}
    needed |= {f"session.{s}" for s in ("full", "upper", "lower", "push", "pull", "legs", "rest")}
    needed |= {f"goal.{g}" for g in ("lose_fat", "muscle", "strength", "fitness")}
    assert all(k in i18n.S for k in needed), [k for k in needed if k not in i18n.S]


def test_translate_fallbacks():
    assert i18n.translate("en", "dash.hello", name="A") == "Hi, A"
    assert i18n.translate("id", "dash.hello", name="A") == "Halo, A"
    assert i18n.translate("id", "does.not.exist") == "does.not.exist"
