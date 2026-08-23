"""Batch mode: compute screen specs for many intakes from a CSV file.

Expected columns (header row required; unknown columns are rejected so typos
don't silently fall back to defaults):

- ``name`` — intake label (optional; defaults to the row number)
- ``flow_m3s`` or ``flow_cfs`` — exactly one per row
- ``water_type`` — "waterbody" (default) or "watercourse"
- ``sweeping_velocity_mps`` — watercourses only
- ``sensitive_species`` — true/false, yes/no, 1/0 (default false)
- ``proposed_opening_mm`` — optional opening-size check
- ``open_area_ratio``, ``blockage_allowance`` — optional overrides

Blank cells take the same defaults as the CLI flags.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass

from .calculator import ScreenSpec, calculate_screen_spec
from .units import cfs_to_m3s

KNOWN_COLUMNS = frozenset(
    {
        "name",
        "flow_m3s",
        "flow_cfs",
        "water_type",
        "sweeping_velocity_mps",
        "sensitive_species",
        "proposed_opening_mm",
        "open_area_ratio",
        "blockage_allowance",
    }
)

_TRUE = {"true", "yes", "y", "1"}
_FALSE = {"false", "no", "n", "0", ""}


@dataclass(frozen=True)
class BatchResult:
    """Outcome for one CSV row: a spec, or the error that prevented one."""

    name: str
    imperial: bool  # row supplied flow_cfs
    spec: ScreenSpec | None
    error: str | None


def _get(row: dict[str, str], key: str) -> str | None:
    value = (row.get(key) or "").strip()
    return value or None


def _parse_float(row: dict[str, str], key: str) -> float | None:
    raw = _get(row, key)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"column {key!r}: {raw!r} is not a number") from None


def _parse_bool(row: dict[str, str], key: str) -> bool:
    raw = (_get(row, key) or "").lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise ValueError(f"column {key!r}: {raw!r} is not true/false")


def _row_result(name: str, row: dict[str, str]) -> BatchResult:
    flow_m3s = _parse_float(row, "flow_m3s")
    flow_cfs = _parse_float(row, "flow_cfs")
    if (flow_m3s is None) == (flow_cfs is None):
        raise ValueError("exactly one of flow_m3s or flow_cfs is required")
    imperial = flow_cfs is not None
    if flow_cfs is not None:
        flow_m3s = cfs_to_m3s(flow_cfs)
    assert flow_m3s is not None

    kwargs: dict[str, object] = {}
    water_type = _get(row, "water_type")
    if water_type is not None:
        kwargs["water_type"] = water_type
    for key in ("sweeping_velocity_mps", "proposed_opening_mm",
                "open_area_ratio", "blockage_allowance"):
        value = _parse_float(row, key)
        if value is not None:
            kwargs[key] = value

    spec = calculate_screen_spec(
        flow_m3s=flow_m3s,
        sensitive_species=_parse_bool(row, "sensitive_species"),
        **kwargs,  # type: ignore[arg-type]
    )
    return BatchResult(name=name, imperial=imperial, spec=spec, error=None)


def run_batch(path: str) -> list[BatchResult]:
    """Compute a spec per CSV row; per-row failures become row errors."""
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: empty file (a header row is required)")
        unknown = [
            f for f in reader.fieldnames
            if f is not None and f.strip() and f.strip() not in KNOWN_COLUMNS
        ]
        if unknown:
            valid = ", ".join(sorted(KNOWN_COLUMNS))
            raise ValueError(
                f"{path}: unknown column(s) {', '.join(unknown)!s}. "
                f"Valid columns: {valid}."
            )
        results: list[BatchResult] = []
        for index, row in enumerate(reader, start=2):  # header is line 1
            name = _get(row, "name") or f"row {index}"
            try:
                results.append(_row_result(name, row))
            except ValueError as exc:
                results.append(
                    BatchResult(
                        name=name, imperial=False, spec=None, error=str(exc)
                    )
                )
    if not results:
        raise ValueError(f"{path}: no data rows")
    return results
