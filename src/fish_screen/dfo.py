"""DFO end-of-pipe fish-screen criteria.

Source: Fisheries and Oceans Canada, *Water intake end-of-pipe fish screens*
(interim national standard), dcterms issued/modified 2026-03-02. A saved copy
of the standard ships in this repository ("Water intake end-of-pipe fish
screens.html") and is the provenance for every constant below; section numbers
cite that document. These values mirror the audited ``DFO_CRITERIA`` block in
``fish-screen-tool.html`` (the project's primary deliverable).

The current standard does not frame criteria as fry / no-fry (that framing
came from the 1995 guideline). Instead:

* **Approach velocity** depends on the sweeping-velocity regime.  Where no
  fish community data are available, the maximum approach velocity is
  0.035 m/s (Table C-1) for still waterbodies.  **Known inconsistency:** the
  §3.1.1 body text instead gives 0.055 m/s as the maximum design approach
  velocity where data are unavailable.  This module, like the HTML tool,
  defaults to the conservative 0.035 m/s and exposes both values.  In
  watercourses where the sweeping velocity exceeds the design approach
  velocity by a factor of at least 2, up to 0.12 m/s may be permitted
  (e.g. 0.24 m/s sweeping -> 0.12 m/s approach).
* **Opening size** depends on species sensitivity: 2.54 mm maximum slot or
  opening size, reduced to 1 mm in the presence of eels or small-bodied
  species at risk (< 25 mm fork length) (§3.2.1; Table C-1).
* **Porosity**: a minimum of 50% of the screen area must be open (§3.2.1).

This module is a scoping/QA aid, not engineering design or a DFO
determination.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Approach velocity (§3.1.1; Table C-1) ---------------------------------

#: Table C-1 maximum approach velocity, still waterbodies / no fish data.
APPROACH_VELOCITY_STILL_TABLE_C1_MPS = 0.035
#: §3.1.1 body-text maximum design approach velocity where data unavailable.
#: Conflicts with Table C-1; retained so the conflict stays visible.
APPROACH_VELOCITY_STILL_BODY_3_1_1_MPS = 0.055
#: Absolute cap on design approach velocity with sweeping-velocity credit.
APPROACH_VELOCITY_ELEVATED_MAX_MPS = 0.12
#: Sweeping velocity must exceed design approach velocity by this factor
#: before the elevated allowance applies (§3.1.1).
SWEEPING_VELOCITY_FACTOR = 2.0

APPROACH_VELOCITY_CONFLICT_NOTE = (
    "The standard is internally inconsistent: §3.1.1 body text gives "
    "0.055 m/s while Table C-1 gives 0.035 m/s for still waterbodies. "
    "This package defaults to the conservative 0.035 m/s — confirm the "
    "governing value with DFO / your QEP."
)

# --- Opening / slot size (§3.2.1; §3.3; Table C-1) -------------------------

#: Maximum slot or opening size, no eels / small-bodied species at risk.
MAX_OPENING_DEFAULT_MM = 2.54
#: Maximum slot or opening size with eels or small-bodied species at risk.
MAX_OPENING_SENSITIVE_MM = 1.0
#: Fork length below which a species counts as small-bodied (§3.2.1).
SENSITIVE_FORK_LENGTH_MM = 25.0

# --- Porosity (§3.2.1; Table C-1) ------------------------------------------

#: Minimum fraction of the screen area that must be open (design rule).
MIN_OPEN_AREA_RATIO = 0.50


@dataclass(frozen=True)
class ScreenCriteria:
    """Design limits for a given approach-velocity scenario."""

    scenario: str
    max_approach_velocity_mps: float  # water velocity normal to screen face
    citation: str


#: Still waterbodies, or no fish community data — sweeping credit N/A.
STILL_WATER = ScreenCriteria(
    scenario="still_water",
    max_approach_velocity_mps=APPROACH_VELOCITY_STILL_TABLE_C1_MPS,
    citation="Table C-1 (0.035 m/s); §3.1.1 body text gives 0.055 m/s — "
             "conservative value used",
)

#: Watercourse with sweeping velocity >= 2x design approach velocity.
#: Site data must support the sweeping-velocity characterization.
SWEEPING_CREDIT = ScreenCriteria(
    scenario="sweeping_credit",
    max_approach_velocity_mps=APPROACH_VELOCITY_ELEVATED_MAX_MPS,
    citation="§3.1.1 (sweeping velocity >= 2x approach; 0.12 m/s cap)",
)

CRITERIA = {c.scenario: c for c in (STILL_WATER, SWEEPING_CREDIT)}

# --- Non-regulatory defaults ------------------------------------------------

#: Default open-area ratio. The standard's floor is 50% open (§3.2.1);
#: the actual value depends on the screen product.
DEFAULT_OPEN_AREA_RATIO = MIN_OPEN_AREA_RATIO

#: Clogging/blockage design allowance applied to gross area. NOT from the
#: standard (which instead requires openings be kept clear in service, §3.4);
#: retained as a conservative design margin.
DEFAULT_BLOCKAGE_ALLOWANCE = 0.20


def get_criteria(scenario: str) -> ScreenCriteria:
    try:
        return CRITERIA[scenario]
    except KeyError as exc:
        valid = ", ".join(sorted(CRITERIA))
        raise ValueError(
            f"Unknown scenario {scenario!r}. Valid options: {valid}."
        ) from exc


def max_opening_mm(sensitive_species_present: bool) -> float:
    """Maximum slot/opening size (mm) per §3.2.1.

    ``sensitive_species_present`` means eels or small-bodied species at risk
    (< 25 mm fork length) may be present.
    """
    if sensitive_species_present:
        return MAX_OPENING_SENSITIVE_MM
    return MAX_OPENING_DEFAULT_MM
