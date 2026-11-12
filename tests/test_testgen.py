"""Tests unitarios del generador de pruebas Golden Master y diferencial."""

from pathlib import Path

import pytest

from zerobreak import runner, testgen
from zerobreak.contracts import FunctionContract


def test_generate_tests_rejects_missing_or_non_py(tmp_path: Path):
    missing = tmp_path / "inexistente.py"
    with pytest.raises(FileNotFoundError, match="no existe o no es un módulo"):
        testgen.generate_tests(missing)

    non_py = tmp_path / "texto.txt"
    non_py.write_text("hola", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="no existe o no es un módulo"):
        testgen.generate_tests(non_py)


def test_generate_tests_rejects_empty_or_private_only(tmp_path: Path):
    mod = tmp_path / "vacio.py"
    mod.write_text("def _privada():\n    pass\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no define funciones públicas"):
        testgen.generate_tests(mod)


def test_generate_tests_handles_import_error(tmp_path: Path):
    mod = tmp_path / "crash_on_import.py"
    mod.write_text("def f():\n    pass\nraise RuntimeError('crash')\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="No se pudo cargar"):
        testgen.generate_tests(mod)


def test_generate_tests_and_execute_golden_and_hypothesis(tmp_path: Path):
    mod = tmp_path / "matematica.py"
    mod.write_text(
        "def sumar(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "def dividir(x: float, y: float) -> float:\n"
        "    return x / y\n\n"
        "def sin_args() -> int:\n"
        "    return 100\n",
        encoding="utf-8",
    )

    out_file = tmp_path / "test_matematica_autogen.py"
    res = testgen.generate_tests(mod, out=out_file, root=tmp_path)

    assert res.target_module == mod.resolve()
    assert res.test_path == out_file.resolve()
    assert set(res.functions_captured) == {"sumar", "dividir", "sin_args"}
    assert out_file.is_file()

    content = out_file.read_text(encoding="utf-8")
    assert "test_golden_master_sumar" in content
    assert "test_golden_master_dividir" in content
    assert "test_golden_master_sin_args" in content
    assert "ZeroDivisionError" in content
    assert "test_differential_sumar" in content
    assert "test_differential_dividir" in content
    assert "@given(" in content

    # Ejecutar pytest sobre el archivo generado en fase baseline (legacy_mod is None)
    result = runner.run_pytest(tmp_path, out_file)
    assert result.ok, f"Fallo al ejecutar tests generados:\n{result.output}"

    # Simular la creación del respaldo legacy y una propuesta idéntica:
    legacy_file = tmp_path / "matematica_legacy_anotado.py"
    legacy_file.write_text(mod.read_text(encoding="utf-8"), encoding="utf-8")

    # Re-ejecutar: ahora legacy_mod existe y se activa la comparación diferencial
    result_diff = runner.run_pytest(tmp_path, out_file)
    assert result_diff.ok, f"Fallo diferencial idéntico:\n{result_diff.output}"

    # Ahora introducimos un bug de lógica en matematica.py (resta en vez de suma)
    mod.write_text(
        "def sumar(a: int, b: int) -> int:\n"
        "    return a - b\n\n"
        "def dividir(x: float, y: float) -> float:\n"
        "    return x / y\n\n"
        "def sin_args() -> int:\n"
        "    return 100\n",
        encoding="utf-8",
    )
    result_bug = runner.run_pytest(tmp_path, out_file)
    assert not result_bug.ok
    assert "AssertionError" in result_bug.output or "Falsifying example" in result_bug.output


def test_seed_and_strategy_coverage():
    # Probar que las estrategias cubren tipos especiales
    contract_misc = FunctionContract(
        name="misc",
        params=["texto", "items", "is_activo", "info", "ratio", "extra_val"],
        annotations={
            "texto": "str",
            "items": "list[int]",
            "is_activo": "bool",
            "info": "dict[str, Any]",
            "ratio": "float",
            "extra_val": "unknown",
        },
    )
    seeds = [
        testgen._seed_values_for_param(p, contract_misc.annotations.get(p))
        for p in contract_misc.params
    ]
    assert len(seeds) == 6
    assert seeds[4] == [0.0, 1.5, -2.0]  # float

    strategies = [
        testgen._strategy_for_param(p, contract_misc.annotations.get(p))
        for p in contract_misc.params
    ]
    assert any("text" in s for s in strategies)
    assert any("lists" in s for s in strategies)
    assert any("dictionaries" in s for s in strategies)
    assert any("floats" in s for s in strategies)
    assert any("booleans" in s for s in strategies)


def test_build_test_file_content_handles_no_outcomes(tmp_path: Path):
    mod = tmp_path / "crash_fn.py"
    mod.write_text(
        "def solo_vararg(*args):\n    return sum(args)\n", encoding="utf-8"
    )
    # vararg only -> clean_params is empty -> runs solo_vararg()
    res = testgen.generate_tests(mod, root=tmp_path)
    assert res.test_path.is_file()


def test_load_module_from_path_failure(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        testgen.importlib.util, "spec_from_file_location", lambda *args: None
    )
    with pytest.raises(ImportError, match="No se pudo cargar"):
        testgen._load_module_from_path(tmp_path / "dummy.py")


def test_capture_function_behavior_zero_args_raising():
    contract = FunctionContract(name="falla", params=[], annotations={})

    def falla():
        raise ValueError("boom")

    outcomes = testgen._capture_function_behavior(falla, contract)
    assert outcomes == [((), "raise", "ValueError")]


def test_build_test_file_content_ignores_non_callable_and_empty_outcomes(
    monkeypatch, tmp_path: Path
):
    mod = tmp_path / "extra.py"
    mod.write_text("def fn_vacia(x):\n    return x\n", encoding="utf-8")
    contracts = [
        FunctionContract(name="no_existe", params=["x"], annotations={}),
        FunctionContract(name="fn_vacia", params=["x"], annotations={}),
    ]
    content = testgen.build_test_file_content(mod, contracts)
    assert "test_golden_master_fn_vacia" in content
    assert "test_golden_master_no_existe" not in content

    # Mock empty outcomes para cubrir lines.append("    pass")
    monkeypatch.setattr(testgen, "_capture_function_behavior", lambda f, c: [])
    content_empty = testgen.build_test_file_content(
        mod, [FunctionContract(name="fn_vacia", params=["x"], annotations={})]
    )
    assert "    pass" in content_empty


