# ============================================================================
# RESPALDO DIDÁCTICO — Código original de `calculadora.py` (pre-refactor)
# ----------------------------------------------------------------------------
# Conserva el código original ÍNTEGRO, sin cambios funcionales. Los comentarios
# añadidos explican cada code smell, por qué penaliza y cómo se resolvió en la
# versión refactorizada. NO es código de producción ni un test.
# ============================================================================

class CalculadoraLenta:
    # SMELL global (tipado/docstrings): ni la clase ni sus métodos tenían
    # anotaciones PEP 484/604 ni docstrings, lo que dificultaba el uso y el
    # análisis estático.
    # Solución: docstrings Google Style + tipos (int | float) en todos ellos.
    def sumar(self, a, b):
        # SMELL (tipado): parámetros y retorno sin anotar.
        # Solución: def sumar(self, a: int | float, b: int | float) -> int | float.
        return a + b

    def restar(self, a, b):
        # SMELL (tipado): parámetros y retorno sin anotar.
        # Solución: def restar(self, a: int | float, b: int | float) -> int | float.
        return a - b

    def multiplicar(self, a, b):
        # SMELL (tipado): parámetros y retorno sin anotar.
        # Solución: def multiplicar(self, a: int | float, b: int | float) -> int | float.
        return a * b

    def dividir(self, a, b):
        # SMELL (tipado): parámetros y retorno sin anotar; además el retorno
        # real de la división es siempre float, dato que se perdía.
        # Solución: def dividir(self, a: int | float, b: int | float) -> float,
        # documentando el ValueError en el docstring.
        if b == 0:
            raise ValueError("No se puede dividir por cero")
        return a / b

    # Nota: el nombre original de la clase era `CalculadoraLenta` porque en su
    # primera versión incluía `time.sleep` (de ahí "lenta"). Al eliminarse las
    # esperas, se renombró a `Calculadora` para reflejar su comportamiento real.
