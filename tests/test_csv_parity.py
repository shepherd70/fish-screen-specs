"""Shared import fixture verifies values and errors across both deliverables."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from fish_screen.batch import run_batch


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Node is needed for HTML parity"
)
def test_shared_csv_fixture():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "tests/fixtures/intakes.csv"
    html = json.loads(subprocess.check_output(
        ["node", str(root / "tests/html/csv-results.cjs"), str(fixture)],
        text=True,
    ))
    python = run_batch(str(fixture))
    assert len(html) == len(python)
    for js, py in zip(html, python, strict=True):
        assert bool(js["error"]) == bool(py.error), py.name
        if py.error:
            continue
        assert js["name"] == py.name
        assert js["Q"] == pytest.approx(py.spec.flow_m3s)
        assert js["Vd"] == pytest.approx(py.spec.design_approach_velocity_mps)
        assert js["effective"] == pytest.approx(py.spec.effective_area_m2)
        assert js["gross"] == pytest.approx(py.spec.gross_area_m2)
        if py.geo:
            assert js["geometry"]["dims"] == pytest.approx(py.geo.dims)
            assert js["geometry"]["area"] == pytest.approx(py.geo.gross_area_total_m2)
