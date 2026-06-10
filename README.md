# Fish Screen Specs

Calculate screen specifications for water intakes that comply with Fisheries and
Oceans Canada (DFO) fish-screen guidelines.

## Purpose

Given an intake design flow and the life stage of fish to be protected, this tool
computes the minimum effective (open) screen area, total screen area, and the
allowable opening size needed to meet DFO's *Freshwater Intake End-of-Pipe Fish
Screen Guideline*. It is intended to support intake design and regulatory review.

## DFO design criteria (reference)

The DFO guideline constrains intake screens primarily through **approach
velocity** and **screen opening size**, which depend on the smallest fish life
stage present:

| Parameter | Fry present | No fry (fingerlings/larger) |
|---|---|---|
| Max approach velocity | 0.038 m/s | 0.119 m/s |
| Max round opening diameter | 2.54 mm | larger (site-specific) |
| Max slot width | 2.54 mm | larger (site-specific) |

Approach velocity is the water velocity normal to the screen face, computed across
the **effective (open) area** of the screen. Total screen area must be increased
to account for the screen's open-area ratio and a clogging/blockage allowance.

> These values are encoded as defaults in `src/fish_screen/dfo.py` and should be
> verified against the current published guideline before use in design.

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
fish-screen --flow 0.05 --life-stage fry
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

The HTML tool is the working deliverable. The Python package under `src/fish_screen/` is an
earlier scaffold whose approach-velocity placeholders (0.038 / 0.119 m/s) are **superseded**
by the authoritative values now encoded in `fish-screen-tool.html`. See `TASKS.md`.
