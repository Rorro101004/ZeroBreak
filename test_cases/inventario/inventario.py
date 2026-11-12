# Inventario con smells deliberados: búsqueda O(n^2) y concatenación con +=

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
        total = 0
        for item in self.items:
            total = total + item["cantidad"]
        return total

    def nombres_duplicados(self):
        nombres = []
        for item in self.items:
            nombres.append(item["nombre"])
        duplicados = []
        for i in range(len(nombres)):
            if nombres.count(nombres[i]) > 1:
                if nombres[i] not in duplicados:
                    duplicados.append(nombres[i])
        return duplicados

    def resumen_texto(self):
        texto = ""
        for item in self.items:
            texto += item["nombre"] + " x" + str(item["cantidad"]) + "\n"
        return texto
