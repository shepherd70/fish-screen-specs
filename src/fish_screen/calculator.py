"""Core fish-screen specification calculations.

The governing constraint is approach velocity across the screen's *effective*
(open) area:

    v_approach = Q / A_effective

Rearranged for the minimum effective area at the DFO velocity limit:

    A_effective_min = Q / v_max

The gross (total) screen area is larger than the effective area because only a
fraction of the screen face is open to flow, and an allowance is added for
clogging/blockage:

    A_gross = A_effective / open_area_ratio / (1 - blockage_allowance)
"""

from __future__ import annotations

from dataclasses import dataclass

from .dfo import (
    DEFAULT_BLOCKAGE_ALLOWANCE,
    DEFAULT_OPEN_AREA_RATIO,
    ScreenCriteria,
    get_criteria,
)


@dataclass(frozen=True)
class ScreenSpec:
    """Result of a screen-spec calculation. Areas in m^2, velocity in m/s."""

    flow_m3s: float
    life_stage: str
    max_approach_velocity_mps: float
    max_opening_mm: float
    effective_area_m2: float
    gross_area_m2: float
    open_area_ratio: float
    blockage_allowance: float


def calculate_screen_spec(
    flow_m3s: float,
    life_stage: str = "fry",
    open_area_ratio: float = DEFAULT_OPEN_AREA_RATIO,
    blockage_allowance: float = DEFAULT_BLOCKAGE_ALLOWANCE,
) -> ScreenSpec:
    """Compute minimum screen areas for a DFO-compliant intake.

    Args:
        flow_m3s: Intake design flow rate (m^3/s). Must be > 0.
        life_stage: Fish life stage key ("fry" or "no_fry").
        open_area_ratio: Fraction of gross area open to flow, in (0, 1].
        blockage_allowance: Clogging allowance fraction, in [0, 1).

    Returns:
        A ScreenSpec with effective and gross area requirements.
    """
    if flow_m3s <= 0:
        raise ValueError(f"flow_m3s must be > 0, got {flow_m3s}.")
    if not 0 < open_area_ratio <= 1:
        raise ValueError(
            f"open_area_ratio must be in (0, 1], got {open_area_ratio}."
        )
    if not 0 <= blockage_allowance < 1:
        raise ValueError(
            f"blockage_allowance must be in [0, 1), got {blockage_allowance}."
        )

    criteria: ScreenCriteria = get_criteria(life_stage)
    v_max = criteria.max_approach_velocity_mps

    effective_area = flow_m3s / v_max
    gross_area = effective_area / open_area_ratio / (1 - blockage_allowance)

    return ScreenSpec(
        flow_m3s=flow_m3s,
        life_stage=criteria.life_stage,
        max_approach_velocity_mps=v_max,
        max_opening_mm=criteria.max_opening_mm,
        effective_area_m2=effective_area,
        gross_area_m2=gross_area,
        open_area_ratio=open_area_ratio,
        blockage_allowance=blockage_allowance,
    )
