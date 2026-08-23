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
fish-screen --flow 0.05                                              # waterbody (still-water) default
fish-screen --flow 0.05 --water-type watercourse --sweeping-velocity 0.24   # sweeping-velocity credit
fish-screen --flow 0.05 --sensitive-species                          # eels / small SAR present
fish-screen --flow-cfs 1.5 --opening 3.0                             # imperial flow + opening check
fish-screen --flow 0.05 --json                                       # machine-readable output
fish-screen --batch intakes.csv                                      # many intakes from CSV
fish-screen --flow 0.05 --geometry cylinder --dim D=0.3 --solve-for L   # size a screen shape
```

Batch CSV columns: `name`, `flow_m3s` *or* `flow_cfs`, `water_type`,
`sweeping_velocity_mps`, `sensitive_species`, `proposed_opening_mm`,
`open_area_ratio`, `blockage_allowance` (blank cells take the CLI defaults;
add `--json` for a machine-readable array). Row errors are reported per intake
without stopping the rest.

## Worked examples

**1. Pond irrigation intake, 50 L/s.** A still waterbody, so the 0.035 m/s
Table C-1 limit governs and no sweeping credit is available:

```
$ fish-screen --flow 0.05
Design approach velocity:  0.035 m/s
Max screen opening:      2.54 mm
Min effective area:      1.429 m^2
Min gross screen area:   3.571 m^2
```

At 50% open area and a 20% clogging allowance, the 1.43 m² effective-area
requirement becomes ~3.57 m² of gross screen.

**2. River intake with characterized sweeping flow.** Baseline data show
0.24 m/s sweeping velocity past the screen face. The design approach velocity
may rise to 50% of sweeping — here exactly the 0.12 m/s cap (the standard's
own worked example) — cutting the required area by ~70%:

```
$ fish-screen --flow 0.05 --water-type watercourse --sweeping-velocity 0.24
Design approach velocity:  0.120 m/s
Min effective area:      0.417 m^2
Min gross screen area:   1.042 m^2
```

**3. Eel-bearing watercourse, imperial flow, checking a vendor screen.**
A 1.5 cfs intake where eels may be present, against a product with 3.0 mm
slots — the opening check fails because the sensitive-species limit is 1 mm:

```
$ fish-screen --flow-cfs 1.5 --water-type watercourse --sensitive-species --opening 3.0
Design flow:             1.500 cfs (0.0425 m^3/s)
Max screen opening:      1.00 mm
Proposed opening:        3.00 mm — FAIL (max 1.00 mm)
Min effective area:      1.214 m^2 (13.06 ft^2)
Min gross screen area:   3.034 m^2 (32.66 ft^2)
```

**4. Sizing a cylindrical (T-screen body) intake.** The six screen shapes
from the standard's Figure 2 (§3.7) — disc, panel, box, cylinder, cone,
half-barrel — can be dimensioned against the required gross area. Fix all
dimensions but one and solve it (rounded up to a 1 mm build increment), or
fix everything to check a proposed screen; `--units N` splits the flow across
identical units:

```
$ fish-screen --flow 0.05 --geometry cylinder --dim D=0.3 --solve-for L --units 2
Geometry:                Cylindrical (T-screen body) — A = π·D·L
Screen units:            2
Solved L:                1.895 m  (D = 0.300 m fixed)
Gross area provided:     2 × 1.786 = 3.572 m^2 — PASS (required 3.571 m^2)
```

Add `--json` to any invocation for machine-readable output (imperial runs
include `flow_cfs` and `*_ft2` fields; geometry runs include a `geometry`
object).

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
