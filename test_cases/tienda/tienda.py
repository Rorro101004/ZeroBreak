"""Lógica de una tienda online basada en un carrito de compras."""

from collections import Counter
from typing import TypedDict


class Producto(TypedDict):
    """Representa un producto dentro del carrito."""

    nombre: str
    precio: float
    categoria: str


class CarritoCompras:
    """Carrito de compras que calcula sus totales bajo demanda."""

    def __init__(self) -> None:
        self.productos: list[Producto] = []

    def agregar_producto(self, nombre: str, precio: float, categoria: str) -> None:
        """Añade un producto al carrito.

        Args:
            nombre: Nombre del producto.
            precio: Precio unitario.
            categoria: Categoría a la que pertenece.
        """
        self.productos.append({"nombre": nombre, "precio": precio, "categoria": categoria})

    def obtener_total_por_categoria(self, categoria: str) -> float:
        """Suma los precios de los productos de una categoría.

        Args:
            categoria: Categoría a totalizar.

        Returns:
            El total acumulado; ``0`` si no hay productos de esa categoría.
        """
        return sum(
            producto["precio"]
            for producto in self.productos
            if producto["categoria"] == categoria
        )

    def buscar_productos_duplicados(self) -> list[str]:
        """Devuelve los nombres de productos repetidos.

        Returns:
            Nombres con más de una aparición, en orden de primera aparición.
        """
        conteo = Counter(producto["nombre"] for producto in self.productos)
        return [nombre for nombre, cantidad in conteo.items() if cantidad > 1]

    def generar_recibo_texto(self) -> str:
        """Genera el recibo del carrito en texto plano.

        Returns:
            Un recibo con una línea por producto y el total al final.
        """
        lineas = ["RECIBO\n"]
        lineas.extend(
            f"- {producto['nombre']}: ${producto['precio']:.2f} ({producto['categoria']})\n"
            for producto in self.productos
        )
        total = sum(producto["precio"] for producto in self.productos)
        lineas.append(f"TOTAL: ${total:.2f}")
        return "".join(lineas)
