import pytest

from calculadora import Calculadora


@pytest.fixture
def calc():
    return Calculadora()


def test_sumar(calc):
    assert calc.sumar(2, 3) == 5


def test_restar(calc):
    assert calc.restar(8, 3) == 5


def test_multiplicar(calc):
    assert calc.multiplicar(10, 3) == 30


def test_dividir_por_cero(calc):
    with pytest.raises(ValueError):
        calc.dividir(10, 0)


def test_dividir(calc):
    assert calc.dividir(20, 4) == 5
