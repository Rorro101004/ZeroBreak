"""Interfaz de línea de comandos de ZeroBreak."""

import argparse
import sys
from pathlib import Path

from . import apply as apply_mod
from . import backup
from . import bench
from . import cases
from . import lint
from . import metrics
from . import runner
from . import scaffold
from . import state as state_mod
from . import testgen as testgen_mod

PROPOSAL_TEMPLATES = ("propuestas/{case}_mejorado.py", "propuestas/{case}.py")


def _root(args: argparse.Namespace) -> Path:
    return Path(args.root).resolve() if args.root else cases.find_root()


def _cmd_cases(args: argparse.Namespace) -> int:
    found = cases.list_cases(_root(args))
    if not found:
        print("No hay casos en test_cases/.")
        return 0
    for case in found:
        modules = ", ".join(module.name for module in case.modules) or "(sin módulos)"
        print(f"{case.name}: {modules}")
    return 0


def _cmd_new(args: argparse.Namespace) -> int:
    root = _root(args)
    try:
        created = scaffold.create_case(root, args.case)
    except (ValueError, FileExistsError) as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Caso '{args.case}' creado correctamente:")
    for path in (created.module_path, created.test_path, created.proposal_path):
        print(f"  - {path.relative_to(root)}")
    print(f"\nSiguiente paso: zerobreak run {args.case}")
    return 0


def _cmd_scaffold_tests(args: argparse.Namespace) -> int:
    target = Path(args.target)
    out = Path(args.out) if args.out else None
    root = _root(args)
    try:
        res = testgen_mod.generate_tests(target, out=out, root=root)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    rel_test = (
        res.test_path.relative_to(root)
        if res.test_path.is_relative_to(root)
        else res.test_path
    )
    print(f"Suite Golden Master + Hypothesis generada para '{target.name}':")
    print(f"  - Archivo de tests: {rel_test}")
    print(f"  - Funciones caracterizadas: {', '.join(res.functions_captured)}")
    print(f"\nEjecuta los tests con: pytest {rel_test}")
    return 0


def _cmd_baseline(args: argparse.Namespace) -> int:
    root = _root(args)
    case = cases.resolve_case(root, args.case)
    result = runner.run_pytest(root, case.path)
    print(result.output)
    if not result.ok:
        print("\nBaseline en ROJO. No se continúa.")
        return 1
    state_mod.record_baseline(root, case.name, case.modules)
    print(f"\nBaseline verde registrado para '{case.name}'.")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    root = _root(args)
    case = cases.resolve_case(root, args.case)
    result = runner.run_pytest(root, case.path)
    print(result.output)
    return result.returncode


def _cmd_snapshot(args: argparse.Namespace) -> int:
    root = _root(args)
    case = cases.resolve_case(root, args.case)
    module = case.path / args.module
    if not module.is_file():
        print(f"No existe el módulo '{module}'.")
        return 1
    target, created = backup.ensure_backup(module)
    etiqueta = "Respaldo creado" if created else "Respaldo ya existente"
    print(f"{etiqueta}: {target.name}")
    return 0


def _cmd_apply(args: argparse.Namespace) -> int:
    root = _root(args)
    case = cases.resolve_case(root, args.case)
    module = case.path / args.module
    if not module.is_file():
        print(f"No existe el módulo '{module}'.")
        return 1

    planned = apply_mod.plan_apply(root, case, module, Path(args.source))
    if planned.diff:
        print(planned.diff)
    if not planned.ok:
        print(f"\n{planned.message}")
        return 1
    if not args.yes:
        print("\nPrevisualización únicamente. Añade --yes para aplicar.")
        return 0

    result = apply_mod.apply(root, case, module, Path(args.source))
    print(result.message)
    return 0 if result.ok else 1


def _cmd_bench(args: argparse.Namespace) -> int:
    root = _root(args)
    case = cases.resolve_case(root, args.case)
    module = cases.resolve_module(case, args.module)
    try:
        rows = bench.run_bench(case, module, number=args.number)
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Caso '{case.name}' · módulo '{module.name}'")
    print(bench.format_report(rows))
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    root = _root(args)
    entries = state_mod.load_state(root).get("cases", {})
    if args.case:
        entry = entries.get(cases.resolve_case(root, args.case).name)
        if entry is None:
            print("Sin estado registrado para ese caso.")
            return 0
        estado = "verde" if entry.get("baseline_ok") else "sin baseline"
        print(f"{entry.get('updated', '?')} — baseline: {estado}")
        for name in (entry.get("modules") or {}):
            print(f"  - {name}")
        return 0
    if not entries:
        print("Sin estado registrado.")
        return 0
    for name, entry in entries.items():
        estado = "verde" if entry.get("baseline_ok") else "sin baseline"
        print(f"{name}: baseline {estado} ({entry.get('updated', '?')})")
    return 0


