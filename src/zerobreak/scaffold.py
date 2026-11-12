"""Generación de plantillas (scaffolding) para nuevos casos de prueba."""

from dataclasses import dataclass
from pathlib import Path

from .cases import CASE_ROOT_NAME

MODULE_TEMPLATE = '''"""Módulo de implementación para el caso '{name}'."""


def resolver(datos: list[int]) -> int:
    """Calcula el resultado a partir de ``datos``."""
    total = 0
    for valor in datos:
        total = total + valor
    return total
'''

TEST_TEMPLATE = '''"""Suite de pruebas para el caso '{name}'."""

from {name} import resolver


def test_resolver_basico() -> None:
    assert resolver([1, 2, 3]) == 6


def test_resolver_vacio() -> None:
    assert resolver([]) == 0
'''

PROPOSAL_TEMPLATE = '''"""Propuesta refactorizada para el caso '{name}'."""


def resolver(datos: list[int]) -> int:
    """Calcula el resultado a partir de ``datos``.

    Args:
        datos: Lista de enteros a procesar.

    Returns:
        La suma total de los elementos.
    """
    return sum(datos)
'''


@dataclass(frozen=True)
class ScaffoldResult:
    """Rutas generadas al crear un nuevo caso de prueba.

    Attributes:
        case_dir: Directorio del caso dentro de ``test_cases/``.
        module_path: Archivo de implementación inicial.
        test_path: Suite de pruebas inicial.
        proposal_path: Plantilla de propuesta bajo ``propuestas/``.
    """

    case_dir: Path
    module_path: Path
    test_path: Path
    proposal_path: Path


def create_case(root: Path, name: str) -> ScaffoldResult:
    """Crea la estructura de directorios y plantillas para un caso nuevo.

    Args:
        root: Raíz del proyecto.
        name: Nombre del caso (debe ser un identificador Python válido).

    Returns:
        Las rutas creadas en disco.

    Raises:
        ValueError: Si ``name`` no es un identificador válido o usa prefijos reservados.
        FileExistsError: Si el directorio del caso ya existe.
    """
    if not name.isidentifier() or name.startswith("_") or name.startswith("test_"):
        raise ValueError(
            f"Nombre de caso inválido: '{name}'. "
            "Usa un identificador Python válido que no empiece por '_' ni 'test_'."
        )

    case_dir = root / CASE_ROOT_NAME / name
    if case_dir.exists():
        raise FileExistsError(
            f"El caso '{name}' ya existe en '{CASE_ROOT_NAME}/{name}'."
        )

    case_dir.mkdir(parents=True, exist_ok=False)
    module_path = case_dir / f"{name}.py"
    test_path = case_dir / f"test_{name}.py"
    proposal_path = root / "propuestas" / f"{name}_mejorado.py"
    proposal_path.parent.mkdir(parents=True, exist_ok=True)

    module_path.write_text(MODULE_TEMPLATE.format(name=name), encoding="utf-8")
    test_path.write_text(TEST_TEMPLATE.format(name=name), encoding="utf-8")
    proposal_path.write_text(PROPOSAL_TEMPLATE.format(name=name), encoding="utf-8")

    return ScaffoldResult(
        case_dir=case_dir,
        module_path=module_path,
        test_path=test_path,
        proposal_path=proposal_path,
    )
