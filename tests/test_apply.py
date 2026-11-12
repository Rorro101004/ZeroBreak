"""Tests de la aplicación con rollback automático."""

from pathlib import Path

from zerobreak import apply as apply_mod
from zerobreak import cases, runner
from zerobreak import state as state_mod

GOOD = "class Calc:\n    def add(self, a: int, b: int) -> int:\n        return a + b\n"
BAD = "class Calc:\n    def add(self, a, b):\n        return a - b\n"
BROKEN_CONTRACT = "class Calc:\n    def add(self, x, y):\n        return x + y\n"


def _source(project: Path, body: str) -> Path:
    path = project / "proposed.py"
    path.write_text(body, encoding="utf-8")
    return path


def _baseline(project: Path):
    case = cases.resolve_case(project, "sample")
    state_mod.record_baseline(project, case.name, case.modules)
    return case


def test_plan_requires_baseline(project):
    case = cases.resolve_case(project, "sample")
    result = apply_mod.plan_apply(
        project, case, case.path / "calc.py", _source(project, GOOD)
    )
    assert result.ok is False
    assert "baseline" in result.message.lower()


def test_plan_missing_source(project):
    case = cases.resolve_case(project, "sample")
    result = apply_mod.plan_apply(
        project, case, case.path / "calc.py", project / "no_existe.py"
    )
    assert result.ok is False
    assert "no existe" in result.message.lower()


def test_plan_hash_mismatch(project):
    case = _baseline(project)
    (case.path / "calc.py").write_text("# tocado a mano\n", encoding="utf-8")
    result = apply_mod.plan_apply(
        project, case, case.path / "calc.py", _source(project, GOOD)
    )
    assert result.ok is False
    assert "cambi" in result.message.lower()


def test_plan_contract_violation_blocks_without_writing(project):
    case = _baseline(project)
    original = (case.path / "calc.py").read_text(encoding="utf-8")
    result = apply_mod.plan_apply(
        project, case, case.path / "calc.py", _source(project, BROKEN_CONTRACT)
    )
    assert result.ok is False
    assert "contrato" in result.message.lower()
    assert result.diff != ""
    assert (case.path / "calc.py").read_text(encoding="utf-8") == original


def test_apply_success_writes_backup_and_records(project):
    case = _baseline(project)
    result = apply_mod.apply(
        project, case, case.path / "calc.py", _source(project, GOOD)
    )
    assert result.ok is True
    assert "int" in (case.path / "calc.py").read_text(encoding="utf-8")
    assert not (case.path / ".calc.py.tmp").exists()
    assert (case.path / "calc_legacy_anotado.py").is_file()
    assert state_mod.get_entry(project, "sample")["baseline_ok"] is True


def test_apply_rolls_back_on_red(project, monkeypatch):
    case = _baseline(project)
    original = (case.path / "calc.py").read_text(encoding="utf-8")
    monkeypatch.setattr(
        runner, "run_pytest", lambda root, target: runner.RunResult(1, "1 failed")
    )
    result = apply_mod.apply(
        project, case, case.path / "calc.py", _source(project, BAD)
    )
    assert result.ok is False
    assert (case.path / "calc.py").read_text(encoding="utf-8") == original


def test_apply_returns_plan_failure_without_writing(project):
    """Si el plan no es válido, apply() delega el fallo y no escribe en disco."""
    case = cases.resolve_case(project, "sample")
    original = (case.path / "calc.py").read_text(encoding="utf-8")
    result = apply_mod.apply(
        project, case, case.path / "calc.py", _source(project, GOOD)
    )
    assert result.ok is False
    assert "baseline" in result.message.lower()
    assert (case.path / "calc.py").read_text(encoding="utf-8") == original
