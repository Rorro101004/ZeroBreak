import pytest

from tienda import CarritoCompras


@pytest.fixture
def vacio():
    return CarritoCompras()


@pytest.fixture
def lleno():
    carrito = CarritoCompras()
    carrito.agregar_producto("Manzana", 1.50, "fruta")
    carrito.agregar_producto("Pera", 2.25, "fruta")
    carrito.agregar_producto("Pan", 2.00, "panaderia")
    carrito.agregar_producto("Leche", 1.10, "lacteos")
    carrito.agregar_producto("Manzana", 1.50, "fruta")
    return carrito


def test_total_por_categoria_fruta(lleno):
    assert lleno.obtener_total_por_categoria("fruta") == pytest.approx(5.25)


def test_total_por_categoria_panaderia(lleno):
    assert lleno.obtener_total_por_categoria("panaderia") == pytest.approx(2.00)


def test_total_por_categoria_lacteos(lleno):
    assert lleno.obtener_total_por_categoria("lacteos") == pytest.approx(1.10)


def test_total_por_categoria_inexistente(lleno):
    assert lleno.obtener_total_por_categoria("bebidas") == 0


def test_total_por_categoria_carrito_vacio(vacio):
    assert vacio.obtener_total_por_categoria("fruta") == 0


def test_sin_duplicados_carrito_vacio(vacio):
    assert vacio.buscar_productos_duplicados() == []


def test_sin_duplicados_cuando_todos_son_unicos():
    carrito = CarritoCompras()
    carrito.agregar_producto("Pan", 2.00, "panaderia")
    carrito.agregar_producto("Leche", 1.10, "lacteos")
    assert carrito.buscar_productos_duplicados() == []


def test_un_producto_duplicado(lleno):
    assert lleno.buscar_productos_duplicados() == ["Manzana"]


def test_multiples_duplicados():
    carrito = CarritoCompras()
    carrito.agregar_producto("Pan", 2.00, "panaderia")
    carrito.agregar_producto("Leche", 1.10, "lacteos")
    carrito.agregar_producto("Pan", 2.00, "panaderia")
    carrito.agregar_producto("Leche", 1.10, "lacteos")
    carrito.agregar_producto("Huevos", 3.00, "lacteos")
    assert carrito.buscar_productos_duplicados() == ["Pan", "Leche"]


def test_recibo_carrito_vacio(vacio):
    assert vacio.generar_recibo_texto() == "RECIBO\nTOTAL: $0.00"


def test_recibo_un_producto():
    carrito = CarritoCompras()
    carrito.agregar_producto("Cafe", 3.50, "bebidas")
    assert carrito.generar_recibo_texto() == "RECIBO\n- Cafe: $3.50 (bebidas)\nTOTAL: $3.50"


def test_recibo_varios_productos(lleno):
    esperado = (
        "RECIBO\n"
        "- Manzana: $1.50 (fruta)\n"
        "- Pera: $2.25 (fruta)\n"
        "- Pan: $2.00 (panaderia)\n"
        "- Leche: $1.10 (lacteos)\n"
        "- Manzana: $1.50 (fruta)\n"
        "TOTAL: $8.35"
    )
    assert lleno.generar_recibo_texto() == esperado


def test_recibo_incluye_producto_recien_agregado(vacio):
    vacio.agregar_producto("Agua", 0.90, "bebidas")
    texto = vacio.generar_recibo_texto()
    assert "Agua" in texto
    assert "TOTAL: $0.90" in texto
