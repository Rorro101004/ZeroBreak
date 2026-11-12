from pathlib import Path

from zerobreak import cli
from zerobreak import lint as lint_mod
from zerobreak import state as state_mod


def test_cases_command(project, capsys):
    code = cli.main(["cases", "--root", str(project)])
    assert code == 0
    assert "sample" in capsys.readouterr().out


def test_cases_command_empty(tmp_path, capsys):
    code = cli.main(["cases", "--root", str(tmp_path)])
    assert code == 0
    assert "No hay casos" in capsys.readouterr().out


def test_new_command_creates_case_and_runs_cleanly(project, capsys):
    code = cli.main(["new", "usuarios", "--root", str(project)])
    assert code == 0
    out = capsys.readouterr().out
    assert "usuarios" in out
    assert (project / "test_cases" / "usuarios" / "usuarios.py").is_file()
    assert (project / "test_cases" / "usuarios" / "test_usuarios.py").is_file()
    assert (project / "propuestas" / "usuarios_mejorado.py").is_file()

    run_code = cli.main(["run", "usuarios", "--yes", "--root", str(project)])
    assert run_code == 0


def test_new_command_rejects_duplicate_or_invalid(project, capsys):
    assert cli.main(["new", "sample", "--root", str(project)]) == 1
    assert "Error" in capsys.readouterr().out
    assert cli.main(["new", "invalido-nombre", "--root", str(project)]) == 1


def test_root_autodetected(project, monkeypatch, capsys):
    monkeypatch.chdir(project / "test_cases" / "sample")
    assert cli.main(["cases"]) == 0
    assert "sample" in capsys.readouterr().out


