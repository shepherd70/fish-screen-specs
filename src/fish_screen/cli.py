"""Command-line interface for the fish-screen spec calculator."""

from __future__ import annotations

import argparse

from .calculator import calculate_screen_spec
from .dfo import (
    APPROACH_VELOCITY_CONFLICT_NOTE,
    APPROACH_VELOCITY_STILL_TABLE_C1_MPS,
    DEFAULT_BLOCKAGE_ALLOWANCE,
    DEFAULT_OPEN_AREA_RATIO,
    WATER_TYPES,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fish-screen",
        description="Calculate DFO-compliant water-intake fish-screen specs.",
    )
    parser.add_argument(
        "--flow", type=float, required=True,
        help="Intake design flow rate in m^3/s.",
    )
    parser.add_argument(
        "--water-type", default="waterbody", choices=list(WATER_TYPES),
        help="waterbody: still waters (lakes, ponds, reservoirs) — 0.035 m/s "
             "limit. watercourse: flowing waters (rivers, streams, channels, "
             "tidal zones) — may use a sweeping-velocity credit. "
             "(default: waterbody)",
    )
    parser.add_argument(
        "--sweeping-velocity", type=float, default=None, metavar="MPS",
        help="Site-characterized sweeping velocity in m/s (watercourses "
             "only). Design approach velocity may rise to 50%% of it, capped "
             "at 0.12 m/s; without it the 0.035 m/s default applies.",
    )
    parser.add_argument(
        "--sensitive-species", action="store_true",
        help="Eels or small-bodied species at risk (< 25 mm fork length) "
             "may be present (tightens max opening to 1 mm).",
    )
    parser.add_argument(
        "--open-area-ratio", type=float, default=DEFAULT_OPEN_AREA_RATIO,
        help=f"Open-area ratio of screen (default: {DEFAULT_OPEN_AREA_RATIO}; "
             "the standard requires >= 0.50).",
    )
    parser.add_argument(
        "--blockage-allowance", type=float, default=DEFAULT_BLOCKAGE_ALLOWANCE,
        help=f"Clogging allowance (default: {DEFAULT_BLOCKAGE_ALLOWANCE}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        spec = calculate_screen_spec(
            flow_m3s=args.flow,
            water_type=args.water_type,
            sweeping_velocity_mps=args.sweeping_velocity,
            sensitive_species=args.sensitive_species,
            open_area_ratio=args.open_area_ratio,
            blockage_allowance=args.blockage_allowance,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    sweep = (
        f"{spec.sweeping_velocity_mps:.3f} m/s"
        if spec.sweeping_velocity_mps is not None else "n/a"
    )
    print(f"Water type:              {spec.water_type}")
    print(f"Sweeping velocity:       {sweep}")
    print(f"Sensitive species:       {'yes' if spec.sensitive_species else 'no'}")
    print(f"Design approach velocity:{spec.design_approach_velocity_mps:>7.3f} m/s")
    print(f"Max screen opening:      {spec.max_opening_mm:.2f} mm")
    print(f"Min effective area:      {spec.effective_area_m2:.3f} m^2")
    print(f"Min gross screen area:   {spec.gross_area_m2:.3f} m^2")
    if not spec.meets_min_open_area:
        print("WARNING: open-area ratio is below the 50% minimum the "
              "standard requires (§3.2.1).")
    at_still_default = (
        spec.design_approach_velocity_mps
        == APPROACH_VELOCITY_STILL_TABLE_C1_MPS
    )
    if at_still_default:
        print(f"NOTE: {APPROACH_VELOCITY_CONFLICT_NOTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
