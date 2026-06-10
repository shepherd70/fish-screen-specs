"""DFO Freshwater Intake End-of-Pipe Fish Screen Guideline criteria.

Values are defaults for development and MUST be verified against the current
published DFO guideline before use in design or regulatory submission.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScreenCriteria:
    """Design limits for a given fish life stage."""

    life_stage: str
    max_approach_velocity_mps: float  # water velocity normal to screen face
    max_opening_mm: float             # max round-hole dia or slot width


# Approach-velocity limits per the DFO guideline.
# Fry are the most restrictive case.
FRY = ScreenCriteria(
    life_stage="fry",
    max_approach_velocity_mps=0.038,
    max_opening_mm=2.54,
)

NO_FRY = ScreenCriteria(
    life_stage="no_fry",
    max_approach_velocity_mps=0.119,
    max_opening_mm=2.54,  # placeholder; site-specific when fry absent
)

CRITERIA = {c.life_stage: c for c in (FRY, NO_FRY)}

# Default fraction of gross screen area that is actually open to flow.
# Real value depends on screen product (mesh, wedge-wire, perforated plate).
DEFAULT_OPEN_AREA_RATIO = 0.40

# Default clogging/blockage safety allowance applied to gross area.
DEFAULT_BLOCKAGE_ALLOWANCE = 0.20


def get_criteria(life_stage: str) -> ScreenCriteria:
    try:
        return CRITERIA[life_stage]
    except KeyError as exc:
        valid = ", ".join(sorted(CRITERIA))
        raise ValueError(
            f"Unknown life_stage {life_stage!r}. Valid options: {valid}."
        ) from exc
