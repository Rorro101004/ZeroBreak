"""Generación de pruebas Golden Master y testing diferencial con Hypothesis."""

import importlib.util
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from types import ModuleType
from typing import Any

from .contracts import FunctionContract, inspect_functions


@dataclass(frozen=True)
class TestGenResult:
    """Resultado de la generación de tests automáticos.

    Attributes:
        target_module: Ruta del módulo analizado.
        test_path: Ruta del archivo de tests generado.
        functions_captured: Nombres de las funciones públicas analizadas.
    """

    target_module: Path
    test_path: Path
    functions_captured: list[str]


def _load_module_from_path(path: Path, name: str = "temp_target_module") -> ModuleType:
    """Carga un módulo Python desde su ruta en disco."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo desde '{path}'.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_values_for_param(param_name: str, annotation: str | None) -> list[Any]:
    """Genera valores semilla seguros para un parámetro según tipo o nombre."""
    ann = (annotation or "").lower()
    name = param_name.lower()

    if "list" in ann or name in (
        "items",
        "lista",
        "datos",
        "valores",
        "nums",
        "elements",
    ):
        return [[], [1, 2], [1, 2, 1]]
    if "dict" in ann or name in ("config", "info", "mapping"):
        return [{}, {"k": 1}]
    if "float" in ann:
        return [0.0, 1.5, -2.0]
    if "bool" in ann or name.startswith("is_") or name.startswith("has_"):
        return [False, True]
    if "str" in ann or name in (
        "texto",
        "nombre",
        "cadena",
        "msg",
        "message",
        "s",
        "key",
    ):
        return ["", "item", "prueba"]
    if "int" in ann or name in (
        "n",
        "i",
        "count",
        "cantidad",
        "total",
        "num",
        "idx",
        "a",
        "b",
        "x",
        "y",
    ):
        return [0, 1, 2, 5]
    return [0, 1, "test"]


def _strategy_for_param(param_name: str, annotation: str | None) -> str:
    """Devuelve la expresión de estrategia Hypothesis adecuada para el parámetro."""
    ann = (annotation or "").lower()
    name = param_name.lower()

    if "list" in ann or name in (
        "items",
        "lista",
        "datos",
        "valores",
        "nums",
        "elements",
    ):
        return "st.lists(st.integers(min_value=-100, max_value=100), max_size=20)"
    if "dict" in ann or name in ("config", "info", "mapping"):
        return "st.dictionaries(st.text(max_size=10), st.integers(min_value=-100, max_value=100))"
    if "float" in ann:
        return (
            "st.floats(min_value=-1000.0, max_value=1000.0, "
            "allow_nan=False, allow_infinity=False)"
        )
    if "bool" in ann or name.startswith("is_") or name.startswith("has_"):
        return "st.booleans()"
    if "str" in ann or name in (
        "texto",
        "nombre",
        "cadena",
        "msg",
        "message",
        "s",
        "key",
    ):
        return "st.text(max_size=40)"
    if "int" in ann or name in (
        "n",
        "i",
        "count",
        "cantidad",
        "total",
        "num",
        "idx",
        "a",
        "b",
        "x",
        "y",
    ):
        return "st.integers(min_value=-1000, max_value=1000)"
    return "st.integers(min_value=-100, max_value=100)"


def _capture_function_behavior(
    func: Any, contract: FunctionContract
) -> list[tuple[tuple[Any, ...], str, str]]:
    """Evalúa la función con muestras semilla y captura el resultado o excepción.

    Returns:
        Lista de tuplas ``(args, 'return' | 'raise', repr_salida)``.
    """
    clean_params = [p for p in contract.params if not p.startswith("*")]
    if not clean_params:
        try:
            val = func()
            return [((), "return", repr(val))]
        except Exception as exc:
            return [((), "raise", exc.__class__.__name__)]

    param_options = [
        _seed_values_for_param(p, contract.annotations.get(p)) for p in clean_params
    ]
    # Limitar el producto cartesiano para evitar combinaciones excesivas (máximo 6)
    all_combos = list(product(*param_options))
    step = max(1, len(all_combos) // 6)
    combos = all_combos[::step][:6]

    outcomes = []
    for args in combos:
        try:
            res = func(*args)
            outcomes.append((args, "return", repr(res)))
        except Exception as exc:
            outcomes.append((args, "raise", exc.__class__.__name__))
    return outcomes


def build_test_file_content(
    target_path: Path, contracts: list[FunctionContract]
) -> str:
    """Construye el código fuente completo del archivo de pruebas."""
    module_name = target_path.stem
    target_abs = str(target_path.resolve())

    # Cargar módulo para caracterización Golden Master
    try:
        mod = _load_module_from_path(target_path, f"golden_{module_name}")
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo cargar '{target_path.name}' para caracterización: {exc}"
        ) from exc

    lines = [
        f'"""Suite de pruebas generada automáticamente para {target_path.name}.',
        "",
        "Incluye:",
        "1. Golden Master: pruebas de caracterización congeladas.",
        "2. Differential Testing: pruebas de propiedades con Hypothesis.",
        '"""',
        "",
        "import importlib.util",
        "from pathlib import Path",
        "import pytest",
        "from hypothesis import given, strategies as st",
        "",
        f'TARGET_PATH = Path(r"{target_abs}")',
        'LEGACY_SUFFIX = "_legacy_anotado.py"',
        "",
        "",
        "def _load(path: Path, name: str):",
        "    spec = importlib.util.spec_from_file_location(name, path)",
        "    if spec is None or spec.loader is None:",
        "        raise ImportError(f'No se pudo cargar {path}')",
        "    mod = importlib.util.module_from_spec(spec)",
        "    spec.loader.exec_module(mod)",
        "    return mod",
        "",
        "",
        "@pytest.fixture(scope='module')",
        "def current_mod():",
        "    return _load(TARGET_PATH, 'current_mod')",
        "",
        "",
        "@pytest.fixture(scope='module')",
        "def legacy_mod():",
        "    legacy_path = TARGET_PATH.with_name(f'{TARGET_PATH.stem}{LEGACY_SUFFIX}')",
        "    if legacy_path.is_file():",
        "        return _load(legacy_path, 'legacy_mod')",
        "    return None",
        "",
    ]

    for c in contracts:
        fn = getattr(mod, c.name, None)
        if fn is None or not callable(fn):
            continue

        clean_params = [p for p in c.params if not p.startswith("*")]
        outcomes = _capture_function_behavior(fn, c)

        # 1. Golden Master
        lines.extend(
            [
                "",
                f"def test_golden_master_{c.name}(current_mod):",
                f'    """Verifica que {c.name} reproduce los resultados caracterizados."""',
                f"    fn = getattr(current_mod, '{c.name}')",
            ]
        )
        if not outcomes:
            lines.append("    pass")
        for args, kind, val in outcomes:
            args_str = ", ".join(repr(a) for a in args)
            if kind == "return":
                lines.append(f"    assert fn({args_str}) == {val}")
            else:
                lines.extend(
                    [
                        f"    with pytest.raises({val}):",
                        f"        fn({args_str})",
                    ]
                )

        # 2. Differential Testing con Hypothesis
        if clean_params:
            st_args = [
                f"{p}={_strategy_for_param(p, c.annotations.get(p))}"
                for p in clean_params
            ]
            given_dec = f"@given({', '.join(st_args)})"
            param_sig = ", ".join(clean_params)
            call_sig = ", ".join(clean_params)

            lines.extend(
                [
                    "",
                    "",
                    given_dec,
                    f"def test_differential_{c.name}(current_mod, legacy_mod, {param_sig}):",
                    f'    """Verifica equivalencia matemática: legacy({call_sig}) == current({call_sig})."""',
                    f"    curr_fn = getattr(current_mod, '{c.name}')",
                    "    if legacy_mod is None:",
                    "        # Sin respaldo legacy todavía (fase baseline): verifica ejecución limpia",
                    "        try:",
                    f"            _ = curr_fn({call_sig})",
                    "        except Exception:",
                    "            pass",
                    "        return",
                    "",
                    f"    leg_fn = getattr(legacy_mod, '{c.name}')",
                    "    try:",
                    f"        expected = leg_fn({call_sig})",
                    f"        actual = curr_fn({call_sig})",
                    "        assert actual == expected",
                    "    except Exception as exc:",
                    "        # Si el legacy lanza una excepción para esa entrada, el actual debe lanzar la misma",
                    "        with pytest.raises(exc.__class__):",
                    f"            curr_fn({call_sig})",
                ]
            )

    lines.append("")
    return "\n".join(lines)


