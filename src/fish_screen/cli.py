"""Command-line interface for the fish-screen spec calculator."""

from __future__ import annotations

import argparse
import dataclasses
import json

from .batch import BatchResult, run_batch
from .calculator import ScreenSpec, calculate_screen_spec
from .dfo import (
    APPROACH_VELOCITY_CONFLICT_NOTE,
    APPROACH_VELOCITY_STILL_TABLE_C1_MPS,
    DEFAULT_BLOCKAGE_ALLOWANCE,
    DEFAULT_OPEN_AREA_RATIO,
    WATER_TYPES,
)
from .geometry import GEOMETRIES, GeometryResult, size_screen
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
    flow.add_argument(
        "--batch", metavar="CSV",
        help="Compute specs for many intakes from a CSV file (columns: "
             "name, flow_m3s or flow_cfs, water_type, sweeping_velocity_mps, "
             "sensitive_species, proposed_opening_mm, open_area_ratio, "
             "blockage_allowance).",
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
        "--geometry", default=None, choices=sorted(GEOMETRIES),
        help="Screen shape (Figure 2, §3.7): dimension it against the "
             "required gross area. Provide dimensions with --dim; solve one "
             "with --solve-for or fix all to check a proposed screen.",
    )
    parser.add_argument(
        "--dim", action="append", default=None, metavar="KEY=METRES",
        help="Screen dimension in metres, e.g. --dim D=0.3 --dim L=1.0. "
             "Repeatable. Keys per geometry: disc D; panel W1,W2; "
             "box L,W1,W2; cylinder/halfbarrel D,L; cone r,L.",
    )
    parser.add_argument(
        "--solve-for", default=None, metavar="KEY",
        help="Dimension key to solve for (others fixed via --dim); solved "
             "value is rounded up to 1 mm. Omit to check fixed dimensions.",
    )
    parser.add_argument(
        "--units", type=int, default=1, metavar="N",
        help="Number of identical screen units sharing the flow "
             "(default: 1).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit the full result as JSON instead of the text report.",
    )
    return parser


def _parse_dims(pairs: list[str] | None) -> dict[str, float]:
    dims: dict[str, float] = {}
    for pair in pairs or []:
        key, sep, raw = pair.partition("=")
        key = key.strip()
        if not sep or not key:
            raise ValueError(
                f"--dim {pair!r}: expected KEY=METRES (e.g. --dim D=0.3)."
            )
        try:
            dims[key] = float(raw)
        except ValueError:
            raise ValueError(
                f"--dim {pair!r}: {raw!r} is not a number."
            ) from None
    return dims


def _spec_as_dict(spec: ScreenSpec, imperial: bool) -> dict[str, object]:
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


def _print_geometry(geo: GeometryResult) -> None:
    g = GEOMETRIES[geo.geometry]
    print(f"Geometry:                {g.label} — {g.formula}")
    if geo.units > 1:
        print(f"Screen units:            {geo.units}")
    fixed = ", ".join(
        f"{k} = {v:.3f} m" for k, v in geo.dims.items() if k != geo.solved_key
    )
    if geo.mode == "solve":
        assert geo.solved_key is not None
        print(
            f"Solved {geo.solved_key}:                "
            f"{geo.dims[geo.solved_key]:.3f} m"
            + (f"  ({fixed} fixed)" if fixed else "")
        )
    per_unit = (
        f"{geo.units} × {geo.gross_area_unit_m2:.3f} = "
        if geo.units > 1 else ""
    )
    verdict = "PASS" if geo.area_sufficient else "FAIL"
    print(
        f"Gross area provided:     {per_unit}{geo.gross_area_total_m2:.3f} "
        f"m^2 — {verdict} (required {geo.required_gross_area_m2:.3f} m^2)"
    )


def _print_batch(results: list[BatchResult], as_json: bool) -> int:
    failures = [r for r in results if r.error is not None]
    if as_json:
        rows: list[dict[str, object]] = []
        for r in results:
            if r.spec is None:
                rows.append({"name": r.name, "error": r.error})
                continue
            row: dict[str, object] = {
                "name": r.name, **_spec_as_dict(r.spec, r.imperial)
            }
            if r.geo is not None:
                row["geometry"] = dataclasses.asdict(r.geo)
            rows.append(row)
        print(json.dumps(rows, indent=2))
        return 2 if failures else 0
    any_geo = any(r.geo is not None for r in results)
    name_width = max(len(r.name) for r in results)
    header = (
        f"{'intake':<{name_width}}  {'v_design':>8}  {'A_eff m^2':>9}  "
        f"{'A_gross m^2':>11}  opening"
    )
    if any_geo:
        header += "  geometry"
    print(header)
    print("-" * len(header))
    for r in results:
        if r.spec is None:
            print(f"{r.name:<{name_width}}  ERROR: {r.error}")
            continue
        s = r.spec
        if s.proposed_opening_mm is None:
            opening = "-"
        else:
            verdict = "PASS" if s.opening_compliant else "FAIL"
            opening = f"{s.proposed_opening_mm:.2f} mm {verdict}"
        geo_txt = ""
        if r.geo is not None:
            g = r.geo
            geo_verdict = "PASS" if g.area_sufficient else "FAIL"
            solved = (
                f" {g.solved_key}={g.dims[g.solved_key]:.3f}m"
                if g.solved_key is not None else ""
            )
            n_units = f" ×{g.units}" if g.units > 1 else ""
            geo_txt = (
                f"  {g.geometry}{n_units}{solved} "
                f"{g.gross_area_total_m2:.3f} m^2 {geo_verdict}"
            )
        if any_geo:
            opening = f"{opening:<12}"
        low_oar = "" if s.meets_min_open_area else "  (OAR < 50% min)"
        print(
            f"{r.name:<{name_width}}  {s.design_approach_velocity_mps:>8.3f}  "
            f"{s.effective_area_m2:>9.3f}  {s.gross_area_m2:>11.3f}  "
            f"{opening}{geo_txt}{low_oar}"
        )
    if failures:
        print(f"\n{len(failures)} of {len(results)} row(s) failed.")
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.batch is not None:
        if args.geometry or args.dim or args.solve_for:
            print("error: --geometry/--dim/--solve-for are not supported "
                  "with --batch.")
            return 2
        try:
            results = run_batch(args.batch)
        except (OSError, ValueError) as exc:
            print(f"error: {exc}")
            return 2
        return _print_batch(results, args.json)
    if (args.dim or args.solve_for) and args.geometry is None:
        print("error: --dim/--solve-for require --geometry.")
        return 2
    imperial = args.flow_cfs is not None
    flow_m3s = cfs_to_m3s(args.flow_cfs) if imperial else args.flow
    geo: GeometryResult | None = None
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
        if args.geometry is not None:
            geo = size_screen(
                required_gross_area_m2=spec.gross_area_m2,
                geometry=args.geometry,
                dims=_parse_dims(args.dim),
                solve_for=args.solve_for,
                units=args.units,
            )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    if args.json:
        out = _spec_as_dict(spec, imperial)
        if geo is not None:
            out["geometry"] = dataclasses.asdict(geo)
        print(json.dumps(out, indent=2))
    else:
        _print_report(spec, imperial)
        if geo is not None:
            _print_geometry(geo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
