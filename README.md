# Fish Screen Specs

Calculate screen specifications for water intakes that comply with Fisheries and
Oceans Canada (DFO) fish-screen guidelines.

## Purpose

Given an intake design flow and the life stage of fish to be protected, this tool
computes the minimum effective (open) screen area, total screen area, and the
allowable opening size needed to meet DFO's *Freshwater Intake End-of-Pipe Fish
Screen Guideline*. It is intended to support intake design and regulatory review.

## DFO design criteria (reference)

The current DFO interim standard, *Water intake end-of-pipe fish screens*
(2026-03-02; a saved copy ships in this repo), constrains intake screens through
**approach velocity** (set by the sweeping-velocity regime) and **screen opening
size** (set by species sensitivity):

| Parameter | Value | Citation |
|---|---|---|
| Max approach velocity — still waters / no fish data | 0.035 m/s (Table C-1) — but §3.1.1 body text says 0.055 m/s; the conservative 0.035 is used | §3.1.1; Table C-1 |
| Max approach velocity — sweeping velocity ≥ 2× approach | up to 0.12 m/s | §3.1.1 |
| Max slot / opening size | 2.54 mm | §3.2.1; Table C-1 |
| Max slot / opening size — eels or small-bodied SAR (< 25 mm fork length) | 1 mm | §3.2.1; Table C-1 |
| Min open screen area (porosity) | 50% | §3.2.1; Table C-1 |

Approach velocity is the water velocity normal to the screen face, computed across
the **effective (open) area** of the screen (submerged area only). Total screen
area must be increased to account for the screen's open-area ratio and a
clogging/blockage allowance (the allowance is a design margin, not a requirement
of the standard).

> These values are encoded with section citations in `src/fish_screen/dfo.py`
> and mirror the audited `DFO_CRITERIA` block in `fish-screen-tool.html`.

## Project layout

```
fish-screen-specs/
├── README.md
├── TASKS.md              # development task tracker
├── pyproject.toml
├── .gitignore
├── src/fish_screen/
│   ├── __init__.py
│   ├── dfo.py            # DFO criteria constants
│   ├── calculator.py     # core screen-spec calculations
│   └── cli.py            # command-line interface
└── tests/
    └── test_calculator.py
```

## Quick start

```bash
pip install -e .
fish-screen --flow 0.05                                      # still-water default
fish-screen --flow 0.05 --scenario sweeping_credit           # sweeping ≥ 2× approach
fish-screen --flow 0.05 --sensitive-species                  # eels / small SAR present
```

## Primary deliverable — `fish-screen-tool.html`

`fish-screen-tool.html` is a **single self-contained HTML file** (no build step, no
network calls, runs offline by double-click) that reproduces and extends DFO's
*End-of-Pipe Screen Size Tool*: design-approach-velocity resolution, minimum effective
area, six screen geometries (solve-for-dimension or check-actual), itemized PASS/FAIL
compliance verdicts with section citations, an intake-hydraulics panel, multi-intake site
roll-up, an editable screen-product library, a §3.4 inspection checklist, and a
print-to-PDF scoping summary.

All regulatory constants live in one audited `DFO_CRITERIA` config block at the top of the
script, each annotated with its standard section. **The standard is internally inconsistent
on the still-water design approach velocity** — §3.1.1 body text gives **0.055 m/s** while
Table C-1 gives **0.035 m/s**. The tool defaults to the conservative **0.035 m/s**, shows
both with citations, and flags the conflict; it does not silently resolve it.

> Criteria source: DFO *Water intake end-of-pipe fish screens* (interim standard). The tool
> is a scoping/QA aid, not engineering design or a DFO determination.

## Status

The HTML tool is the primary deliverable. The Python package under `src/fish_screen/` is a
lightweight scriptable companion: its criteria constants are now synced with the tool's
audited `DFO_CRITERIA` block (the old 0.038 / 0.119 m/s fry-based placeholders are gone).
See `TASKS.md`.