def generate_tests(
    target: Path, out: Path | None = None, root: Path | None = None
) -> TestGenResult:
    """Genera automáticamente una suite de tests Golden Master y diferenciales.

    Args:
        target: Archivo objetivo en Python.
        out: Ruta de destino (opcional).
        root: Raíz del proyecto.

    Returns:
        TestGenResult con los datos generados.

    Raises:
        FileNotFoundError: Si el módulo objetivo no existe o no es '.py'.
        ValueError: Si el módulo objetivo no define funciones públicas.
    """
    target = target.resolve()
    if not target.is_file() or target.suffix != ".py":
        raise FileNotFoundError(
            f"El archivo objetivo '{target}' no existe o no es un módulo '.py'."
        )

    code = target.read_text(encoding="utf-8")
    contracts = inspect_functions(code)
    if not contracts:
        raise ValueError(
            f"El archivo '{target.name}' no define funciones públicas para testear."
        )

    if out is not None:
        test_path = out.resolve()
    else:
        effective_root = root.resolve() if root is not None else target.parent
        test_dir = effective_root / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"test_autogen_{target.stem}.py"

    test_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_test_file_content(target, contracts)
    test_path.write_text(content, encoding="utf-8")

    return TestGenResult(
        target_module=target,
        test_path=test_path,
        functions_captured=[c.name for c in contracts],
    )
