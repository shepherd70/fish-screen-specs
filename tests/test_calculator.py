"""Tests for the fish-screen spec calculator."""

import math

import pytest

from fish_screen.calculator import calculate_screen_spec
from fish_screen.dfo import max_opening_mm


def test_effective_area_still_water():
    # Q / v_max = 0.035 / 0.035 = 1.0 m^2 at the Table C-1 limit
    spec = calculate_screen_spec(flow_m3s=0.035, scenario="still_water")
    assert math.isclose(spec.effective_area_m2, 1.0, rel_tol=1e-9)
    assert math.isclose(spec.max_approach_velocity_mps, 0.035, rel_tol=1e-9)


def test_gross_area_applies_open_ratio_and_blockage():
    spec = calculate_screen_spec(
        flow_m3s=0.035, scenario="still_water",
        open_area_ratio=0.5, blockage_allowance=0.0,
    )
    # effective 1.0 / 0.5 / (1 - 0) = 2.0
    assert math.isclose(spec.gross_area_m2, 2.0, rel_tol=1e-9)


def test_sweeping_credit_uses_elevated_velocity():
    still = calculate_screen_spec(flow_m3s=0.1, scenario="still_water")
    swept = calculate_screen_spec(flow_m3s=0.1, scenario="sweeping_credit")
    assert math.isclose(swept.max_approach_velocity_mps, 0.12, rel_tol=1e-9)
    assert swept.effective_area_m2 < still.effective_area_m2


def test_opening_size_default_and_sensitive():
    assert math.isclose(max_opening_mm(False), 2.54, rel_tol=1e-9)
    assert math.isclose(max_opening_mm(True), 1.0, rel_tol=1e-9)
    spec = calculate_screen_spec(flow_m3s=0.05, sensitive_species=True)
    assert math.isclose(spec.max_opening_mm, 1.0, rel_tol=1e-9)


def test_min_open_area_flag():
    ok = calculate_screen_spec(flow_m3s=0.05, open_area_ratio=0.5)
    low = calculate_screen_spec(flow_m3s=0.05, open_area_ratio=0.4)
    assert ok.meets_min_open_area
    assert not low.meets_min_open_area


def test_invalid_flow_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.0)


def test_invalid_scenario_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.05, scenario="fry")


def test_invalid_open_area_ratio_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.05, open_area_ratio=1.5)
