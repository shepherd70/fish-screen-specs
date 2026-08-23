"""Tests for the fish-screen spec calculator."""

import math

import pytest

from fish_screen.calculator import calculate_screen_spec
from fish_screen.dfo import design_approach_velocity_mps, max_opening_mm


def test_effective_area_waterbody():
    # Q / v_max = 0.035 / 0.035 = 1.0 m^2 at the Table C-1 limit
    spec = calculate_screen_spec(flow_m3s=0.035, water_type="waterbody")
    assert math.isclose(spec.effective_area_m2, 1.0, rel_tol=1e-9)
    assert math.isclose(spec.design_approach_velocity_mps, 0.035, rel_tol=1e-9)


def test_gross_area_applies_open_ratio_and_blockage():
    spec = calculate_screen_spec(
        flow_m3s=0.035, water_type="waterbody",
        open_area_ratio=0.5, blockage_allowance=0.0,
    )
    # effective 1.0 / 0.5 / (1 - 0) = 2.0
    assert math.isclose(spec.gross_area_m2, 2.0, rel_tol=1e-9)


def test_sweeping_credit_is_half_sweeping_capped():
    # Standard's worked example: 0.24 m/s sweeping -> up to 0.12 m/s approach
    assert math.isclose(
        design_approach_velocity_mps("watercourse", 0.24), 0.12, rel_tol=1e-9
    )
    # Above the cap it stays at 0.12
    assert math.isclose(
        design_approach_velocity_mps("watercourse", 0.40), 0.12, rel_tol=1e-9
    )
    # Between: 50% of sweeping velocity
    assert math.isclose(
        design_approach_velocity_mps("watercourse", 0.10), 0.05, rel_tol=1e-9
    )
    # Low sweeping never drops the limit below the 0.035 default
    assert math.isclose(
        design_approach_velocity_mps("watercourse", 0.05), 0.035, rel_tol=1e-9
    )


def test_watercourse_without_sweeping_data_uses_default():
    spec = calculate_screen_spec(flow_m3s=0.1, water_type="watercourse")
    assert math.isclose(spec.design_approach_velocity_mps, 0.035, rel_tol=1e-9)


def test_sweeping_credit_shrinks_required_area():
    still = calculate_screen_spec(flow_m3s=0.1, water_type="waterbody")
    swept = calculate_screen_spec(
        flow_m3s=0.1, water_type="watercourse", sweeping_velocity_mps=0.24
    )
    assert swept.effective_area_m2 < still.effective_area_m2


def test_sweeping_velocity_rejected_for_waterbody():
    with pytest.raises(ValueError):
        calculate_screen_spec(
            flow_m3s=0.1, water_type="waterbody", sweeping_velocity_mps=0.24
        )


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


def test_invalid_water_type_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.05, water_type="fry")


def test_invalid_sweeping_velocity_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(
            flow_m3s=0.05, water_type="watercourse", sweeping_velocity_mps=0.0
        )


def test_invalid_open_area_ratio_raises():
    with pytest.raises(ValueError):
        calculate_screen_spec(flow_m3s=0.05, open_area_ratio=1.5)