def _discover_source(root: Path, case: cases.Case) -> Path | None:
    """Busca una propuesta estándar para ``case`` bajo ``propuestas/``."""
    for template in PROPOSAL_TEMPLATES:
        candidate = root / template.format(case=case.name)
        if candidate.is_file():
            return candidate
    return None


def _ask_confirmation() -> bool:
    """Pausa interactiva: ``True`` si se confirma, ``False`` si se cancela."""
    prompt = "¿Deseas aplicar estos cambios? [Enter/y para confirmar, n para cancelar]: "
    while True:
        try:
            answer = input(prompt).strip().lower()
        except (EOFError, OSError):
            print("\n(Entrada no interactiva: se cancela. Usa --yes para automatizar.)")
            return False
        except KeyboardInterrupt:
            print("\nCancelado.")
            return False
        if answer in ("", "y", "yes", "s", "si", "sí"):
            return True
        if answer in ("n", "no"):
            return False
        print("Respuesta no reconocida: pulsa Enter o 'y' para confirmar, 'n' para cancelar.")


def _resolve_run_target(
    args: argparse.Namespace,
) -> tuple[Path, cases.Case, Path]:
    """Resuelve ``(root, case, module)`` en modo caso o en modo archivo libre."""
    if args.target:
        target_path = Path(args.target)
        tests_path = Path(args.tests) if args.tests else None
        root_path = Path(args.root) if args.root else None
        if tests_path is None and getattr(args, "scaffold_tests", False):
            resolved_mod = target_path.resolve()
            companion = resolved_mod.parent / f"test_{resolved_mod.name}"
            if not companion.exists():
                gen = testgen_mod.generate_tests(resolved_mod, root=root_path)
                print(
                    f"Suite Golden Master + Hypothesis generada: {gen.test_path.name}"
                )
                tests_path = gen.test_path
        return cases.resolve_free_case(target_path, tests_path, root_path)
    if not args.case:
        raise FileNotFoundError(
            "Debes indicar el nombre de un caso o usar --target <archivo.py>."
        )
    root = _root(args)
    case = cases.resolve_case(root, args.case)
    module = cases.resolve_module(case, args.module)
    return root, case, module


