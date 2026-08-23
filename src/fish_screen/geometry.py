"""Screen geometries: gross surface-area formulas per Figure 2 (§3.7).

Mirrors the ``GEOMETRIES`` block in ``fish-screen-tool.html`` — the same six
shapes, formulas, and dimension solvers. Dimensions are metres; ``area``
returns the gross geometric area of ONE screen unit. A T-screen's body is
modelled as a cylinder.

Two usage modes, matching the HTML tool:

* **solve** — fix all dimensions but one and solve the free dimension so one
  unit provides its share of the required gross area. The solved value is
  rounded UP to a 1 mm build increment (never down: a larger dimension only
  adds area, so rounding up can't turn a passing design into a failing one).
* **check** — fix every dimension and compare the provided gross area
  against the requirement.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

#: Solved dimensions are rounded up to this build increment (1 mm).
BUILD_INCREMENT_M = 0.001

_Dims = Mapping[str, float]


@dataclass(frozen=True)
class Geometry:
    """One screen shape: its area formula and closed-form dimension solver."""

    key: str
    label: str
    formula: str
    dim_keys: tuple[str, ...]
    area: Callable[[_Dims], float]
    # solve(dim_key, target_area, fixed_dims) -> raw dimension in metres
    solve: Callable[[str, float, _Dims], float]


def _solve_disc(key: str, area: float, d: _Dims) -> float:
    return math.sqrt(4 * area / math.pi)


def _solve_panel(key: str, area: float, d: _Dims) -> float:
    return area / d["W2"] if key == "W1" else area / d["W1"]


def _solve_box(key: str, area: float, d: _Dims) -> float:
    if key == "L":
        return area / (2 * (d["W1"] + d["W2"]))
    if key == "W1":
        return area / (2 * d["L"]) - d["W2"]
    return area / (2 * d["L"]) - d["W1"]


def _solve_cylinder(key: str, area: float, d: _Dims) -> float:
    return area / (math.pi * (d["L"] if key == "D" else d["D"]))


def _solve_cone(key: str, area: float, d: _Dims) -> float:
    return area / (math.pi * (d["L"] if key == "r" else d["r"]))


def _solve_halfbarrel(key: str, area: float, d: _Dims) -> float:
    return 2 * area / (math.pi * (d["L"] if key == "D" else d["D"]))


GEOMETRIES: dict[str, Geometry] = {
    g.key: g
    for g in (
        Geometry(
            key="disc",
            label="Circular flat disc",
            formula="A = (π/4)·D²",
            dim_keys=("D",),
            area=lambda d: math.pi / 4 * d["D"] ** 2,
            solve=_solve_disc,
        ),
        Geometry(
            key="panel",
            label="Square / rectangular flat panel",
            formula="A = W1·W2",
            dim_keys=("W1", "W2"),
            area=lambda d: d["W1"] * d["W2"],
            solve=_solve_panel,
        ),
        Geometry(
            key="box",
            label="Square box / barrel (4 sides)",
            formula="A = 2·L·(W1+W2)",
            dim_keys=("L", "W1", "W2"),
            area=lambda d: 2 * d["L"] * (d["W1"] + d["W2"]),
            solve=_solve_box,
        ),
        Geometry(
            key="cylinder",
            label="Cylindrical (T-screen body)",
            formula="A = π·D·L",
            dim_keys=("D", "L"),
            area=lambda d: math.pi * d["D"] * d["L"],
            solve=_solve_cylinder,
        ),
        Geometry(
            key="cone",
            label="Conical",
            formula="A = π·r·L  (r = base radius, L = slant length)",
            dim_keys=("r", "L"),
            area=lambda d: math.pi * d["r"] * d["L"],
            solve=_solve_cone,
        ),
        Geometry(
            key="halfbarrel",
            label="Semi-hemispherical / half-barrel",
            formula="A = ½·π·D·L  (= ½ cylindrical)",
            dim_keys=("D", "L"),
            area=lambda d: 0.5 * math.pi * d["D"] * d["L"],
            solve=_solve_halfbarrel,
        ),
    )
}


@dataclass(frozen=True)
class GeometryResult:
    """Dimensioning outcome for one geometry against a required gross area."""

    geometry: str
    mode: str  # "solve" or "check"
    units: int
    dims: dict[str, float]  # final dimensions (solved value rounded up)
    solved_key: str | None
    solved_raw_m: float | None  # exact solution before the 1 mm round-up
    gross_area_unit_m2: float
    gross_area_total_m2: float
    required_gross_area_m2: float
    area_sufficient: bool


def _get_geometry(geometry: str) -> Geometry:
    try:
        return GEOMETRIES[geometry]
    except KeyError as exc:
        valid = ", ".join(sorted(GEOMETRIES))
        raise ValueError(
            f"Unknown geometry {geometry!r}. Valid options: {valid}."
        ) from exc


def size_screen(
    required_gross_area_m2: float,
    geometry: str,
    dims: Mapping[str, float],
    solve_for: str | None = None,
    units: int = 1,
) -> GeometryResult:
    """Solve one free dimension, or check fully-fixed dimensions.

    Args:
        required_gross_area_m2: Total required gross screen area across all
            units (e.g. ``ScreenSpec.gross_area_m2``).
        geometry: One of ``GEOMETRIES`` (disc, panel, box, cylinder, cone,
            halfbarrel).
        dims: Dimensions in metres. In solve mode the ``solve_for`` entry
            may be omitted; every other dimension of the shape is required.
        solve_for: Dimension key to solve for, or None to check as-fixed.
        units: Number of identical screen units sharing the flow (>= 1).
    """
    geo = _get_geometry(geometry)
    if units < 1:
        raise ValueError(f"units must be >= 1, got {units}.")
    if required_gross_area_m2 <= 0:
        raise ValueError(
            f"required_gross_area_m2 must be > 0, got {required_gross_area_m2}."
        )
    if solve_for is not None and solve_for not in geo.dim_keys:
        keys = ", ".join(geo.dim_keys)
        raise ValueError(
            f"Cannot solve for {solve_for!r}: {geo.key} has dimensions {keys}."
        )
    needed = [k for k in geo.dim_keys if k != solve_for]
    missing = [k for k in needed if k not in dims]
    if missing:
        raise ValueError(
            f"Missing dimension(s) for {geo.key}: {', '.join(missing)}."
        )
    bad = [k for k in needed if not dims[k] > 0]
    if bad:
        raise ValueError(
            f"Dimension(s) must be > 0: {', '.join(bad)}."
        )

    required_unit = required_gross_area_m2 / units
    final: dict[str, float] = {k: dims[k] for k in needed}

    if solve_for is None:
        area_unit = geo.area(final)
        area_total = area_unit * units
        return GeometryResult(
            geometry=geo.key,
            mode="check",
            units=units,
            dims=final,
            solved_key=None,
            solved_raw_m=None,
            gross_area_unit_m2=area_unit,
            gross_area_total_m2=area_total,
            required_gross_area_m2=required_gross_area_m2,
            # tolerance so a dimension solved at exactly the requirement
            # re-checks as sufficient despite float rounding
            area_sufficient=area_total >= required_gross_area_m2 * (1 - 1e-9),
        )

    raw = geo.solve(solve_for, required_unit, final)
    if not math.isfinite(raw) or raw <= 0:
        raise ValueError(
            f"Cannot solve for {solve_for!r} with the given fixed dimensions "
            "(result <= 0). Adjust the fixed dimensions."
        )
    rounded = math.ceil(raw / BUILD_INCREMENT_M) * BUILD_INCREMENT_M
    final[solve_for] = rounded
    area_unit = geo.area(final)
    area_total = area_unit * units
    return GeometryResult(
        geometry=geo.key,
        mode="solve",
        units=units,
        dims=final,
        solved_key=solve_for,
        solved_raw_m=raw,
        gross_area_unit_m2=area_unit,
        gross_area_total_m2=area_total,
        required_gross_area_m2=required_gross_area_m2,
        area_sufficient=True,  # rounded up, so always covers the requirement
    )
