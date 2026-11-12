"""Ejecución de pytest en un subproceso aislado."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunResult:
    """Resultado de una invocación de pytest.

    Attributes:
        returncode: Código de salida del proceso.
        output: Salida combinada (stdout + stderr), sin espacios sobrantes.
    """

    returncode: int
    output: str

    @property
    def ok(self) -> bool:
        """Indica si la ejecución terminó en verde."""
        return self.returncode == 0


def run_pytest(root: Path, target: Path) -> RunResult:
    """Ejecuta pytest sobre ``target`` usando ``root`` como directorio de trabajo.

    Args:
        root: Raíz del proyecto (cwd del subproceso).
        target: Ruta del caso o archivo a probar.

    Returns:
        El resultado de la ejecución.
    """
    process = subprocess.run(
        [sys.executable, "-m", "pytest", str(target), "-q"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    output = f"{process.stdout or ''}{process.stderr or ''}".strip()
    return RunResult(process.returncode, output)
