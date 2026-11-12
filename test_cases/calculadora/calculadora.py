"""Calculadora de operaciones aritméticas básicas."""


class Calculadora:
    """Calculadora sin estado con las cuatro operaciones básicas."""

    def sumar(self, a: int | float, b: int | float) -> int | float:
        """Suma dos números.

        Args:
            a: Primer operando.
            b: Segundo operando.

        Returns:
            La suma de ``a`` y ``b``.
        """
        return a + b

    def restar(self, a: int | float, b: int | float) -> int | float:
        """Resta ``b`` a ``a``.

        Args:
            a: Minuendo.
            b: Sustraendo.

        Returns:
            La diferencia de ``a`` menos ``b``.
        """
        return a - b

    def multiplicar(self, a: int | float, b: int | float) -> int | float:
        """Multiplica dos números.

        Args:
            a: Primer factor.
            b: Segundo factor.

        Returns:
            El producto de ``a`` por ``b``.
        """
        return a * b

    def dividir(self, a: int | float, b: int | float) -> float:
        """Divide ``a`` entre ``b``.

        Args:
            a: Dividendo.
            b: Divisor.

        Returns:
            El cociente de ``a`` entre ``b``.

        Raises:
            ValueError: Si ``b`` es cero.
        """
        if b == 0:
            raise ValueError("No se puede dividir por cero")
        return a / b
