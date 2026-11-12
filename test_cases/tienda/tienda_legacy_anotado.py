# ============================================================================
# RESPALDO DIDÁCTICO — Código original de `tienda.py` (pre-refactor)
# ----------------------------------------------------------------------------
# Conserva el código original ÍNTEGRO, sin cambios funcionales. Los comentarios
# añadidos explican cada code smell, por qué penaliza y cómo se resolvió en la
# versión refactorizada. NO es código de producción ni un test.
# ============================================================================

# Logica de una tienda online. Version sin optimizar (objetivo de refactorizacion).

class CarritoCompras:
    def __init__(self):
        self.productos = []
        # SMELL (tipado): lista sin anotar; se pierde la información de tipo.
        # Solución: self.productos: list[Producto] = []  (PEP 585/589).

    def agregar_producto(self, nombre, precio, categoria):
        # SMELL (tipado/docstrings): sin anotaciones PEP 484/604 ni docstring,
        # lo que dificulta el uso y el análisis estático.
        # Solución: firma (nombre: str, precio: float, categoria: str) -> None
        # más docstring Google Style.
        producto = {"nombre": nombre, "precio": precio, "categoria": categoria}
        self.productos.append(producto)

    def obtener_total_por_categoria(self, categoria):
        # SMELL (idiomático): acumulación manual con bucle en lugar de sum().
        # Es O(n) pero verboso y más propenso a errores que un generador.
        # Solución: return sum(p["precio"] for p in self.productos
        #                      if p["categoria"] == categoria).
        total = 0
        for producto in self.productos:
            if producto["categoria"] == categoria:
                total = total + producto["precio"]
        return total

    def buscar_productos_duplicados(self):
        # SMELL (rendimiento, O(n²)): `nombres.count(x)` recorre la lista
        # completa en CADA iteración, y el `not in duplicados` añade otro
        # recorrido; el coste crece de forma cuadrática con el número de items.
        # Solución: collections.Counter en UNA sola pasada (O(n)):
        #   conteo = Counter(p["nombre"] for p in self.productos)
        #   return [n for n, c in conteo.items() if c > 1]
        nombres = []
        for producto in self.productos:
            nombres.append(producto["nombre"])
        duplicados = []
        for i in range(len(nombres)):
            if nombres.count(nombres[i]) > 1:
                if nombres[i] not in duplicados:
                    duplicados.append(nombres[i])
        return duplicados

    def generar_recibo_texto(self):
        # SMELL (idiomático/portabilidad): concatenar con `+=` dentro del bucle
        # es O(n²) en el caso general (cada paso copia la cadena acumulada). En
        # CPython existe una optimización in-place que lo mitiga, así que la
        # mejora medida es pequeña; aun así "".join(...) es lo idiomático y
        # GARANTIZA coste lineal en cualquier implementación, además de evitar
        # el segundo recorrido usado para calcular el total.
        # Solución: acumular líneas en una lista y unirlas con "".join(...),
        # calculando el total con sum(...) en una sola expresión.
        texto = "RECIBO\n"
        for producto in self.productos:
            texto += "- " + producto["nombre"] + ": $" + f"{producto['precio']:.2f}" + " (" + producto["categoria"] + ")\n"
        total = 0
        for producto in self.productos:
            total = total + producto["precio"]
        texto += "TOTAL: $" + f"{total:.2f}"
        return texto

    # SMELL (tipado/docstrings): ningún método tenía anotaciones ni docstrings.
    # Solución global: tipos PEP 484/585/604 y docstrings Google Style en todos.
