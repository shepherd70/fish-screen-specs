"""Command-line interface for the fish-screen spec calculator."""

from __future__ import annotations

import argparse

from .calculator import calculate_screen_spec
from .dfo import DEFAULT_BLOCKAGE_ALLOWANCE, DEFAULT_OPEN_AREA_RATIO


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
        "--life-stage", default="fry", choices=["fry", "no_fry"],
        help="Smallest fish life stage present (default: fry).",
    )
    parser.add_argument(
        "--open-area-ratio", type=float, default=DEFAULT_OPEN_AREA_RATIO,
        help=f"Open-area ratio of screen (default: {DEFAULT_OPEN_AREA_RATIO}).",
    )
    parser.add_argument(
        "--blockage-allowance", type=float, default=DEFAULT_BLOCKAGE_ALLOWANCE,
        help=f"Clogging allowance (default: {DEFAULT_BLOCKAGE_ALLOWANCE}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    spec = calculate_screen_spec(
        flow_m3s=args.flow,
        life_stage=args.life_stage,
        open_area_ratio=args.open_area_ratio,
        blockage_allowance=args.blockage_allowance,
    )
    print(f"Life stage:              {spec.life_stage}")
    print(f"Max approach velocity:   {spec.max_approach_velocity_mps:.3f} m/s")
    print(f"Max screen opening:      {spec.max_opening_mm:.2f} mm")
    print(f"Min effective area:      {spec.effective_area_m2:.3f} m^2")
    print(f"Min gross screen area:   {spec.gross_area_m2:.3f} m^2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
