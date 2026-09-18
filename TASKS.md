# Development Task Tracker — Fish Screen Specs

Project: DFO-compliant water-intake fish-screen spec calculator
Repo: https://github.com/shepherd70/fish-screen-specs
Last updated: 2026-09-18 (cross-browser coverage merged; manual verification prepared)

Status legend: ✅ done · 🔄 in progress · ⬜ not started · 🅿️ blocked · ⛔ superseded

> **Direction change (June 2026):** the single-file `fish-screen-tool.html` is now
> the **primary deliverable** (see README). It reproduces and extends DFO's
> *End-of-Pipe Screen Size Tool* with authoritative criteria from the interim
> standard (cited by URL in the README and `src/fish_screen/dfo.py`). The Python
> package under
> `src/fish_screen/` is a scriptable companion whose criteria constants were
> synced with the tool's `DFO_CRITERIA` block on 2026-08-23;
> the HTML tool remains the working deliverable.

Current status: implementation milestones through UI are complete. The UI
review and hardening shipped in
[PR #12](https://github.com/shepherd70/fish-screen-specs/pull/12) and
[PR #13](https://github.com/shepherd70/fish-screen-specs/pull/13), both merged
2026-09-18. Cross-browser coverage shipped in
[PR #14](https://github.com/shepherd70/fish-screen-specs/pull/14), also merged
2026-09-18. [Hosted CI on main](https://github.com/shepherd70/fish-screen-specs/actions/runs/35360017602)
passed for commit `159ee95`, including Chromium, Firefox, and WebKit.
Human screen-reader verification remains open (see Milestone V).

## Milestone 0 — Project setup

- ✅ Move project to its own working directory
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
      module docstring cites the standard (interim, 2026-03-02) by URL.
- ✅ "No fry" opening size — retired. The current standard keys opening size
      to sensitive-species presence (2.54 mm default / 1 mm with eels or
      small-bodied SAR < 25 mm fork length), not fry vs. no-fry; the package
      API now follows that structure, in the standard's own vocabulary
      (`water_type` waterbody/watercourse + `sweeping_velocity_mps` +
      `sensitive_species`).

## Milestone PY — Python scaffold disposition (was Milestones 2–4)

The Python package is retained as a scriptable/batch companion, as documented
in the README. Its original backlog is complete; the HTML tool remains the
primary deliverable, with its own assessment and session workflows.

- ✅ Sync `dfo.py` constants + citations with the tool's `DFO_CRITERIA` block
      (2026-08-23; API reworked to the standard's terms — water type +
      sweeping velocity + sensitive species, min-open-area flag added,
      tests 12/12)
- ✅ Opening-size compliance check (2026-08-23: `--opening MM` / 
      `proposed_opening_mm` → PASS/FAIL vs the sensitive-aware limit)
- ✅ Imperial units (cfs / ft²) with conversion (2026-08-23: `--flow-cfs`
      input; areas also reported in ft²; conversions in `units.py`)
- ✅ Cylindrical/T-screen and other geometries (2026-08-23: `geometry.py`
      ports all six Figure-2 shapes from the HTML tool — disc, panel, box,
      cylinder, cone, half-barrel — with solve-one-dimension (1 mm round-up)
      and check-as-fixed modes, multi-unit support; CLI `--geometry/--dim/
      --solve-for/--units`)
- ✅ Geometry columns in batch CSV mode (2026-08-23: `geometry`, `dim_*`,
      `solve_for`, `units` per row; solve or check per intake, geometry
      column in the table and object in JSON, row errors isolated)
- ✅ Structured JSON output on the CLI (2026-08-23: `--json`; imperial runs
      include `flow_cfs` / `*_ft2` fields)
- ✅ Batch mode: read intake parameters from CSV (2026-08-23: `--batch FILE`,
      per-row errors isolated, unknown columns rejected, table or JSON output)
- ✅ Expanded tests, ruff, mypy, CI (2026-08-23: 26 tests; ruff + strict mypy
      clean; GitHub Actions runs lint/type/test via uv. Python floor raised
      to 3.10 — 3.9 is EOL and unsupported by current mypy)
- ✅ Tag v0.1.0 (2026-08-23: annotated tag on b72bccb + GitHub release;
      42 tests, ruff + strict mypy clean at tag time)

## Milestone U — Usability & output (HTML tool backlog)

- ✅ Export/import site state (JSON) so a scoping session can be saved/shared
      (2026-08-23: Save/Load buttons; schema-tagged file carries site fields,
      intakes, product library, display units; loads merge over defaults so
      older saves stay compatible; replace-confirmation before load)
- ✅ CSV import of intake parameters (2026-08-23: same columns as
      `fish-screen --batch` incl. geometry columns; appends intakes; per-row
      errors skipped and reported; sweeping-velocity rows still require the
      baseline-data confirmation — the tool never auto-asserts the elevated
      claim; `blockage_allowance` maps to the fouling de-rating factor)
- ✅ Imperial-unit display option (2026-08-23: site-level toggle adds
      cfs / ft² / ft/s / in equivalents in metric tiles and roll-up;
      display-only — calculations stay SI)
- ✅ Worked examples in README (2026-08-23: three examples — still-water
      default, sweeping credit at the standard's 0.24→0.12 example, and an
      imperial eel-bearing case with a failing opening check)

## Milestone GP — Go public

- ✅ Pre-publication audit (2026-08-23: full-history secrets sweep clean; commit
      authorship already on noreply addresses; no deleted-file exposure)
- ✅ Remove the saved DFO page capture + assets (~2.3 MB, Crown Copyright,
      embedded GTM/Clarity analytics); cite the standard by URL instead
      (README, `dfo.py`, tracker)
- ✅ Genericize site placeholders in `fish-screen-tool.html` (project /
      location / water-body examples no longer name a real project)
- ✅ Add MIT `LICENSE` (matches the `pyproject.toml` declaration), `authors`
      and `[project.urls]` metadata
- ✅ Remove `setup-git.ps1` and local Windows paths from the tracker
- ✅ README overhaul: HTML tool leads, correct standard title in the intro
      (was citing the legacy 1995 guideline), URL citation, real project
      layout, CI + license badges, Development and License sections
- ✅ CI hardening: `permissions: contents: read`; Python 3.10–3.13 matrix
- ✅ Verified at publication: ruff clean, strict mypy clean, **45 tests
      passing** (2026-08-23)
- ✅ Repo made public with description + topics

## Milestone UI — UI review and hardening (HTML tool)

Findings, priorities, and the four-phase plan live in `UI_REVIEW_PLAN.md`.

- ✅ UI review of `fish-screen-tool.html` (2026-09-17): three focused reviews
      (visual/responsive, accessibility, intake-sizing workflow) plus a second
      pass that re-ran every exercised case under node, corrected three
      findings, and added the missed gaps (sweeping verdict that cannot fail,
      optimizer skipping input validation, false FAIL on a non-numeric
      envelope, enum validation on JSON load, CSV parity with the Python
      reader, locale-mixed number formatting); merged in
      [PR #12](https://github.com/shepherd70/fish-screen-specs/pull/12)
- ✅ Phase 1 — assessment state model in `ASSESSMENT_STATES.md`; strict shared
      numeric validation; explicit input confirmation; elevated credit gated by
      environment and baseline evidence; SPOT basis/species and review policy;
      informational sweeping ratio; intake numbering fixed.
- ✅ Phase 2 — optimizer evaluates complete intake checks, preserves fixed and
      displayed calculated dimensions, and previews changes; transactional JSON
      load validates structure/enums/product references; checklist round-trip;
      shared CSV fixture and environment mismatch guidance; flow units convert;
      explicit product snapshots; 30-second deletion undo.
- ✅ Phase 3 — programmatic labels, contextual actions, intake headings, field
      error associations and stable live regions; focus preserved on updates and
      moved after add/duplicate/remove; mobile controls and grids fit; stronger
      chart contrast; compact result summary; fixed period decimal convention;
      print values wrap and headings/verdicts stay with their content.
- ✅ Phase 4 — 34 Node regression cases, 46 Python tests including shared CSV
      parity, and 13 Chromium browser workflows pass locally; ruff and strict
      mypy pass. Browser coverage includes 320/390/640 px, 200% CSS scaling,
      French locale, keyboard sizing/save, JSON rollback, snapshots/undo, and
      default/assessed/multi-intake PDFs. CI runs both test stacks and retains
      browser artifacts. Default Letter PDF is five pages (previously six).
- ✅ Merge all four implementation phases in
      [PR #13](https://github.com/shepherd70/fish-screen-specs/pull/13)
      (2026-09-18; main commit `0404b1f`).
- ✅ Hosted CI passes on the merged main commit (2026-09-18): Python
      3.10–3.13 lint/type/test matrix and HTML regression/browser job;
      [run #35356868506](https://github.com/shepherd70/fish-screen-specs/actions/runs/35356868506).

Verification at merge used Chromium. Follow-up coverage and remaining limits
are tracked below.

## Milestone V — Cross-browser and accessibility verification

- ✅ Run the shared offline-file workflows in Chromium, Firefox, and WebKit
      (2026-09-18): 13 scenarios per engine plus one Chromium PDF-export case,
      **40 browser checks passing locally**. Coverage includes assessment
      states, optimizer Apply, save/load rollback, CSV import, product snapshots,
      deletion undo, keyboard focus, 320/390/640 px layouts, 200% CSS scaling,
      and period decimals under a French locale.
- ✅ Verify default, assessed, and multi-intake print views in each engine,
      including readable values and return to screen mode. Keep native
      default/assessed/multi-intake PDF export checks in Chromium.
- ✅ Configure CI to install all three browsers and retain mobile/print-view
      screenshots, PDFs, and failure screenshots/traces. The Chromium executable
      override is scoped to its project; document single-browser test commands.
- ✅ Merge the cross-browser extension in
      [PR #14](https://github.com/shepherd70/fish-screen-specs/pull/14)
      (2026-09-18; main commit `159ee95`).
- ✅ Verify hosted CI for both the PR and merged main commit: browser/HTML
      job and Python 3.10–3.13 matrix passed;
      [PR run](https://github.com/shepherd70/fish-screen-specs/actions/runs/35359650225),
      [main run](https://github.com/shepherd70/fish-screen-specs/actions/runs/35360017602).
- ✅ Prepare [manual screen-reader cases and a session record](SCREEN_READER_CHECK.md)
      grounded in the current app's labels, assessment states, and workflows.
- ⬜ Human screen-reader session: verify labels, field-error announcements,
      verdict changes, and focus through sizing, save/load, and deletion undo;
      record observed speech and focus using `SCREEN_READER_CHECK.md`.

Local verification: browser checks above, HTML Node regression suite, **46
Python tests**, ruff, strict mypy, and `git diff --check` pass. WebKit used its
Playwright binary with temporary host libraries and a local launcher because
system package installation required interactive sudo; CI uses Playwright's
standard `--with-deps` setup. Print views use print-media emulation and dispatched
print events; native PDF generation is tested separately. Physical mobile
devices and native Firefox/WebKit print dialogs/pagination remain unverified.

## Notes

- **Git:** resolved. The earlier Cowork-sandbox file-locking issue was worked
  around by running git locally; repo is on GitHub (`shepherd70/fish-screen-specs`)
  with a PR workflow. The one-time `setup-git.ps1` bootstrap script has been
  removed.
- **Criteria provenance:** DFO's *Water intake end-of-pipe fish screens* interim
  standard (2026-03-02,
  <https://www.dfo-mpo.gc.ca/pnw-ppe/standards-normes/fish-screen-grillage-poisson-eng.html>)
  is the source for `DFO_CRITERIA`. A saved page capture previously shipped in the
  repo; it was removed before going public (Crown Copyright + embedded analytics
  scripts) and is kept locally outside the repo.
  The tool is a scoping/QA aid, not engineering design or a DFO determination.
- **`uv.lock`** committed 2026-08-23 — CI installs with `uv sync`, so the
  lockfile keeps runs reproducible.
