import pytest

from inventario import Inventario


@pytest.fixture
def inv():
    i = Inventario()
    i.agregar("tornillo", 10)
    i.agregar("tuerca", 5)
    i.agregar("tornillo", 2)
    return i


def test_buscar_existente(inv):
    assert inv.buscar("tornillo") == 10


def test_buscar_inexistente(inv):
    assert inv.buscar("clavo") == 0


def test_total(inv):
    assert inv.total() == 17


def test_duplicados(inv):
    assert inv.nombres_duplicados() == ["tornillo"]


def test_resumen(inv):
    assert inv.resumen_texto() == "tornillo x10\ntuerca x5\ntornillo x2\n"


def test_vacio():
    i = Inventario()
    assert i.total() == 0
    assert i.nombres_duplicados() == []
    assert i.resumen_texto() == ""
