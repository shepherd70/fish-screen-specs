"""Command-line interface for the fish-screen spec calculator."""

from __future__ import annotations

import argparse
import dataclasses
import json

from .calculator import ScreenSpec, calculate_screen_spec
from .dfo import (
    APPROACH_VELOCITY_CONFLICT_NOTE,
    APPROACH_VELOCITY_STILL_TABLE_C1_MPS,
    DEFAULT_BLOCKAGE_ALLOWANCE,
    DEFAULT_OPEN_AREA_RATIO,
    WATER_TYPES,
)
from .units import cfs_to_m3s, m2_to_ft2, m3s_to_cfs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fish-screen",
        description="Calculate DFO-compliant water-intake fish-screen specs.",
    )
    flow = parser.add_mutually_exclusive_group(required=True)
    flow.add_argument(
        "--flow", type=float,
        help="Intake design flow rate in m^3/s.",
    )
    flow.add_argument(
        "--flow-cfs", type=float,
        help="Intake design flow rate in cubic feet per second (imperial); "
             "areas are then also reported in ft^2.",
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
        "--opening", type=float, default=None, metavar="MM",
        help="Proposed screen slot/opening size in mm; checked against the "
             "allowable maximum and reported PASS/FAIL.",
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
    parser.add_argument(
        "--json", action="store_true",
        help="Emit the full result as JSON instead of the text report.",
    )
    return parser


def _spec_as_dict(spec: ScreenSpec, imperial: bool) -> dict:
    out = dataclasses.asdict(spec)
    if imperial:
        out["flow_cfs"] = m3s_to_cfs(spec.flow_m3s)
        out["effective_area_ft2"] = m2_to_ft2(spec.effective_area_m2)
        out["gross_area_ft2"] = m2_to_ft2(spec.gross_area_m2)
    return out


def _print_report(spec: ScreenSpec, imperial: bool) -> None:
    sweep = (
        f"{spec.sweeping_velocity_mps:.3f} m/s"
        if spec.sweeping_velocity_mps is not None else "n/a"
    )
    print(f"Water type:              {spec.water_type}")
    print(f"Sweeping velocity:       {sweep}")
    print(f"Sensitive species:       {'yes' if spec.sensitive_species else 'no'}")
    if imperial:
        print(f"Design flow:             {m3s_to_cfs(spec.flow_m3s):.3f} cfs "
              f"({spec.flow_m3s:.4f} m^3/s)")
    print(f"Design approach velocity:{spec.design_approach_velocity_mps:>7.3f} m/s")
    print(f"Max screen opening:      {spec.max_opening_mm:.2f} mm")
    if spec.proposed_opening_mm is not None:
        verdict = "PASS" if spec.opening_compliant else "FAIL"
        print(f"Proposed opening:        {spec.proposed_opening_mm:.2f} mm — "
              f"{verdict} (max {spec.max_opening_mm:.2f} mm)")
    if imperial:
        print(f"Min effective area:      {spec.effective_area_m2:.3f} m^2 "
              f"({m2_to_ft2(spec.effective_area_m2):.2f} ft^2)")
        print(f"Min gross screen area:   {spec.gross_area_m2:.3f} m^2 "
              f"({m2_to_ft2(spec.gross_area_m2):.2f} ft^2)")
    else:
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


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    imperial = args.flow_cfs is not None
    flow_m3s = cfs_to_m3s(args.flow_cfs) if imperial else args.flow
    try:
        spec = calculate_screen_spec(
            flow_m3s=flow_m3s,
            water_type=args.water_type,
            sweeping_velocity_mps=args.sweeping_velocity,
            sensitive_species=args.sensitive_species,
            proposed_opening_mm=args.opening,
            open_area_ratio=args.open_area_ratio,
            blockage_allowance=args.blockage_allowance,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    if args.json:
        print(json.dumps(_spec_as_dict(spec, imperial), indent=2))
    else:
        _print_report(spec, imperial)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
