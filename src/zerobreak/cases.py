"""Descubrimiento de casos de prueba bajo ``test_cases/``."""

from dataclasses import dataclass
from pathlib import Path

CASE_ROOT_NAME = "test_cases"
LEGACY_SUFFIX = "_legacy_anotado.py"
BENCH_PREFIX = "bench_"


@dataclass(frozen=True)
class Case:
    """Un caso de prueba aislado o un módulo en modo archivo libre.

    Attributes:
        name: Nombre identificador del caso.
        path: Ruta absoluta al directorio del caso.
        test_target: Ruta explícita de pruebas (modo archivo libre).
        target_module: Módulo único objetivo (modo archivo libre).
    """

    name: str
    path: Path
    test_target: Path | None = None
    target_module: Path | None = None

    @property
    def test_path(self) -> Path:
        """Ruta objetivo para ejecutar ``pytest``."""
        return self.test_target or self.path

    @property
    def modules(self) -> list[Path]:
        """Módulos de implementación (excluye tests, respaldos y benchmarks)."""
        if self.target_module is not None:
            return [self.target_module]
        result = []
        for file in sorted(self.path.glob("*.py")):
            if file.name.startswith("test_"):
                continue
            if file.name.endswith(LEGACY_SUFFIX):
                continue
            if file.name.startswith(BENCH_PREFIX):
                continue
            result.append(file)
        return result

    @property
    def tests(self) -> list[Path]:
        """Módulos de prueba (``test_*.py``) del caso."""
        return sorted(self.path.glob("test_*.py"))


def find_root(start: Path | None = None) -> Path:
    """Sube desde ``start`` hasta hallar el directorio que contiene ``test_cases/``.

    Args:
        start: Punto de partida; por defecto, el directorio actual.

    Returns:
        La raíz del proyecto.

    Raises:
        FileNotFoundError: Si no se encuentra ``test_cases/`` hacia arriba.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / CASE_ROOT_NAME).is_dir():
            return candidate
    raise FileNotFoundError(
        f"No se encontró un directorio '{CASE_ROOT_NAME}/' desde {current}."
    )


def list_cases(root: Path) -> list[Case]:
    """Devuelve los casos que contienen al menos un módulo de prueba."""
    base = root / CASE_ROOT_NAME
    if not base.is_dir():
        return []
    result = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir() and list(entry.glob("test_*.py")):
            result.append(Case(entry.name, entry))
    return result


def resolve_case(root: Path, name: str) -> Case:
    """Resuelve un caso por nombre o por ruta ``test_cases/<nombre>``.

    Args:
        root: Raíz del proyecto.
        name: Nombre del caso o ruta que termine en él.

    Returns:
        El caso resuelto.

    Raises:
        FileNotFoundError: Si el caso no existe.
    """
    wanted = Path(name).name
    for case in list_cases(root):
        if case.name == wanted:
            return case
    available = ", ".join(case.name for case in list_cases(root)) or "(ninguno)"
    raise FileNotFoundError(f"Caso '{wanted}' no encontrado. Disponibles: {available}.")


def resolve_module(case: Case, name: str | None = None) -> Path:
    """Resuelve el módulo de implementación del caso.

    Si ``name`` se indica, lo usa. Si no, lo deduce: un único módulo, o
    ``<caso>.py`` por convención.

    Args:
        case: Caso objetivo.
        name: Nombre de archivo explícito (opcional).

    Returns:
        La ruta del módulo resuelto.

    Raises:
        FileNotFoundError: Si el módulo indicado no existe o no puede deducirse.
    """
    modules = case.modules
    if name:
        candidate = case.path / name
        if not candidate.is_file():
            disponibles = ", ".join(module.name for module in modules) or "(ninguno)"
            raise FileNotFoundError(
                f"No existe el módulo '{name}' en el caso '{case.name}'. "
                f"Disponibles: {disponibles}."
            )
        return candidate

    if len(modules) == 1:
        return modules[0]

    by_convention = case.path / f"{case.name}.py"
    if by_convention in modules:
        return by_convention

    if not modules:
        raise FileNotFoundError(
            f"El caso '{case.name}' no tiene módulos de implementación."
        )

    disponibles = ", ".join(module.name for module in modules)
    raise FileNotFoundError(
        f"El caso '{case.name}' tiene varios módulos; indica uno con --module. "
        f"Disponibles: {disponibles}."
    )


def resolve_free_case(
    target: Path, tests: Path | None = None, root: Path | None = None
) -> tuple[Path, Case, Path]:
    """Construye un ``Case`` ad-hoc para un archivo ``.py`` fuera de ``test_cases/``.

    Args:
        target: Ruta al archivo ``.py`` que se desea refactorizar.
        tests: Ruta al archivo o directorio de tests (si se omite, busca
            ``test_<modulo>.py`` junto a ``target``).
        root: Directorio de trabajo para ``pytest`` y ``.zerobreak/``
            (por defecto, el directorio padre de ``target``).

    Returns:
        Tupla ``(root, case, module)``.

    Raises:
        FileNotFoundError: Si ``target`` no es un ``.py`` existente o no hay tests.
    """
    module = target.resolve()
    if not module.is_file() or module.suffix != ".py":
        raise FileNotFoundError(
            f"El archivo objetivo '{target}' no existe o no es un módulo '.py'."
        )

    resolved_tests = (
        tests.resolve()
        if tests is not None
        else module.parent / f"test_{module.name}"
    )
    if not resolved_tests.exists():
        raise FileNotFoundError(
            f"No se encontraron tests en '{resolved_tests}'. "
            "Indica la ruta de pruebas con --tests."
        )

    effective_root = root.resolve() if root is not None else module.parent
    case = Case(
        name=module.stem,
        path=module.parent,
        test_target=resolved_tests,
        target_module=module,
    )
    return effective_root, case, module
