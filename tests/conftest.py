"""Fixtures compartidas para los tests del framework."""

from pathlib import Path

import pytest


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Crea un proyecto ZeroBreak mínimo en un directorio temporal."""
    case = tmp_path / "test_cases" / "sample"
    case.mkdir(parents=True)
    (case / "calc.py").write_text(
        '"""Módulo de ejemplo."""\n'
        "\n"
        "\n"
        "class Calc:\n"
        "    def add(self, a, b):\n"
        "        return a + b\n",
        encoding="utf-8",
    )
    (case / "test_calc.py").write_text(
        "from calc import Calc\n"
        "\n"
        "\n"
        "def test_add():\n"
        "    assert Calc().add(2, 3) == 5\n",
        encoding="utf-8",
    )
    return tmp_path
