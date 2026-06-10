# Development Task Tracker — Fish Screen Specs

Project: DFO-compliant water-intake fish-screen spec calculator
Location: `C:\dev\fish-screen-specs`
Last updated: 2026-06-10

Status legend: ✅ done · 🔄 in progress · ⬜ not started · 🅿️ blocked

## Milestone 0 — Project setup

- ✅ Move project to `C:\dev\fish-screen-specs`
- ✅ Scaffold package layout (`src/fish_screen`, `tests`, `pyproject.toml`)
- ✅ Core calculator with approach-velocity + gross-area logic
- ✅ CLI entry point (`fish-screen`)
- ✅ Initial unit tests (6 passing)
- ⬜ Initialize git repo + first commit on a feature branch
      (must be run in a local terminal — the Cowork sandbox mount cannot
       perform git's file locking on this folder; see NOTES below)

## Milestone 1 — Verify DFO criteria

- ⬜ Confirm approach-velocity limits against the current published DFO
      *Freshwater Intake End-of-Pipe Fish Screen Guideline* (fry vs. no-fry)
- ⬜ Confirm max opening size (round-hole dia / slot width) per life stage
- ⬜ Decide handling for the "no fry" opening size (currently a placeholder)
- ⬜ Cite the guideline version/date in `dfo.py` docstring
- ⬜ Add any additional criteria the guideline imposes (e.g. sweeping velocity,
      screen orientation, minimum submergence)

## Milestone 2 — Calculation completeness

- ⬜ Add opening-size compliance check (warn if proposed mesh > allowed)
- ⬜ Support imperial units (cfs / ft²) with conversion
- ⬜ Add sweeping-velocity calc for angled/cylindrical screens (if in scope)
- ⬜ Support cylindrical/T-screen geometry, not just flat-area
- ⬜ Validate open-area-ratio defaults against real screen products

## Milestone 3 — Usability & output

- ⬜ Structured output (JSON) option on the CLI
- ⬜ Human-readable compliance report (pass/fail summary)
- ⬜ Batch mode: read intake parameters from CSV
- ⬜ Worked examples in README

## Milestone 4 — Quality & release

- ⬜ Expand test coverage (unit conversions, edge cases, geometry)
- ⬜ Add linting/formatting config (ruff) and run in CI
- ⬜ Type-check with mypy
- ⬜ Tag v0.1.0

## Notes

- **Git in this environment:** the Cowork Linux sandbox can create files on the
  `C:\dev\fish-screen-specs` mount but cannot delete/rename them, which git
  requires. A half-initialized `.git/` from an earlier attempt is present and
  must be removed from a local terminal. Run git commands directly in PowerShell
  (full permissions there). See the setup snippet shared in chat.
- **DFO defaults are unverified** placeholders in `dfo.py` and Milestone 1 must
  close before any design use.
