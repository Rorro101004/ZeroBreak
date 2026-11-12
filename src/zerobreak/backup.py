"""Creación del respaldo didáctico antes de aplicar un refactor."""

from pathlib import Path

from .cases import LEGACY_SUFFIX

_HEADER = '''\
# ============================================================================
# RESPALDO DIDÁCTICO — {name} (pre-refactor)
# ----------------------------------------------------------------------------
# Copia verbatim del código original, creada automáticamente por ZeroBreak
# antes de aplicar un refactor. Añade aquí las anotaciones didácticas (smell,
# por qué perjudica y solución aplicada). NO es código de producción ni un test.
# ============================================================================

'''


def legacy_path(module: Path) -> Path:
    """Ruta del respaldo didáctico correspondiente a ``module``."""
    return module.with_name(f"{module.stem}{LEGACY_SUFFIX}")


def ensure_backup(module: Path) -> tuple[Path, bool]:
    """Crea el respaldo si no existe.

    Args:
        module: Módulo de implementación a respaldar.

    Returns:
        Una tupla ``(ruta_del_respaldo, creado)``.
    """
    target = legacy_path(module)
    if target.is_file():
        return target, False
    body = module.read_text(encoding="utf-8")
    target.write_text(_HEADER.format(name=module.name) + body, encoding="utf-8")
    return target, True
