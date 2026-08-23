"""DFO end-of-pipe fish-screen criteria.

Source: Fisheries and Oceans Canada, *Water intake end-of-pipe fish screens*
(interim national standard), dcterms issued/modified 2026-03-02. A saved copy
of the standard ships in this repository ("Water intake end-of-pipe fish
screens.html") and is the provenance for every constant below; section numbers
cite that document. These values mirror the audited ``DFO_CRITERIA`` block in
``fish-screen-tool.html`` (the project's primary deliverable).

The current standard does not frame criteria as fry / no-fry (that framing
came from the 1995 guideline). Instead, in the standard's own terms:

* **Approach velocity** depends on the setting.  In **waterbodies** (lakes,
  ponds, reservoirs — still waters where "the sweeping velocity criterion
  typically does not apply") the maximum approach velocity is 0.035 m/s
  (Table C-1).  **Known inconsistency:** the §3.1.1 body text instead gives
  0.055 m/s as the maximum design approach velocity where data are
  unavailable.  This module, like the HTML tool, defaults to the conservative
  0.035 m/s and exposes both values.  In **watercourses** (rivers, streams,
  channels, tidal zones) a higher design approach velocity may be considered
  where baseline data show the sweeping velocity exceeds it by a factor of
  at least 2 — i.e. 50% of sweeping velocity, capped at 0.12 m/s
  (e.g. 0.24 m/s sweeping -> 0.12 m/s approach).  Without sweeping-velocity
  data the conservative 0.035 m/s default stands.
* **Opening size** depends on species sensitivity: 2.54 mm maximum slot or
  opening size, reduced to 1 mm in the presence of eels or small-bodied
  species at risk (< 25 mm fork length) (§3.2.1; Table C-1).
* **Porosity**: a minimum of 50% of the screen area must be open (§3.2.1).

This module is a scoping/QA aid, not engineering design or a DFO
determination.
"""

from __future__ import annotations

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


# --- Water types (§3.1.2) ---------------------------------------------------

#: The standard's two settings: "waterbodies" are still waters (lakes, ponds,
#: reservoirs) where the sweeping-velocity criterion typically does not
#: apply; "watercourses" are flowing waters (rivers, streams, channels,
#: tidal zones) where it does.
WATER_TYPES = ("waterbody", "watercourse")


def design_approach_velocity_mps(
    water_type: str,
    sweeping_velocity_mps: float | None = None,
) -> float:
    """Maximum design approach velocity (m/s) per §3.1.1 / Table C-1.

    Args:
        water_type: "waterbody" (still waters) or "watercourse" (flowing
            waters, including tidal zones).
        sweeping_velocity_mps: Site-characterized sweeping velocity, only
            meaningful for watercourses. When provided, the design approach
            velocity may rise to 50% of it, capped at 0.12 m/s, and never
            below the 0.035 m/s conservative default. Must come from
            baseline data (§3.1.2).

    Raises:
        ValueError: for an unknown water type, a non-positive sweeping
            velocity, or a sweeping velocity supplied for a waterbody
            (where the criterion does not apply).
    """
    if water_type not in WATER_TYPES:
        valid = ", ".join(WATER_TYPES)
        raise ValueError(
            f"Unknown water_type {water_type!r}. Valid options: {valid}."
        )
    if water_type == "waterbody":
        if sweeping_velocity_mps is not None:
            raise ValueError(
                "sweeping_velocity_mps does not apply to still waterbodies "
                "(§3.1.2); omit it or use water_type='watercourse'."
            )
        return APPROACH_VELOCITY_STILL_TABLE_C1_MPS
    if sweeping_velocity_mps is None:
        # Watercourse without sweeping-velocity data: conservative default.
        return APPROACH_VELOCITY_STILL_TABLE_C1_MPS
    if sweeping_velocity_mps <= 0:
        raise ValueError(
            f"sweeping_velocity_mps must be > 0, got {sweeping_velocity_mps}."
        )
    credited = sweeping_velocity_mps / SWEEPING_VELOCITY_FACTOR
    return min(
        APPROACH_VELOCITY_ELEVATED_MAX_MPS,
        max(APPROACH_VELOCITY_STILL_TABLE_C1_MPS, credited),
    )

# --- Non-regulatory defaults ------------------------------------------------

#: Default open-area ratio. The standard's floor is 50% open (§3.2.1);
#: the actual value depends on the screen product.
DEFAULT_OPEN_AREA_RATIO = MIN_OPEN_AREA_RATIO

#: Clogging/blockage design allowance applied to gross area. NOT from the
#: standard (which instead requires openings be kept clear in service, §3.4);
#: retained as a conservative design margin.
DEFAULT_BLOCKAGE_ALLOWANCE = 0.20


def max_opening_mm(sensitive_species_present: bool) -> float:
    """Maximum slot/opening size (mm) per §3.2.1.

    ``sensitive_species_present`` means eels or small-bodied species at risk
    (< 25 mm fork length) may be present.
    """
    if sensitive_species_present:
        return MAX_OPENING_SENSITIVE_MM
    return MAX_OPENING_DEFAULT_MM