def test_missing_root_returns_2(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert cli.main(["cases"]) == 2
    assert "Error" in capsys.readouterr().out


def test_baseline_records_state(project):
    assert cli.main(["baseline", "sample", "--root", str(project)]) == 0
    assert state_mod.get_entry(project, "sample")["baseline_ok"] is True


def test_verify_returns_zero(project):
    assert cli.main(["verify", "sample", "--root", str(project)]) == 0


def test_snapshot_creates_backup(project):
    code = cli.main(["snapshot", "sample", "--module", "calc.py", "--root", str(project)])
    assert code == 0
    assert (project / "test_cases" / "sample" / "calc_legacy_anotado.py").is_file()


def test_snapshot_missing_module(project, capsys):
    code = cli.main(["snapshot", "sample", "--module", "nope.py", "--root", str(project)])
    assert code == 1
    assert "No existe" in capsys.readouterr().out


def test_status_with_case(project, capsys):
    cli.main(["baseline", "sample", "--root", str(project)])
    assert cli.main(["status", "sample", "--root", str(project)]) == 0
    assert "calc.py" in capsys.readouterr().out


def test_status_unknown_case(project, capsys):
    assert cli.main(["status", "sample", "--root", str(project)]) == 0
    assert "Sin estado" in capsys.readouterr().out


def test_apply_preview_does_not_write(project):
    cli.main(["baseline", "sample", "--root", str(project)])
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    code = cli.main(
        ["apply", "sample", "--module", "calc.py", "--source", str(src), "--root", str(project)]
    )
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "cambiado" not in current


def test_apply_yes_writes_change(project):
    cli.main(["baseline", "sample", "--root", str(project)])
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    code = cli.main(
        [
            "apply",
            "sample",
            "--module",
            "calc.py",
            "--source",
            str(src),
            "--yes",
            "--root",
            str(project),
        ]
    )
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "cambiado" in current


def test_apply_missing_module(project, capsys):
    src = project / "proposed.py"
    src.write_text("x = 1\n", encoding="utf-8")
    code = cli.main(
        ["apply", "sample", "--module", "nope.py", "--source", str(src), "--root", str(project)]
    )
    assert code == 1
    assert "No existe" in capsys.readouterr().out


def test_apply_missing_source(project, capsys):
    code = cli.main(
        [
            "apply",
            "sample",
            "--module",
            "calc.py",
            "--source",
            str(project / "no_existe.py"),
            "--root",
            str(project),
        ]
    )
    assert code == 1
    assert "no existe" in capsys.readouterr().out.lower()


def test_missing_case_returns_2(project, capsys):
    assert cli.main(["baseline", "nope", "--root", str(project)]) == 2


def test_run_baseline_and_backup(project, capsys):
    code = cli.main(["run", "sample", "--root", str(project)])
    assert code == 0
    assert state_mod.get_entry(project, "sample")["baseline_ok"] is True
    assert (project / "test_cases" / "sample" / "calc_legacy_anotado.py").is_file()


def test_run_cancel_does_not_write(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    code = cli.main(["run", "sample", "--source", str(src), "--root", str(project)])
    sample = project / "test_cases" / "sample"
    assert code == 0
    assert "cambiado" not in (sample / "calc.py").read_text(encoding="utf-8")
    assert not (sample / "calc_legacy_anotado.py").exists()


def test_run_interactive_confirm_applies(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    code = cli.main(["run", "sample", "--source", str(src), "--root", str(project)])
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "cambiado" in current


def test_run_interactive_reprompts_on_unknown(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    answers = iter(["quizas", "y"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    code = cli.main(["run", "sample", "--source", str(src), "--root", str(project)])
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "cambiado" in current


def test_run_interactive_eof_cancels(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b\n", encoding="utf-8"
    )

    def _raise(prompt=""):
        raise OSError("no stdin")

    monkeypatch.setattr("builtins.input", _raise)
    assert cli.main(["run", "sample", "--source", str(src), "--root", str(project)]) == 0


def test_run_interactive_keyboard_interrupt_cancels(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b\n", encoding="utf-8"
    )

    def _raise(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", _raise)
    assert cli.main(["run", "sample", "--source", str(src), "--root", str(project)]) == 0


def test_run_auto_discovers_proposal(project):
    propuestas = project / "propuestas"
    propuestas.mkdir()
    (propuestas / "sample_mejorado.py").write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # auto\n",
        encoding="utf-8",
    )
    code = cli.main(["run", "sample", "--yes", "--root", str(project)])
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "auto" in current


def test_run_without_proposal_returns_0(project, capsys):
    assert cli.main(["run", "sample", "--root", str(project)]) == 0
    assert "No hay propuesta" in capsys.readouterr().out


def test_run_cancel_keeps_existing_backup(project, monkeypatch):
    sample = project / "test_cases" / "sample"
    (sample / "calc_legacy_anotado.py").write_text("PRE-EXISTENTE\n", encoding="utf-8")
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    code = cli.main(["run", "sample", "--source", str(src), "--root", str(project)])
    assert code == 0
    assert (sample / "calc_legacy_anotado.py").read_text(encoding="utf-8") == "PRE-EXISTENTE\n"
    assert "cambiado" not in (sample / "calc.py").read_text(encoding="utf-8")


def test_run_lint_clean_applies(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # lintok\n",
        encoding="utf-8",
    )
    report = lint_mod.LintReport(("ruff", "mypy"), (), ())
    monkeypatch.setattr(cli.lint, "run_linters", lambda target: report)
    code = cli.main(
        ["run", "sample", "--source", str(src), "--lint", "--yes", "--root", str(project)]
    )
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "lintok" in current


def test_run_lint_blocks_on_findings(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # lintbad\n",
        encoding="utf-8",
    )
    report = lint_mod.LintReport(
        ("ruff", "mypy"),
        (),
        (lint_mod.LintFinding("ruff", "F401 boom"), lint_mod.LintFinding("mypy", "")),
    )
    monkeypatch.setattr(cli.lint, "run_linters", lambda target: report)
    code = cli.main(
        ["run", "sample", "--source", str(src), "--lint", "--yes", "--root", str(project)]
    )
    assert code == 1
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "lintbad" not in current


def test_run_lint_missing_tools_continues(project, monkeypatch):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # lintnone\n",
        encoding="utf-8",
    )
    report = lint_mod.LintReport((), ("ruff", "mypy"), ())
    monkeypatch.setattr(cli.lint, "run_linters", lambda target: report)
    code = cli.main(
        ["run", "sample", "--source", str(src), "--lint", "--yes", "--root", str(project)]
    )
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "lintnone" in current


def test_run_applies_with_yes(project):
    src = project / "proposed.py"
    src.write_text(
        "class Calc:\n    def add(self, a, b):\n        return a + b  # cambiado\n",
        encoding="utf-8",
    )
    code = cli.main(
        ["run", "sample", "--source", str(src), "--yes", "--root", str(project)]
    )
    assert code == 0
    current = (project / "test_cases" / "sample" / "calc.py").read_text(encoding="utf-8")
    assert "cambiado" in current


def test_run_ambiguous_module_returns_2(project):
    (project / "test_cases" / "sample" / "otro.py").write_text("z = 3\n", encoding="utf-8")
    assert cli.main(["run", "sample", "--root", str(project)]) == 2


def _make_red_case(root):
    case = root / "test_cases" / "rojo"
    case.mkdir(parents=True)
    (case / "rojo.py").write_text("def valor():\n    return 1\n", encoding="utf-8")
    (case / "test_rojo.py").write_text(
        "from rojo import valor\n\n\ndef test_valor():\n    assert valor() == 2\n",
        encoding="utf-8",
    )
    return case


def test_baseline_red_returns_1(tmp_path):
    _make_red_case(tmp_path)
    assert cli.main(["baseline", "rojo", "--root", str(tmp_path)]) == 1


def test_run_red_baseline_returns_1(tmp_path):
    _make_red_case(tmp_path)
    assert cli.main(["run", "rojo", "--root", str(tmp_path)]) == 1


def test_run_missing_source_returns_1(project):
    code = cli.main(
        [
            "run",
            "sample",
            "--source",
            str(project / "no_existe.py"),
            "--root",
            str(project),
        ]
    )
    assert code == 1


def test_status_global_lists_cases(project, capsys):
    cli.main(["baseline", "sample", "--root", str(project)])
    assert cli.main(["status", "--root", str(project)]) == 0
    assert "sample" in capsys.readouterr().out


def test_status_global_empty(tmp_path, capsys):
    assert cli.main(["status", "--root", str(tmp_path)]) == 0
    assert "Sin estado" in capsys.readouterr().out


def test_run_free_file_mode_outside_test_cases(tmp_path):
    app_dir = tmp_path / "mi_app"
    tests_dir = tmp_path / "mis_tests"
    app_dir.mkdir()
    tests_dir.mkdir()
    target = app_dir / "util.py"
    test_file = tests_dir / "test_util.py"
    propuesta = tmp_path / "util_mejorado.py"

    target.write_text("def doble(x):\n    return x + x\n", encoding="utf-8")
    test_file.write_text(
        "from util import doble\n\n\ndef test_doble():\n    assert doble(4) == 8\n",
        encoding="utf-8",
    )
    propuesta.write_text(
        '"""Optimizado."""\n\n\ndef doble(x: int) -> int:\n    """Duplica x."""\n    return x * 2\n',
        encoding="utf-8",
    )

    code = cli.main(
        [
            "run",
            "--target",
            str(target),
            "--tests",
            str(test_file),
            "--source",
            str(propuesta),
            "--yes",
        ]
    )
    assert code == 0
    assert "x * 2" in target.read_text(encoding="utf-8")
    assert (app_dir / "util_legacy_anotado.py").is_file()


def test_run_without_case_or_target_returns_2(project, capsys):
    assert cli.main(["run", "--root", str(project)]) == 2
    assert "--target" in capsys.readouterr().out


def test_scaffold_tests_subcommand_generates_suite(tmp_path: Path, capsys):
    target = tmp_path / "modulo.py"
    target.write_text(
        "def triplicar(x: int) -> int:\n    return x * 3\n", encoding="utf-8"
    )
    out = tmp_path / "custom_test.py"
    code = cli.main(
        [
            "scaffold-tests",
            str(target),
            "--out",
            str(out),
            "--root",
            str(tmp_path),
        ]
    )
    assert code == 0
    assert out.is_file()
    captured = capsys.readouterr().out
    assert "Suite Golden Master + Hypothesis generada" in captured
    assert "triplicar" in captured


def test_scaffold_tests_subcommand_handles_error(tmp_path: Path, capsys):
    target = tmp_path / "vacio.py"
    target.write_text("x = 1\n", encoding="utf-8")
    code = cli.main(["scaffold-tests", str(target), "--root", str(tmp_path)])
    assert code == 1
    assert "no define funciones públicas" in capsys.readouterr().out


def test_run_with_scaffold_tests_flag(tmp_path: Path, capsys):
    target = tmp_path / "calc_libre.py"
    target.write_text(
        "def doble(x: int) -> int:\n    return x + x\n", encoding="utf-8"
    )
    propuesta = tmp_path / "calc_libre_mejorado.py"
    propuesta.write_text(
        '"""Doble."""\n\ndef doble(x: int) -> int:\n    """Doc."""\n    return x * 2\n',
        encoding="utf-8",
    )

    code = cli.main(
        [
            "run",
            "--target",
            str(target),
            "--source",
            str(propuesta),
            "--scaffold-tests",
            "--yes",
            "--root",
            str(tmp_path),
        ]
    )
    assert code == 0
    captured = capsys.readouterr().out
    assert "Suite Golden Master + Hypothesis generada" in captured
    assert "x * 2" in target.read_text(encoding="utf-8")
    assert (tmp_path / "calc_libre_legacy_anotado.py").is_file()


def test_run_with_scaffold_tests_flag_when_companion_exists(tmp_path: Path):
    target = tmp_path / "existente.py"
    target.write_text(
        "def doble(x: int) -> int:\n    return x + x\n", encoding="utf-8"
    )
    companion = tmp_path / "test_existente.py"
    companion.write_text(
        "from existente import doble\ndef test_d(): assert doble(2) == 4\n",
        encoding="utf-8",
    )
    propuesta = tmp_path / "existente_mejorado.py"
    propuesta.write_text(
        'def doble(x: int) -> int:\n    return x * 2\n', encoding="utf-8"
    )

    code = cli.main(
        [
            "run",
            "--target",
            str(target),
            "--source",
            str(propuesta),
            "--scaffold-tests",
            "--yes",
            "--root",
            str(tmp_path),
        ]
    )
    assert code == 0

