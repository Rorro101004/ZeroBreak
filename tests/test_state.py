"""Tests unitarios de ``zerobreak.state``."""

import hashlib
import json

from zerobreak import state


def test_state_path(tmp_path):
    assert state.state_path(tmp_path) == tmp_path / ".zerobreak" / "state.json"


def test_sha256_file_matches_hashlib(tmp_path):
    file = tmp_path / "data.txt"
    file.write_bytes(b"contenido de prueba")
    expected = hashlib.sha256(b"contenido de prueba").hexdigest()
    assert state.sha256_file(file) == expected


def test_sha256_file_detects_single_byte_change(tmp_path):
    file = tmp_path / "data.bin"
    file.write_bytes(b"A")
    first = state.sha256_file(file)
    file.write_bytes(b"B")
    assert state.sha256_file(file) != first


def test_load_state_returns_skeleton_when_missing(tmp_path):
    assert state.load_state(tmp_path) == {"cases": {}}


def test_save_and_load_state_roundtrip(tmp_path):
    state.save_state(tmp_path, {"cases": {"sample": {"baseline_ok": True}}})
    assert state.load_state(tmp_path) == {"cases": {"sample": {"baseline_ok": True}}}


def test_get_entry_returns_none_when_absent(tmp_path):
    assert state.get_entry(tmp_path, "sample") is None


def test_record_baseline_sets_green_and_hashes(tmp_path):
    module = tmp_path / "calc.py"
    module.write_text("x = 1\n", encoding="utf-8")
    state.record_baseline(tmp_path, "sample", [module])
    entry = state.get_entry(tmp_path, "sample")
    assert entry["baseline_ok"] is True
    assert entry["updated"]
    assert entry["modules"] == {"calc.py": state.sha256_file(module)}


def test_record_baseline_persists_json(tmp_path):
    module = tmp_path / "calc.py"
    module.write_text("x = 1\n", encoding="utf-8")
    state.record_baseline(tmp_path, "sample", [module])
    raw = json.loads(state.state_path(tmp_path).read_text(encoding="utf-8"))
    assert raw["cases"]["sample"]["baseline_ok"] is True
