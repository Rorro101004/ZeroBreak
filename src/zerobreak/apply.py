"""Aplicación de un refactor con guardas y rollback automático."""

import difflib
import os
from dataclasses import dataclass
from pathlib import Path

from . import backup
from . import contracts
from . import runner
from . import state as state_mod
from .cases import Case


@dataclass(frozen=True)
class ApplyResult:
    """Resultado de (la planificación de) una aplicación de refactor.

    Attributes:
        ok: Si la operación es válida / terminó en verde.
        message: Mensaje legible para el usuario.
        diff: Diff unificado entre el código actual y el propuesto.
    """

    ok: bool
    message: str
    diff: str


def _unified_diff(before: str, after: str, name: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"{name} (actual)",
            tofile=f"{name} (propuesto)",
        )
    )


def _atomic_write_bytes(target: Path, data: bytes) -> None:
    """Escribe ``data`` en ``target`` de forma atómica vía archivo temporal."""
    tmp = target.with_name(f".{target.name}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, target)


def plan_apply(root: Path, case: Case, module: Path, source: Path) -> ApplyResult:
    """Valida las guardas y genera el diff sin escribir en disco.

    Args:
        root: Raíz del proyecto.
        case: Caso objetivo.
        module: Módulo de implementación que se reemplazaría.
        source: Archivo con el contenido propuesto.

    Returns:
        El resultado de la planificación (con el diff si es válida).
    """
    if not source.is_file():
        return ApplyResult(False, f"El archivo fuente '{source}' no existe.", "")

    entry = state_mod.get_entry(root, case.name)
    if not entry or not entry.get("baseline_ok"):
        return ApplyResult(
            False, "No hay baseline verde registrado. Ejecuta 'baseline' primero.", ""
        )

    recorded = (entry.get("modules") or {}).get(module.name)
    if recorded != state_mod.sha256_file(module):
        return ApplyResult(
            False,
            "El módulo cambió desde el baseline (hash distinto). Re-ejecuta 'baseline'.",
            "",
        )

    before_text = module.read_text(encoding="utf-8")
    after_text = source.read_text(encoding="utf-8")
    diff = _unified_diff(before_text, after_text, module.name)

    violations = contracts.check_contracts(before_text, after_text)
    if violations:
        detalle = "\n".join(f"  - {v}" for v in violations)
        return ApplyResult(False, f"Contrato público roto:\n{detalle}", diff)

    return ApplyResult(True, "Cambio validado; listo para aplicar.", diff)


def apply(root: Path, case: Case, module: Path, source: Path) -> ApplyResult:
    """Aplica el refactor, verifica y revierte si los tests fallan.

    Args:
        root: Raíz del proyecto.
        case: Caso objetivo.
        module: Módulo de implementación a reemplazar.
        source: Archivo con el contenido propuesto.

    Returns:
        El resultado de la operación.
    """
    check = plan_apply(root, case, module, source)
    if not check.ok:
        return check

    backup_path, created = backup.ensure_backup(module)
    original = module.read_bytes()
    _atomic_write_bytes(module, source.read_text(encoding="utf-8").encode("utf-8"))

    result = runner.run_pytest(root, case.test_path)
    if not result.ok:
        _atomic_write_bytes(module, original)
        detalle = result.output or "pytest devolvió un error."
        return ApplyResult(
            False, f"Tests en ROJO; cambio revertido.\n{detalle}", check.diff
        )

    state_mod.record_baseline(root, case.name, case.modules)
    etiqueta = "Respaldo creado" if created else "Respaldo existente"
    return ApplyResult(
        True, f"Tests en verde. {etiqueta}: {backup_path.name}", check.diff
    )
