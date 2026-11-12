"""Escenarios de rendimiento del caso 'tienda' (no es un test ni producción).

``zerobreak bench tienda`` llama a ``escenarios`` dos veces: una con el
módulo legacy (``tienda_legacy_anotado.py``) y otra con el actual
(``tienda.py``), y mide cada invocable devuelto.
"""


def _carrito(modulo, n):
    carrito = modulo.CarritoCompras()
    for i in range(n):
        carrito.agregar_producto(f"producto-{i % 50}", 1.5, "general")
    return carrito


def escenarios(modulo):
    """Devuelve ``{nombre: invocable_sin_argumentos}`` a medir."""
    grande = _carrito(modulo, 2000)
    return {
        "buscar_productos_duplicados (n=2000)": grande.buscar_productos_duplicados,
        "generar_recibo_texto (n=2000)": grande.generar_recibo_texto,
    }
