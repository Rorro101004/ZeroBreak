"""Ejecución **opcional** de linters y type-checkers sobre una propuesta.

No añade dependencias al runtime: las herramientas se detectan en tiempo de
ejecución y, si no están disponibles, se omiten con un aviso.
"""

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

#: Herramientas a ejecutar, con sus argumentos base (además del archivo).
LINTERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ruff", ("check",)),
    ("mypy", ()),
)

#: Marcadores de que la herramienta **falló al ejecutarse** (no es un hallazgo).
_CRASH_MARKERS = ("INTERNAL ERROR", "Traceback (most recent call last)")


@dataclass(frozen=True)
class LintFinding:
    """Hallazgo reportado por una herramienta.

    Attributes:
        tool: Nombre de la herramienta (``ruff``, ``mypy``).
        output: Salida combinada de la herramienta.
    """

    tool: str
    output: str


@dataclass(frozen=True)
class LintReport:
    """Resultado de ejecutar las herramientas disponibles.

    Attributes:
        ran: Herramientas que se ejecutaron correctamente.
        missing: Herramientas no disponibles (no instaladas o que fallaron al arrancar).
        findings: Hallazgos por herramienta.
    """

    ran: tuple[str, ...]
    missing: tuple[str, ...]
    findings: tuple[LintFinding, ...]

    @property
    def ok(self) -> bool:
        """``True`` si no hubo ningún hallazgo."""
        return not self.findings


def _looks_like_crash(output: str) -> bool:
    """Detecta un fallo de la herramienta (no un hallazgo sobre el código)."""
    return any(marker in output for marker in _CRASH_MARKERS)


def _is_available(tool: str) -> bool:
    """Comprueba que ``tool`` está instalada **y** se puede ejecutar.

    Ejecutar ``--version`` evita falsos positivos cuando el binario está
    instalado pero bloqueado por el sistema.
    """
    if importlib.util.find_spec(tool) is None:
        return False
    try:
        completed = subprocess.run(
            [sys.executable, "-m", tool, "--version"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return completed.returncode == 0


def run_linters(target: Path) -> LintReport:
    """Ejecuta los linters/type-checkers disponibles sobre ``target``.

    Args:
        target: Archivo (la propuesta) a analizar.

    Returns:
        Un informe con las herramientas ejecutadas, las ausentes y los hallazgos.
    """
    ran: list[str] = []
    missing: list[str] = []
    findings: list[LintFinding] = []

    for tool, extra in LINTERS:
        if not _is_available(tool):
            missing.append(tool)
            continue
        completed = subprocess.run(
            [sys.executable, "-m", tool, *extra, str(target)],
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            ran.append(tool)
            continue
        output = f"{completed.stdout or ''}{completed.stderr or ''}".strip()
        if _looks_like_crash(output):
            missing.append(tool)
            continue
        ran.append(tool)
        findings.append(LintFinding(tool, output or "código de salida distinto de cero"))

    return LintReport(tuple(ran), tuple(missing), tuple(findings))
