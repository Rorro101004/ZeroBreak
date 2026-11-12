"""Tests unitarios de ``zerobreak.lint``."""

import subprocess

from zerobreak import lint


def _completed(returncode: int, stdout: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=""
    )


def test_run_linters_reports_missing_tools(monkeypatch):
    monkeypatch.setattr(lint, "_is_available", lambda tool: False)
    report = lint.run_linters("x.py")
    assert report.ran == ()
    assert report.missing == ("ruff", "mypy")
    assert report.ok is True


def test_run_linters_clean(monkeypatch):
    monkeypatch.setattr(lint, "_is_available", lambda tool: True)
    monkeypatch.setattr(lint.subprocess, "run", lambda *args, **kwargs: _completed(0))
    report = lint.run_linters("x.py")
    assert report.ran == ("ruff", "mypy")
    assert report.ok is True


def test_run_linters_reports_findings(monkeypatch):
    monkeypatch.setattr(lint, "_is_available", lambda tool: True)
    monkeypatch.setattr(
        lint.subprocess, "run", lambda *args, **kwargs: _completed(1, "F401 boom")
    )
    report = lint.run_linters("x.py")
    assert report.ran == ("ruff", "mypy")
    assert report.ok is False
    assert {finding.tool for finding in report.findings} == {"ruff", "mypy"}


def test_run_linters_treats_crash_as_unavailable(monkeypatch):
    monkeypatch.setattr(lint, "_is_available", lambda tool: True)
    monkeypatch.setattr(
        lint.subprocess,
        "run",
        lambda *args, **kwargs: _completed(1, "INTERNAL ERROR: broken tool"),
    )
    report = lint.run_linters("x.py")
    assert report.ran == ()
    assert report.missing == ("ruff", "mypy")
    assert report.ok is True


def test_is_available_false_when_not_installed(monkeypatch):
    monkeypatch.setattr(lint.importlib.util, "find_spec", lambda name: None)
    assert lint._is_available("ruff") is False


def test_is_available_false_when_execution_blocked(monkeypatch):
    monkeypatch.setattr(lint.importlib.util, "find_spec", lambda name: object())

    def _raise(*args, **kwargs):
        raise OSError("blocked")

    monkeypatch.setattr(lint.subprocess, "run", _raise)
    assert lint._is_available("mypy") is False


def test_is_available_true_when_version_runs(monkeypatch):
    monkeypatch.setattr(lint.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(
        lint.subprocess, "run", lambda *args, **kwargs: _completed(0, "tool 1.0")
    )
    assert lint._is_available("ruff") is True


def test_is_available_false_when_version_fails(monkeypatch):
    monkeypatch.setattr(lint.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(
        lint.subprocess, "run", lambda *args, **kwargs: _completed(1, "boom")
    )
    assert lint._is_available("ruff") is False
