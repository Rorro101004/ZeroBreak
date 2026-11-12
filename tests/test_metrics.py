"""Tests unitarios de las métricas comparativas de refactorización."""

from zerobreak import metrics

BEFORE_CODE = (
    "# Comentario inicial\n"
    "\n"
    "def sumar(datos):\n"
    "    total = 0\n"
    "    for x in datos:\n"
    "        total = total + x\n"
    "    return total\n"
)

AFTER_CODE = (
    '"""Módulo optimizado."""\n'
    "\n"
    "def sumar(datos: list[int]) -> int:\n"
    '    """Suma los elementos."""\n'
    "    return sum(datos)\n"
)


def test_analyze_counts_sloc_types_and_docstrings():
    before = metrics.analyze(BEFORE_CODE)
    assert before == metrics.CodeMetrics(
        sloc=5,
        public_symbols=1,
        typed_functions=0,
        total_functions=1,
        docstrings=0,
    )

    after = metrics.analyze(AFTER_CODE)
    assert after == metrics.CodeMetrics(
        sloc=4,
        public_symbols=1,
        typed_functions=1,
        total_functions=1,
        docstrings=2,
    )


def test_format_comparison_renders_deltas():
    summary = metrics.format_comparison(BEFORE_CODE, AFTER_CODE)
    assert "Resumen de métricas" in summary
    assert "5 -> 4 (-1)" in summary
    assert "1 -> 1" in summary
    assert "0/1 -> 1/1" in summary
    assert "0 -> 2 (+2)" in summary
