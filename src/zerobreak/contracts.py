import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionContract:
    """Información estructural de una función pública para generación de tests."""

    name: str
    params: list[str]
    annotations: dict[str, str]
    return_annotation: str | None = None


def _format_args(args: ast.arguments) -> str:
    """Formatea los nombres de los parámetros ignorando anotaciones de tipo."""
    parts = [arg.arg for arg in (*args.posonlyargs, *args.args)]
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    parts.extend(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return ", ".join(parts)


def _is_public_method(name: str) -> bool:
    """Indica si un método es público o es el constructor ``__init__``."""
    return not name.startswith("_") or name == "__init__"


def _collect_class_methods(
    node: ast.ClassDef, signatures: dict[str, str]
) -> None:
    """Registra la clase pública y sus métodos públicos en ``signatures``."""
    signatures[node.name] = f"class {node.name}"
    for item in node.body:
        if isinstance(
            item, (ast.FunctionDef, ast.AsyncFunctionDef)
        ) and _is_public_method(item.name):
            qualified = f"{node.name}.{item.name}"
            signatures[qualified] = f"{qualified}({_format_args(item.args)})"


def extract_signatures(source: str) -> dict[str, str]:
    """Extrae las firmas públicas (funciones, clases y métodos) de un código.

    Args:
        source: Código fuente en Python.

    Returns:
        Mapa ``{simbolo: firma_canonica}``.

    Raises:
        SyntaxError: Si el código fuente no es Python válido.
    """
    tree = ast.parse(source)
    signatures: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                signatures[node.name] = f"{node.name}({_format_args(node.args)})"
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            _collect_class_methods(node, signatures)
    return signatures


def check_contracts(original: str, proposed: str) -> list[str]:
    """Compara el contrato público original contra el propuesto.

    Verifica que ningún símbolo público existente desaparezca ni altere los
    nombres u orden de sus parámetros. Permite añadir nuevos símbolos,
    anotaciones de tipo, docstrings o funciones privadas (``_...``).

    Args:
        original: Código fuente original.
        proposed: Código fuente propuesto.

    Returns:
        Lista de violaciones detectadas (vacía si el contrato se respeta).
    """
    try:
        before = extract_signatures(original)
        after = extract_signatures(proposed)
    except SyntaxError as exc:
        return [f"Error de sintaxis en el código: {exc.msg} (línea {exc.lineno})."]

    violations: list[str] = []
    for symbol, expected_sig in before.items():
        if symbol not in after:
            violations.append(f"Símbolo público eliminado: '{symbol}'.")
        elif after[symbol] != expected_sig:
            violations.append(
                f"Firma pública alterada: '{expected_sig}' -> '{after[symbol]}'."
            )
    return violations


def inspect_functions(source: str) -> list[FunctionContract]:
    """Extrae las funciones públicas de primer nivel y sus tipos.

    Args:
        source: Código fuente en Python.

    Returns:
        Lista de contratos de función.

    Raises:
        SyntaxError: Si el código fuente no es Python válido.
    """
    tree = ast.parse(source)
    results: list[FunctionContract] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                params = [arg.arg for arg in (*node.args.posonlyargs, *node.args.args)]
                if node.args.vararg:
                    params.append(f"*{node.args.vararg.arg}")
                params.extend(arg.arg for arg in node.args.kwonlyargs)
                if node.args.kwarg:
                    params.append(f"**{node.args.kwarg.arg}")

                annotations: dict[str, str] = {}
                for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                    if arg.annotation is not None:
                        annotations[arg.arg] = ast.unparse(arg.annotation)
                if node.args.vararg and node.args.vararg.annotation:
                    annotations[node.args.vararg.arg] = ast.unparse(
                        node.args.vararg.annotation
                    )
                if node.args.kwarg and node.args.kwarg.annotation:
                    annotations[node.args.kwarg.arg] = ast.unparse(
                        node.args.kwarg.annotation
                    )

                ret_ann = (
                    ast.unparse(node.returns) if node.returns is not None else None
                )
                results.append(
                    FunctionContract(
                        name=node.name,
                        params=params,
                        annotations=annotations,
                        return_annotation=ret_ann,
                    )
                )
    return results

