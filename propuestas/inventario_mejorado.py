"""Inventario mejorado: Counter + sum() + join() + tipado."""

from collections import Counter


class Inventario:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def agregar(self, nombre: str, cantidad: int) -> None:
        self.items.append({"nombre": nombre, "cantidad": cantidad})

    def buscar(self, nombre: str) -> int:
        for item in self.items:
            if item["nombre"] == nombre:
                return item["cantidad"]
        return 0

    def total(self) -> int:
        return sum(item["cantidad"] for item in self.items)

    def nombres_duplicados(self) -> list[str]:
        conteo = Counter(item["nombre"] for item in self.items)
        return [nombre for nombre, c in conteo.items() if c > 1]

    def resumen_texto(self) -> str:
        return "".join(f"{item['nombre']} x{item['cantidad']}\n" for item in self.items)
