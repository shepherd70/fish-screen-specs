"""Tests for the fish-screen CLI."""

import json
import math

import pytest

from fish_screen.cli import main
from fish_screen.units import CFS_TO_M3S


def test_json_output_round_trips(capsys):
    rc = main(["--flow", "0.05", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["water_type"] == "waterbody"
    assert math.isclose(out["design_approach_velocity_mps"], 0.035)
    assert out["opening_compliant"] is None
    assert "flow_cfs" not in out  # SI input -> no imperial fields


def test_json_output_imperial_fields(capsys):
    rc = main(["--flow-cfs", "1.0", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert math.isclose(out["flow_m3s"], CFS_TO_M3S)
    assert math.isclose(out["flow_cfs"], 1.0)
    # 1 cfs / 0.035 m/s, expressed in ft^2
    assert math.isclose(
        out["effective_area_ft2"],
        out["effective_area_m2"] * 10.763910416709722,
    )


def test_opening_check_pass_and_fail(capsys):
    main(["--flow", "0.05", "--opening", "2.54"])
    assert "PASS" in capsys.readouterr().out
    main(["--flow", "0.05", "--opening", "3.0"])
    assert "FAIL" in capsys.readouterr().out
    # Sensitive species tightens the limit to 1 mm
    main(["--flow", "0.05", "--opening", "2.0", "--sensitive-species"])
    assert "FAIL" in capsys.readouterr().out


def test_flow_flags_mutually_exclusive(capsys):
    with pytest.raises(SystemExit):
        main(["--flow", "0.05", "--flow-cfs", "1.0"])


def test_invalid_input_exits_2(capsys):
    rc = main(["--flow", "0.05", "--water-type", "waterbody",
               "--sweeping-velocity", "0.2"])
    assert rc == 2
    assert "error:" in capsys.readouterr().out
