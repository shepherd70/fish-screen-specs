"""Tests for the fish-screen spec calculator."""

import math

import pytest

from fish_screen.calculator import calculate_screen_spec


def test_effective_area_fry():
    # Q / v_max = 0.038 / 0.038 = 1.0 m^2
    spec = calculate_screen_spec(flow_m3s=0.038, life_stage="fry")
    assert math.isclose(spec.effective_area_m2, 1.0, rel_tol=1e-9)


def test_gross_area_applies_open_ratio_and_blockage():
    spec = calculate_screen_spec(
        flow_m3s=0.038, life_stage="fry",
        open_area_ratio=0.5, blockage_allowance=0.0,
    )
    # effective 1.0 / 0.5 / (1 - 0) = 2.0
    assert math.isclose(spec.gross_area_m2, 2.0, rel_tol=1e-9)


def test_no_fry_uses_higher_velocity():
    fry = calculate_screen_spec(flow_m3s=0.1, life_stage="fry")
    no_fry = calculate_screen_spec(flow_m3s=0.1, life_stage="no_fry")
    assert no_fry.effective_area_m2 < fry.effective_area_m2


def test_invalid_flow_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.0)


def test_invalid_life_stage_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.05, life_stage="smolt")


def test_invalid_open_area_ratio_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.05, open_area_ratio=1.5)
