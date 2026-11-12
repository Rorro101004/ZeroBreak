"""Medición de rendimiento: respaldo legacy frente a la versión actual."""

import importlib.util
import sys
import timeit
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from . import backup
from .cases import BENCH_PREFIX, Case

Scenarios = dict[str, Callable[[], object]]


@dataclass(frozen=True)
class BenchRow:
    """Resultado de un escenario medido en ambas versiones.

    Attributes:
        name: Nombre legible del escenario.
        legacy: Mejor tiempo por llamada de la versión legacy (segundos).
        current: Mejor tiempo por llamada de la versión actual (segundos).
    """

    name: str
    legacy: float
    current: float

    @property
    def speedup(self) -> float:
        """Factor de aceleración (``legacy / current``)."""
        return self.legacy / self.current if self.current else float("inf")


def bench_path(case: Case) -> Path:
    """Ruta del archivo de escenarios ``bench_<caso>.py`` de ``case``."""
    return case.path / f"{BENCH_PREFIX}{case.name}.py"


def load_module(path: Path, name: str) -> ModuleType:
    """Carga un módulo Python desde ``path`` sin dejarlo en ``sys.modules``.

    Raises:
        ImportError: Si la ruta no puede cargarse como módulo Python.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def best_time(func: Callable[[], object], number: int | None = None, repeats: int = 3) -> float:
    """Mejor tiempo medio por llamada de ``func`` (en segundos).

    Args:
        func: Invocable sin argumentos a medir.
        number: Llamadas por repetición; si es ``None`` se calibra con ``autorange``.
        repeats: Repeticiones; se toma la mejor para reducir el ruido.
    """
    timer = timeit.Timer(func)
    calls = number if number else timer.autorange()[0]
    return min(timer.repeat(repeat=repeats, number=calls)) / calls


def run_bench(case: Case, module: Path, number: int | None = None) -> list[BenchRow]:
    """Mide los escenarios de ``bench_<caso>.py`` en legacy y en la versión actual.

    Args:
        case: Caso objetivo.
        module: Módulo de implementación actual.
        number: Llamadas por repetición (``None`` para calibrar automáticamente).

    Returns:
        Una fila por escenario.

    Raises:
        FileNotFoundError: Si falta el archivo de escenarios o el respaldo legacy.
        ValueError: Si el archivo de escenarios no define ``escenarios(modulo)``.
    """
    spec_file = bench_path(case)
    if not spec_file.is_file():
        raise FileNotFoundError(
            f"No existe '{spec_file.name}'. Créalo con una función "
            "'escenarios(modulo)' que devuelva {nombre: invocable}."
        )
    legacy = backup.legacy_path(module)
    if not legacy.is_file():
        raise FileNotFoundError(
            f"No existe el respaldo '{legacy.name}'. Ejecuta 'run' o 'snapshot' primero."
        )

    bench_mod = load_module(spec_file, f"_cc_bench_{case.name}")
    escenarios = getattr(bench_mod, "escenarios", None)
    if not callable(escenarios):
        raise ValueError(f"'{spec_file.name}' debe definir 'escenarios(modulo)'.")

    old: Scenarios = escenarios(load_module(legacy, f"_cc_legacy_{case.name}"))
    new: Scenarios = escenarios(load_module(module, f"_cc_current_{case.name}"))
    return [
        BenchRow(name, best_time(old[name], number), best_time(new[name], number))
        for name in old
    ]


def format_report(rows: list[BenchRow]) -> str:
    """Formatea las filas de benchmark como bloque de texto legible."""
    if not rows:
        return "Sin escenarios definidos en el archivo de benchmark."
    lines = ["Benchmark (legacy -> actual), mejor tiempo por llamada:"]
    for row in rows:
        veredicto = (
            f"{row.speedup:.1f}× más rápido"
            if row.speedup >= 1
            else f"{row.speedup:.2f}×, más lento"
        )
        lines.append(
            f"  · {row.name}: {row.legacy * 1000:.3f} ms -> "
            f"{row.current * 1000:.3f} ms ({veredicto})"
        )
    return "\n".join(lines)
