"""Unit conversions for imperial input/output.

The calculations are SI throughout (m^3/s, m^2, m/s, mm); these factors
convert at the edges only.
"""

from __future__ import annotations

#: 1 cubic foot per second in cubic metres per second (exact: 0.3048^3).
CFS_TO_M3S = 0.028316846592

#: 1 square metre in square feet (exact: 1 / 0.3048^2).
M2_TO_FT2 = 10.763910416709722


def cfs_to_m3s(flow_cfs: float) -> float:
    return flow_cfs * CFS_TO_M3S


def m3s_to_cfs(flow_m3s: float) -> float:
    return flow_m3s / CFS_TO_M3S


def m2_to_ft2(area_m2: float) -> float:
    return area_m2 * M2_TO_FT2
