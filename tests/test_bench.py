"""Tests unitarios del benchmark legacy vs actual (``zerobreak.bench``)."""

from pathlib import Path

import pytest

from zerobreak import bench, cases, cli

LEGACY = "def total(datos):\n    t = 0\n    for x in datos:\n        t = t + x\n    return t\n"
CURRENT = "def total(datos):\n    return sum(datos)\n"
SCENARIOS = (
    "def escenarios(modulo):\n"
    "    datos = list(range(100))\n"
    "    return {'total (n=100)': lambda: modulo.total(datos)}\n"
)


def _bench_case(tmp_path: Path, scenarios: str | None = SCENARIOS, legacy: bool = True):
    case_dir = tmp_path / "test_cases" / "suma"
    case_dir.mkdir(parents=True)
    (case_dir / "suma.py").write_text(CURRENT, encoding="utf-8")
    (case_dir / "test_suma.py").write_text(
        "from suma import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n",
        encoding="utf-8",
    )
    if legacy:
        (case_dir / "suma_legacy_anotado.py").write_text(LEGACY, encoding="utf-8")
    if scenarios is not None:
        (case_dir / "bench_suma.py").write_text(scenarios, encoding="utf-8")
    case = cases.resolve_case(tmp_path, "suma")
    return case, case_dir / "suma.py"


def test_bench_file_is_not_a_module(tmp_path):
    case, _ = _bench_case(tmp_path)
    assert [module.name for module in case.modules] == ["suma.py"]


def test_run_bench_measures_each_scenario(tmp_path):
    case, module = _bench_case(tmp_path)
    rows = bench.run_bench(case, module, number=5)
    assert [row.name for row in rows] == ["total (n=100)"]
    assert rows[0].legacy > 0 and rows[0].current > 0


def test_run_bench_without_scenarios_file(tmp_path):
    case, module = _bench_case(tmp_path, scenarios=None)
    with pytest.raises(FileNotFoundError, match="bench_suma.py"):
        bench.run_bench(case, module, number=1)


def test_run_bench_without_legacy(tmp_path):
    case, module = _bench_case(tmp_path, legacy=False)
    with pytest.raises(FileNotFoundError, match="respaldo"):
        bench.run_bench(case, module, number=1)


def test_run_bench_without_escenarios_function(tmp_path):
    case, module = _bench_case(tmp_path, scenarios="x = 1\n")
    with pytest.raises(ValueError, match="escenarios"):
        bench.run_bench(case, module, number=1)


def test_load_module_rejects_non_python(tmp_path):
    path = tmp_path / "datos.txt"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(ImportError):
        bench.load_module(path, "_cc_txt")


def test_best_time_autorange_calibrates():
    assert bench.best_time(lambda: None, repeats=1) > 0


def test_speedup_handles_zero_current():
    assert bench.BenchRow("x", 1.0, 0.0).speedup == float("inf")


def test_format_report_faster_slower_and_empty():
    report = bench.format_report(
        [bench.BenchRow("rapido", 0.010, 0.001), bench.BenchRow("lento", 0.001, 0.002)]
    )
    assert "10.0× más rápido" in report
    assert "0.50×, más lento" in report
    assert "Sin escenarios" in bench.format_report([])


def test_cli_bench_prints_report(tmp_path, capsys):
    _bench_case(tmp_path)
    code = cli.main(["bench", "suma", "--number", "5", "--root", str(tmp_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Benchmark (legacy -> actual)" in out
    assert "total (n=100)" in out


def test_cli_bench_missing_scenarios_returns_1(tmp_path, capsys):
    _bench_case(tmp_path, scenarios=None)
    assert cli.main(["bench", "suma", "--root", str(tmp_path)]) == 1
    assert "Error" in capsys.readouterr().out