def _cmd_run(args: argparse.Namespace) -> int:
    root, case, module = _resolve_run_target(args)
    print(f"Caso '{case.name}' · módulo '{module.name}'")

    # a) Baseline
    baseline = runner.run_pytest(root, case.test_path)
    print(baseline.output)
    if not baseline.ok:
        print("\nBaseline en ROJO. No se continúa.")
        return 1
    state_mod.record_baseline(root, case.name, case.modules)
    print(f"Baseline verde registrado para '{case.name}'.")

    # b) Snapshot didáctico
    backup_path, created = backup.ensure_backup(module)
    etiqueta = "creado" if created else "ya existente"
    print(f"Respaldo didáctico {etiqueta}: {backup_path.name}")

    # Resolver la propuesta: explícita (--source) o autodetectada
    source = Path(args.source) if args.source else _discover_source(root, case)
    if source is None:
        print(
            "\nNo hay propuesta. Pasa --source <archivo> o crea "
            f"propuestas/{case.name}_mejorado.py."
        )
        return 0
    if not args.source:
        print(f"Propuesta detectada: {source.relative_to(root)}")

    # c) Guardas de integridad + diff formateado + comparativa de métricas
    planned = apply_mod.plan_apply(root, case, module, source)
    if planned.diff:
        print("\nCambios propuestos:")
        print(planned.diff)
    if not planned.ok:
        print(f"\n{planned.message}")
        return 1
    print(
        "\n"
        + metrics.format_comparison(
            module.read_text(encoding="utf-8"),
            source.read_text(encoding="utf-8"),
        )
    )

    # c.1) Lint opcional de la propuesta (--lint)
    if args.lint:
        report = lint.run_linters(source)
        print("\nLint de la propuesta (--lint):")
        for tool in report.ran:
            con_hallazgos = any(finding.tool == tool for finding in report.findings)
            print(f"· {tool}: {'con hallazgos' if con_hallazgos else 'sin problemas'}")
        for finding in report.findings:
            if finding.output:
                print(finding.output)
        if report.missing:
            print("· no disponibles (se omiten): " + ", ".join(report.missing))
        if not report.ran:
            print('  instálalas con: pip install -e ".[dev]"')
        if not report.ok:
            print("\nLa propuesta no pasa el lint; no se aplica. Corrige o repite sin --lint.")
            return 1

    # d) Confirmación interactiva (salvo --yes)
    if not args.yes and not _ask_confirmation():
        if created and backup_path.is_file():
            backup_path.unlink()
            print("Cancelado. No se aplicó ningún cambio (respaldo descartado).")
        else:
            print("Cancelado. No se aplicó ningún cambio.")
        return 0

    # e) Aplicar (con verificación post y rollback automático)
    result = apply_mod.apply(root, case, module, source)
    print("\n" + result.message)
    return 0 if result.ok else 1


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de la CLI."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root", help="Raíz del proyecto (por defecto: se autodetecta hacia arriba)."
    )

    parser = argparse.ArgumentParser(
        prog="zerobreak",
        description="Guardarraíl mecánico de refactorización segura (Zero Breakage).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "cases", parents=[common], help="Lista los casos disponibles."
    ).set_defaults(func=_cmd_cases)

    p = sub.add_parser(
        "new",
        parents=[common],
        help="Crea la estructura y plantillas para un nuevo caso de prueba.",
    )
    p.add_argument("case", help="Nombre del nuevo caso (identificador Python válido).")
    p.set_defaults(func=_cmd_new)

    p = sub.add_parser(
        "scaffold-tests",
        parents=[common],
        help="Genera suite de pruebas Golden Master y diferenciales (Hypothesis) para un módulo.",
    )
    p.add_argument("target", help="Archivo .py objetivo a caracterizar.")
    p.add_argument("--out", default=None, help="Ruta de destino del archivo de tests.")
    p.set_defaults(func=_cmd_scaffold_tests)

    p = sub.add_parser(
        "baseline", parents=[common], help="Ejecuta pytest y registra el estado base."
    )
    p.add_argument("case", help="Nombre del caso (p. ej. tienda).")
    p.set_defaults(func=_cmd_baseline)

    p = sub.add_parser(
        "verify", parents=[common], help="Ejecuta pytest sobre un caso."
    )
    p.add_argument("case", help="Nombre del caso.")
    p.set_defaults(func=_cmd_verify)

    p = sub.add_parser(
        "snapshot", parents=[common], help="Crea el respaldo didáctico del módulo."
    )
    p.add_argument("case", help="Nombre del caso.")
    p.add_argument("--module", required=True, help="Archivo del módulo, p. ej. tienda.py.")
    p.set_defaults(func=_cmd_snapshot)

    p = sub.add_parser(
        "apply", parents=[common], help="Aplica un refactor con rollback automático."
    )
    p.add_argument("case", help="Nombre del caso.")
    p.add_argument("--module", required=True, help="Archivo del módulo a reemplazar.")
    p.add_argument("--source", required=True, help="Archivo con el contenido propuesto.")
    p.add_argument("--yes", action="store_true", help="Confirma la escritura en disco.")
    p.set_defaults(func=_cmd_apply)

    p = sub.add_parser(
        "run",
        parents=[common],
        help="Orquesta baseline + respaldo + (opcional) aplicación en un paso.",
    )
    p.add_argument("case", nargs="?", help="Nombre del caso (opcional si se usa --target).")
    p.add_argument("--target", help="Ruta a un archivo .py libre fuera de test_cases/.")
    p.add_argument("--tests", help="Ruta a los tests cuando se usa --target.")
    p.add_argument(
        "--scaffold-tests",
        action="store_true",
        help="Genera suite Golden Master + Hypothesis si no existen tests.",
    )
    p.add_argument("--module", help="Módulo a refactorizar (se deduce si se omite).")
    p.add_argument("--source", help="Propuesta a aplicar (se autodetecta en propuestas/ si se omite).")
    p.add_argument("--lint", action="store_true", help="Analiza la propuesta con ruff/mypy si están instalados.")
    p.add_argument("--yes", action="store_true", help="Confirma la escritura en disco.")
    p.set_defaults(func=_cmd_run)

    p = sub.add_parser(
        "bench",
        parents=[common],
        help="Compara el rendimiento del respaldo legacy frente a la versión actual.",
    )
    p.add_argument("case", help="Nombre del caso.")
    p.add_argument("--module", help="Módulo a medir (se deduce si se omite).")
    p.add_argument(
        "--number", type=int, help="Llamadas por repetición (por defecto: calibración automática)."
    )
    p.set_defaults(func=_cmd_bench)

    p = sub.add_parser(
        "status", parents=[common], help="Muestra el estado guardado."
    )
    p.add_argument("case", nargs="?", help="Nombre del caso (opcional).")
    p.set_defaults(func=_cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de la CLI.

    Args:
        argv: Argumentos (por defecto, ``sys.argv[1:]``).

    Returns:
        El código de salida del proceso.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
