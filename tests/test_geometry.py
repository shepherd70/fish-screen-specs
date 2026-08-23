"""Tests for screen geometries (Figure 2, §3.7)."""

import json
import math

import pytest

from fish_screen.cli import main
from fish_screen.geometry import BUILD_INCREMENT_M, GEOMETRIES, size_screen

REFERENCE_DIMS = {
    "disc": {"D": 0.6},
    "panel": {"W1": 0.5, "W2": 0.8},
    "box": {"L": 1.2, "W1": 0.5, "W2": 0.4},
    "cylinder": {"D": 0.3, "L": 1.0},
    "cone": {"r": 0.3, "L": 0.9},
    "halfbarrel": {"D": 0.4, "L": 1.1},
}


def test_area_formulas_match_figure_2():
    assert math.isclose(
        GEOMETRIES["disc"].area({"D": 0.6}), math.pi / 4 * 0.36
    )
    assert math.isclose(GEOMETRIES["panel"].area({"W1": 0.5, "W2": 0.8}), 0.4)
    assert math.isclose(
        GEOMETRIES["box"].area({"L": 1.2, "W1": 0.5, "W2": 0.4}),
        2 * 1.2 * 0.9,
    )
    assert math.isclose(
        GEOMETRIES["cylinder"].area({"D": 0.3, "L": 1.0}), math.pi * 0.3
    )
    assert math.isclose(
        GEOMETRIES["cone"].area({"r": 0.3, "L": 0.9}), math.pi * 0.27
    )
    assert math.isclose(
        GEOMETRIES["halfbarrel"].area({"D": 0.4, "L": 1.1}),
        0.5 * math.pi * 0.44,
    )


@pytest.mark.parametrize("key", sorted(GEOMETRIES))
def test_solve_round_trips_every_dimension(key):
    geo = GEOMETRIES[key]
    dims = REFERENCE_DIMS[key]
    area = geo.area(dims)
    for dim_key in geo.dim_keys:
        others = {k: v for k, v in dims.items() if k != dim_key}
        solved = geo.solve(dim_key, area, others)
        assert math.isclose(solved, dims[dim_key]), (key, dim_key)


def test_solved_dimension_rounds_up_to_build_increment():
    result = size_screen(1.0, "cylinder", {"D": 0.3}, solve_for="L")
    exact = 1.0 / (math.pi * 0.3)
    assert result.solved_raw_m == pytest.approx(exact)
    assert result.dims["L"] >= exact
    assert result.dims["L"] - exact < BUILD_INCREMENT_M
    assert result.area_sufficient
    # rounded value re-checks as sufficient
    recheck = size_screen(1.0, "cylinder", dict(result.dims))
    assert recheck.area_sufficient


def test_units_split_the_required_area():
    one = size_screen(2.0, "cylinder", {"D": 0.3}, solve_for="L", units=1)
    two = size_screen(2.0, "cylinder", {"D": 0.3}, solve_for="L", units=2)
    assert two.dims["L"] == pytest.approx(one.dims["L"] / 2, abs=1e-3)
    assert two.gross_area_total_m2 >= 2.0


def test_check_mode_pass_and_fail():
    ok = size_screen(0.9, "cylinder", {"D": 0.3, "L": 1.0})
    small = size_screen(1.0, "cylinder", {"D": 0.3, "L": 1.0})
    assert ok.mode == "check" and ok.area_sufficient
    assert math.isclose(small.gross_area_total_m2, math.pi * 0.3)
    assert not small.area_sufficient


def test_impossible_solve_raises():
    # box W1 = A/(2L) - W2 goes negative for a huge fixed W2
    with pytest.raises(ValueError, match="Cannot solve"):
        size_screen(0.1, "box", {"L": 1.0, "W2": 5.0}, solve_for="W1")


def test_missing_and_invalid_inputs_raise():
    with pytest.raises(ValueError, match="Missing dimension"):
        size_screen(1.0, "cylinder", {"D": 0.3})
    with pytest.raises(ValueError, match="Unknown geometry"):
        size_screen(1.0, "sphere", {"D": 0.3})
    with pytest.raises(ValueError, match="Cannot solve for"):
        size_screen(1.0, "cylinder", {"D": 0.3}, solve_for="W1")
    with pytest.raises(ValueError, match="units"):
        size_screen(1.0, "cylinder", {"D": 0.3, "L": 1.0}, units=0)


def test_cli_solve_reports_dimension(capsys):
    rc = main(["--flow", "0.05", "--geometry", "cylinder",
               "--dim", "D=0.3", "--solve-for", "L"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Solved L:" in out and "PASS" in out


def test_cli_check_fail(capsys):
    rc = main(["--flow", "0.05", "--geometry", "panel",
               "--dim", "W1=0.5", "--dim", "W2=0.5"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "FAIL" in out  # 0.25 m^2 << required gross area


def test_cli_json_includes_geometry(capsys):
    rc = main(["--flow", "0.05", "--geometry", "cylinder",
               "--dim", "D=0.3", "--solve-for", "L", "--units", "2",
               "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    geo = out["geometry"]
    assert geo["mode"] == "solve" and geo["units"] == 2
    assert geo["area_sufficient"] is True


def test_cli_geometry_flag_errors(capsys):
    assert main(["--flow", "0.05", "--dim", "D=0.3"]) == 2
    assert "require --geometry" in capsys.readouterr().out
    assert main(["--flow", "0.05", "--geometry", "cylinder",
                 "--dim", "D=x", "--solve-for", "L"]) == 2
    assert "not a number" in capsys.readouterr().out
    assert main(["--batch", "whatever.csv", "--geometry", "cylinder"]) == 2
    assert "not supported" in capsys.readouterr().out
