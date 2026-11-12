"""Métricas estáticas deterministas para comparar el impacto de un refactor."""

import ast
from dataclasses import dataclass

from . import contracts


@dataclass(frozen=True)
class CodeMetrics:
    """Instantánea de métricas de calidad y tamaño de un módulo Python.

    Attributes:
        sloc: Líneas efectivas de código (sin vacías ni comentarios).
        public_symbols: Cantidad de funciones, clases y métodos públicos.
        typed_functions: Funciones/métodos con anotación de retorno PEP 484.
        total_functions: Total de funciones y métodos definidos.
        docstrings: Total de docstrings (módulo, clases y funciones).
    """

    sloc: int
    public_symbols: int
    typed_functions: int
    total_functions: int
    docstrings: int


def _count_sloc(source: str) -> int:
    """Cuenta las líneas no vacías que no son comentarios puros."""
    return sum(
        1
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def analyze(source: str) -> CodeMetrics:
    """Calcula las métricas estáticas de ``source`` mediante ``ast``.

    Args:
        source: Código fuente en Python válido.

    Returns:
        Objeto ``CodeMetrics`` con el conteo del código.
    """
    tree = ast.parse(source)
    fn_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    doc_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        )
    ]
    return CodeMetrics(
        sloc=_count_sloc(source),
        public_symbols=len(contracts.extract_signatures(source)),
        typed_functions=sum(1 for node in fn_nodes if node.returns is not None),
        total_functions=len(fn_nodes),
        docstrings=sum(1 for node in doc_nodes if ast.get_docstring(node) is not None),
    )


def _format_delta(before: int, after: int) -> str:
    """Formatea el cambio numérico con signo explícito."""
    diff = after - before
    return f"{before} -> {after} ({diff:+d})"


def format_comparison(before_source: str, after_source: str) -> str:
    """Genera un resumen legible comparando las métricas antes y después.

    Args:
        before_source: Código fuente original.
        after_source: Código fuente propuesto.

    Returns:
        Bloque de texto multi-línea con la comparativa.
    """
    before = analyze(before_source)
    after = analyze(after_source)
    return "\n".join(
        [
            "Resumen de métricas (actual -> propuesto):",
            f"  · Líneas efectivas (SLOC): {_format_delta(before.sloc, after.sloc)}",
            f"  · Símbolos públicos:       {before.public_symbols} -> {after.public_symbols}",
            f"  · Funciones tipadas:       {before.typed_functions}/{before.total_functions}"
            f" -> {after.typed_functions}/{after.total_functions}",
            f"  · Docstrings (PEP 257):    {_format_delta(before.docstrings, after.docstrings)}",
        ]
    )
