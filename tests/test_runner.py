"""Tests unitarios de ``zerobreak.runner`` (ejecución de pytest por subproceso)."""

import pytest

from zerobreak import runner


@pytest.fixture(autouse=True)
def _clean_coverage_env(monkeypatch):
    """Evita que los subprocesos hereden el arranque de coverage del proceso padre."""
    for var in (
        "COV_CORE_SOURCE",
        "COV_CORE_CONFIG",
        "COV_CORE_DATAFILE",
        "COV_CORE_DEBUG",
        "COVERAGE_PROCESS_START",
    ):
        monkeypatch.delenv(var, raising=False)


def _make_project(tmp_path, ok: bool):
    (tmp_path / "sample.py").write_text(
        "def add(a, b):\n    return a + b\n", encoding="utf-8"
    )
    resultado = "5" if ok else "6"
    (tmp_path / "test_sample.py").write_text(
        "from sample import add\n\n\ndef test_add():\n"
        f"    assert add(2, 3) == {resultado}\n",
        encoding="utf-8",
    )
    return tmp_path


def test_run_pytest_ok(tmp_path):
    root = _make_project(tmp_path, ok=True)
    result = runner.run_pytest(root, root / "test_sample.py")
    assert result.ok is True
    assert result.returncode == 0
    assert "passed" in result.output


def test_run_pytest_failure(tmp_path):
    root = _make_project(tmp_path, ok=False)
    result = runner.run_pytest(root, root / "test_sample.py")
    assert result.ok is False
    assert result.returncode != 0
    assert "failed" in result.output


def test_run_result_ok_property():
    assert runner.RunResult(0, "").ok is True
    assert runner.RunResult(1, "boom").ok is False
