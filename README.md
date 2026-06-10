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

## Status

Early scaffold. See `TASKS.md` for the development plan and current progress.
