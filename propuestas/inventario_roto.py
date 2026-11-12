# Versión ROTA a propósito: sirve para ver el rollback automático en vivo.

class Inventario:
    def __init__(self):
        self.items = []

    def agregar(self, nombre, cantidad):
        self.items.append({"nombre": nombre, "cantidad": cantidad})

    def buscar(self, nombre):
        for item in self.items:
            if item["nombre"] == nombre:
                return item["cantidad"]
        return 0

    def total(self):
        return 0  # ROTO: test_total fallará

    def nombres_duplicados(self):
        return []  # ROTO: test_duplicados fallará

    def resumen_texto(self):
        return ""  # ROTO: test_resumen fallará
