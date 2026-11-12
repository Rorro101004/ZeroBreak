"""Tests unitarios de ``zerobreak.backup``."""

from zerobreak import backup, cases


def test_legacy_path_is_sibling_with_suffix(tmp_path):
    module = tmp_path / "tienda.py"
    assert backup.legacy_path(module) == tmp_path / "tienda_legacy_anotado.py"


def test_ensure_backup_creates_file_with_original_body(project):
    case = cases.resolve_case(project, "sample")
    target, created = backup.ensure_backup(case.path / "calc.py")
    assert created is True
    assert target.name == "calc_legacy_anotado.py"
    content = target.read_text(encoding="utf-8")
    assert "RESPALDO DIDÁCTICO" in content
    assert "class Calc:" in content


def test_ensure_backup_is_idempotent(project):
    case = cases.resolve_case(project, "sample")
    module = case.path / "calc.py"
    first, _ = backup.ensure_backup(module)
    first.write_text("MANUAL\n", encoding="utf-8")
    second, created = backup.ensure_backup(module)
    assert created is False
    assert second.read_text(encoding="utf-8") == "MANUAL\n"
