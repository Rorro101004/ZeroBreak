"""Tests unitarios de generación de plantillas (scaffolding)."""

from pathlib import Path

import pytest

from zerobreak import runner, scaffold


def test_create_case_generates_files_and_passes_pytest(tmp_path: Path):
    (tmp_path / "test_cases").mkdir()
    result = scaffold.create_case(tmp_path, "usuarios")
    assert result.case_dir == tmp_path / "test_cases" / "usuarios"
    assert result.module_path.is_file()
    assert result.test_path.is_file()
    assert result.proposal_path.is_file()

    run = runner.run_pytest(tmp_path, result.case_dir)
    assert run.ok is True


@pytest.mark.parametrize("bad_name", ["123invalido", "con-guion", "_privado", "test_algo"])
def test_create_case_rejects_invalid_names(tmp_path: Path, bad_name: str):
    with pytest.raises(ValueError, match="inválido"):
        scaffold.create_case(tmp_path, bad_name)


def test_create_case_rejects_existing_case(project: Path):
    with pytest.raises(FileExistsError, match="ya existe"):
        scaffold.create_case(project, "sample")
