# Development Task Tracker — Fish Screen Specs

Project: DFO-compliant water-intake fish-screen spec calculator
Location: `C:\dev\fish-screen-specs` (worked on via WSL at `~/dev/fish-screen-specs`)
Repo: https://github.com/shepherd70/fish-screen-specs
Last updated: 2026-08-23 (criteria sync)

Status legend: ✅ done · 🔄 in progress · ⬜ not started · 🅿️ blocked · ⛔ superseded

> **Direction change (June 2026):** the single-file `fish-screen-tool.html` is now
> the **primary deliverable** (see README). It reproduces and extends DFO's
> *End-of-Pipe Screen Size Tool* with authoritative criteria from the interim
> standard (a saved copy of the standard is in the repo). The Python package under
> `src/fish_screen/` is a scriptable companion whose criteria constants were
> synced with the tool's `DFO_CRITERIA` block on 2026-08-23 (8 tests passing);
> the HTML tool remains the working deliverable.

## Milestone 0 — Project setup

- ✅ Move project to `C:\dev\fish-screen-specs`
- ✅ Scaffold package layout (`src/fish_screen`, `tests`, `pyproject.toml`)
- ✅ Core calculator with approach-velocity + gross-area logic
- ✅ CLI entry point (`fish-screen`)
- ✅ Initial unit tests (6 passing)
- ✅ Initialize git repo + first commit
      (done from a local terminal; repo now on GitHub with a PR workflow —
      PR #1 merged 2026-06-10)

## Milestone HT — HTML tool (primary deliverable)

- ✅ Single self-contained `fish-screen-tool.html`: design-approach-velocity
      resolution, minimum effective area, six screen geometries
      (solve-for-dimension or check-actual), itemized PASS/FAIL verdicts with
      section citations, intake-hydraulics panel, multi-intake site roll-up,
      editable screen-product library, §3.4 inspection checklist, print-to-PDF
      scoping summary
- ✅ Inline SVG charts: approach-velocity gauge, required-vs-provided area bar,
      annotated geometry schematic, sweeping-ratio gauge,
      submergence-sensitivity line chart, site roll-up utilization (PR #1)
- ✅ Per-intake design optimizer: searches product library / unit count / free
      dimension for leanest compliant design at a target velocity margin, ranked
      candidates with exclusion reasons, Apply locks dimensions (PR #1)
- ✅ Fix in-card buttons firing no event (Optimize/Apply/Remove/Duplicate) —
      `[data-act]` wiring routed BUTTON nodes to "click" (PR #1)
- ✅ Visual presentation pass: AA contrast, non-color pass/fail cues for
      grayscale print, responsive tables/checklist, print pagination, focus
      rings, chart label legibility (commit 38db5df)
- ✅ Merge `feature/visual-polish` to main (PR #3, merged 2026-08-23)

## Milestone 1 — Verify DFO criteria

- ✅ Confirm approach-velocity limits against the published DFO standard
      — done in the HTML tool. All regulatory constants live in one audited
      `DFO_CRITERIA` block annotated with section numbers. **Known standard
      inconsistency:** §3.1.1 body text gives 0.055 m/s still-water design
      approach velocity vs. Table C-1's 0.035 m/s; tool defaults to the
      conservative 0.035, shows both with citations, and flags the conflict.
- ✅ Confirm max opening size (round-hole dia / slot width) per life stage
      — encoded with citations in `DFO_CRITERIA`
- ✅ Additional criteria from the standard (sweeping velocity, submergence,
      §3.4 inspection requirements) — in the HTML tool
- ✅ Update `src/fish_screen/dfo.py` placeholders — synced with the tool's
      `DFO_CRITERIA` block 2026-08-23: constants carry section citations, the
      §3.1.1/Table C-1 conflict is documented and surfaced by the CLI, and the
      module docstring cites the standard (interim, 2026-03-02) and the saved
      copy in-repo.
- ✅ "No fry" opening size — retired. The current standard keys opening size
      to sensitive-species presence (2.54 mm default / 1 mm with eels or
      small-bodied SAR < 25 mm fork length), not fry vs. no-fry; the package
      API now follows that structure, in the standard's own vocabulary
      (`water_type` waterbody/watercourse + `sweeping_velocity_mps` +
      `sensitive_species`).

## Milestone PY — Python scaffold disposition (was Milestones 2–4)

Decide: retire the Python package, or bring it up to parity with the HTML tool
as a scriptable/batch backend. If kept, the original backlog applies:

- ✅ Sync `dfo.py` constants + citations with the tool's `DFO_CRITERIA` block
      (2026-08-23; API reworked to the standard's terms — water type +
      sweeping velocity + sensitive species, min-open-area flag added,
      tests 12/12)
- ⬜ Opening-size compliance check
- ⬜ Imperial units (cfs / ft²) with conversion
- ⬜ Cylindrical/T-screen and other geometries (HTML tool has six)
- ⬜ Structured JSON output on the CLI
- ⬜ Batch mode: read intake parameters from CSV
- ⬜ Expanded tests, ruff, mypy, CI
- ⬜ Tag v0.1.0

## Milestone U — Usability & output (HTML tool backlog)

- ⬜ Export/import site state (JSON) so a scoping session can be saved/shared
- ⬜ CSV import of intake parameters (batch)
- ⬜ Imperial-unit display option (cfs / ft² / in)
- ⬜ Worked examples in README

## Notes

- **Git:** resolved. The earlier Cowork-sandbox file-locking issue was worked
  around by running git locally; repo is on GitHub (`shepherd70/fish-screen-specs`)
  with a PR workflow. `setup-git.ps1` is now historical.
- **Criteria provenance:** `Water intake end-of-pipe fish screens.html` (+ assets)
  is a saved copy of the DFO interim standard used to source `DFO_CRITERIA`.
  The tool is a scoping/QA aid, not engineering design or a DFO determination.
- **`uv.lock`** appeared untracked (uv is now used to run tests); decide whether
  to commit it.
