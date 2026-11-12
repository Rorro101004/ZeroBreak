"""Tests unitarios de la verificación determinista de contratos públicos."""

from zerobreak import contracts


def test_extract_signatures_functions_and_classes():
    code = (
        "def publica(a, /, b: int, *args, c: str = 'x', **kwargs) -> int:\n"
        "    return 1\n\n"
        "def _privada(x):\n"
        "    return x\n\n"
        "class _ClasePrivada:\n"
        "    def metodo(self):\n"
        "        pass\n\n"
        "class Caja:\n"
        "    VERSION = 1\n"
        "    def __init__(self, inicial: int = 0) -> None:\n"
        "        self.valor = inicial\n"
        "    def _interno(self) -> None:\n"
        "        pass\n"
        "    async def sumar(self, cantidad: int) -> int:\n"
        "        return self.valor + cantidad\n"
    )
    sigs = contracts.extract_signatures(code)
    assert sigs == {
        "publica": "publica(a, b, *args, c, **kwargs)",
        "Caja": "class Caja",
        "Caja.__init__": "Caja.__init__(self, inicial)",
        "Caja.sumar": "Caja.sumar(self, cantidad)",
    }


def test_check_contracts_allows_types_docstrings_and_new_helpers():
    original = (
        "class Tienda:\n"
        "    def total(self, items):\n"
        "        return sum(items)\n\n"
        "def calcular(x, y):\n"
        "    return x + y\n"
    )
    proposed = (
        '"""Docstring de módulo."""\n\n'
        "def _helper(val: int) -> int:\n"
        "    return val * 2\n\n"
        "def nueva_funcion_publica() -> None:\n"
        "    pass\n\n"
        "class Tienda:\n"
        '    """Docstring de clase."""\n'
        "    def total(self, items: list[int]) -> int:\n"
        "        return sum(items)\n\n"
        "def calcular(x: int, y: int) -> int:\n"
        "    return _helper(x) + y\n"
    )
    assert contracts.check_contracts(original, proposed) == []


def test_check_contracts_detects_removed_symbol():
    original = "def sumar(a, b):\n    return a + b\n"
    proposed = "def adicionar(a, b):\n    return a + b\n"
    violations = contracts.check_contracts(original, proposed)
    assert len(violations) == 1
    assert "eliminado" in violations[0]
    assert "'sumar'" in violations[0]


def test_check_contracts_detects_altered_parameters():
    original = "def sumar(a, b):\n    return a + b\n"
    proposed = "def sumar(x, y):\n    return x + y\n"
    violations = contracts.check_contracts(original, proposed)
    assert len(violations) == 1
    assert "alterada" in violations[0]
    assert "sumar(a, b)" in violations[0]
    assert "sumar(x, y)" in violations[0]


def test_check_contracts_detects_syntax_error():
    original = "def sumar(a, b):\n    return a + b\n"
    proposed = "def sumar(a, b)\n    return a + b\n"
    violations = contracts.check_contracts(original, proposed)
    assert len(violations) == 1
    assert "sintaxis" in violations[0].lower()


def test_inspect_functions_extracts_contracts_and_annotations():
    code = (
        "def procesar(datos: list[int], factor: float = 1.0, *extra: str, **opciones: int) -> int:\n"
        "    return 42\n\n"
        "def simple(x, *args, **kwargs):\n"
        "    pass\n\n"
        "def _ignorado():\n"
        "    pass\n"
    )
    funcs = contracts.inspect_functions(code)
    assert len(funcs) == 2
    fn = funcs[0]
    assert fn.name == "procesar"
    assert fn.params == ["datos", "factor", "*extra", "**opciones"]
    assert fn.annotations["datos"] == "list[int]"
    assert fn.annotations["factor"] == "float"
    assert fn.annotations["extra"] == "str"
    assert fn.annotations["opciones"] == "int"
    assert fn.return_annotation == "int"

    fn2 = funcs[1]
    assert fn2.name == "simple"
    assert fn2.params == ["x", "*args", "**kwargs"]
    assert fn2.annotations == {}
    assert fn2.return_annotation is None


