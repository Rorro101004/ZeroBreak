"""Tests unitarios de ``zerobreak.cases`` (find_root, list_cases, resolve_case)."""

import pytest

from zerobreak import cases


def test_find_root_finds_project(project):
    assert cases.find_root(project / "test_cases" / "sample") == project.resolve()


def test_find_root_raises_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError) as exc:
        cases.find_root()
    assert "test_cases" in str(exc.value)


def test_list_cases_returns_only_cases_with_tests(project):
    assert [case.name for case in cases.list_cases(project)] == ["sample"]


def test_list_cases_without_test_cases_dir(tmp_path):
    assert cases.list_cases(tmp_path) == []


def test_list_cases_ignores_dirs_without_tests(project):
    (project / "test_cases" / "vacio").mkdir()
    assert [case.name for case in cases.list_cases(project)] == ["sample"]


def test_resolve_case_by_name_and_by_path(project):
    assert cases.resolve_case(project, "sample").name == "sample"
    assert cases.resolve_case(project, "test_cases/sample").name == "sample"


def test_resolve_case_missing_raises_with_available(project):
    with pytest.raises(FileNotFoundError) as exc:
        cases.resolve_case(project, "no_existe")
    assert "sample" in str(exc.value)


def test_case_modules_excludes_tests_and_legacy(project):
    case = cases.resolve_case(project, "sample")
    (case.path / "calc_legacy_anotado.py").write_text("x = 1\n", encoding="utf-8")
    (case.path / "bench_sample.py").write_text("x = 1\n", encoding="utf-8")
    assert [module.name for module in case.modules] == ["calc.py"]
    assert [test.name for test in case.tests] == ["test_calc.py"]


def test_resolve_module_single(project):
    case = cases.resolve_case(project, "sample")
    assert cases.resolve_module(case).name == "calc.py"


def test_resolve_module_by_explicit_name(project):
    case = cases.resolve_case(project, "sample")
    assert cases.resolve_module(case, "calc.py").name == "calc.py"


def test_resolve_module_explicit_missing(project):
    case = cases.resolve_case(project, "sample")
    with pytest.raises(FileNotFoundError):
        cases.resolve_module(case, "nope.py")


def test_resolve_module_by_convention(project):
    case = cases.resolve_case(project, "sample")
    (case.path / "otro.py").write_text("z = 3\n", encoding="utf-8")
    (case.path / "sample.py").write_text("w = 4\n", encoding="utf-8")
    assert cases.resolve_module(case).name == "sample.py"


def test_resolve_module_multiple_is_ambiguous(project):
    case = cases.resolve_case(project, "sample")
    (case.path / "otro.py").write_text("z = 3\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError) as exc:
        cases.resolve_module(case)
    assert "--module" in str(exc.value)


def test_resolve_module_without_modules(tmp_path):
    empty_case = cases.Case("suelto", tmp_path)
    with pytest.raises(FileNotFoundError):
        cases.resolve_module(empty_case)


def test_resolve_free_case_autodetects_companion_test(tmp_path):
    mod = tmp_path / "pagos.py"
    tst = tmp_path / "test_pagos.py"
    mod.write_text("def cobrar(monto):\n    return monto\n", encoding="utf-8")
    tst.write_text("from pagos import cobrar\n\ndef test_ok():\n    assert cobrar(5) == 5\n", encoding="utf-8")
    root, case, module = cases.resolve_free_case(mod)
    assert root == tmp_path.resolve()
    assert module == mod.resolve()
    assert case.modules == [mod.resolve()]
    assert case.test_path == tst.resolve()


def test_resolve_free_case_rejects_missing_or_non_py(tmp_path):
    txt = tmp_path / "nota.txt"
    txt.write_text("hola", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match=".py"):
        cases.resolve_free_case(txt)
    with pytest.raises(FileNotFoundError, match="no existe"):
        cases.resolve_free_case(tmp_path / "fantasma.py")


def test_resolve_free_case_rejects_missing_tests(tmp_path):
    mod = tmp_path / "pagos.py"
    mod.write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="--tests"):
        cases.resolve_free_case(mod)
