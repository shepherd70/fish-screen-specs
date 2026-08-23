"""Tests for CSV batch mode."""

import json
import math
import textwrap

import pytest

from fish_screen.batch import run_batch
from fish_screen.cli import main


def write_csv(tmp_path, content):
    path = tmp_path / "intakes.csv"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(path)


GOOD_CSV = """\
    name,flow_m3s,flow_cfs,water_type,sweeping_velocity_mps,sensitive_species,proposed_opening_mm
    pond,0.05,,waterbody,,no,2.54
    river,,1.5,watercourse,0.24,yes,3.0
    """


def test_run_batch_computes_each_row(tmp_path):
    results = run_batch(write_csv(tmp_path, GOOD_CSV))
    assert [r.name for r in results] == ["pond", "river"]
    pond, river = results
    assert pond.error is None and river.error is None
    assert math.isclose(pond.spec.design_approach_velocity_mps, 0.035)
    assert pond.spec.opening_compliant is True
    assert river.imperial is True
    assert math.isclose(river.spec.design_approach_velocity_mps, 0.12)
    assert river.spec.opening_compliant is False  # 3.0 mm vs 1 mm sensitive


def test_row_errors_are_isolated(tmp_path):
    path = write_csv(tmp_path, """\
        name,flow_m3s,water_type
        good,0.05,waterbody
        bad,,waterbody
        also-bad,0.05,lagoon
        """)
    results = run_batch(path)
    assert results[0].error is None
    assert "flow_m3s or flow_cfs" in results[1].error
    assert "lagoon" in results[2].error


def test_unknown_column_rejected(tmp_path):
    path = write_csv(tmp_path, """\
        name,flow_m3s,sweeping_velocity
        x,0.05,0.2
        """)
    with pytest.raises(ValueError, match="sweeping_velocity"):
        run_batch(path)


def test_cli_batch_table_and_exit_codes(tmp_path, capsys):
    rc = main(["--batch", write_csv(tmp_path, GOOD_CSV)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "pond" in out and "PASS" in out and "FAIL" in out


def test_cli_batch_json(tmp_path, capsys):
    rc = main(["--batch", write_csv(tmp_path, GOOD_CSV), "--json"])
    assert rc == 0
    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["name"] == "pond"
    assert math.isclose(rows[1]["flow_cfs"], 1.5)
    assert "effective_area_ft2" in rows[1]


def test_cli_batch_failure_exit_code(tmp_path, capsys):
    path = write_csv(tmp_path, """\
        name,flow_m3s
        bad,-1
        """)
    rc = main(["--batch", path])
    assert rc == 2
    assert "ERROR" in capsys.readouterr().out


GEO_CSV = """\
    name,flow_m3s,geometry,dim_D,dim_L,dim_W1,dim_W2,solve_for,units
    solve-cyl,0.05,cylinder,0.3,,,,L,2
    check-panel,0.05,panel,,,0.5,0.5,,
    no-geo,0.05,,,,,,,
    """


def test_batch_geometry_solve_and_check(tmp_path):
    results = run_batch(write_csv(tmp_path, GEO_CSV))
    solve, check, plain = results
    assert solve.error is None
    assert solve.geo.mode == "solve" and solve.geo.units == 2
    assert solve.geo.solved_key == "L" and solve.geo.area_sufficient
    assert check.geo.mode == "check"
    assert not check.geo.area_sufficient  # 0.25 m^2 << required gross
    assert plain.geo is None


def test_batch_geometry_row_errors_are_isolated(tmp_path):
    path = write_csv(tmp_path, """\
        name,flow_m3s,geometry,dim_D,solve_for,units
        bad-shape,0.05,sphere,0.3,,
        bad-units,0.05,cylinder,0.3,L,two
        orphan-dim,0.05,,0.3,,
        good,0.05,cylinder,0.3,L,
        """)
    results = run_batch(path)
    assert "Unknown geometry" in results[0].error
    assert "not an integer" in results[1].error
    assert "require a geometry" in results[2].error
    assert results[3].error is None and results[3].geo is not None


def test_cli_batch_geometry_table_and_json(tmp_path, capsys):
    path = write_csv(tmp_path, GEO_CSV)
    rc = main(["--batch", path])
    out = capsys.readouterr().out
    assert rc == 0
    assert "geometry" in out  # header column
    assert "cylinder ×2 L=" in out
    assert "panel" in out and "FAIL" in out
    rc = main(["--batch", path, "--json"])
    assert rc == 0
    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["geometry"]["solved_key"] == "L"
    assert rows[1]["geometry"]["area_sufficient"] is False
    assert "geometry" not in rows[2]


def test_cli_batch_missing_file(capsys):
    rc = main(["--batch", "/nonexistent/intakes.csv"])
    assert rc == 2
    assert "error:" in capsys.readouterr().out
