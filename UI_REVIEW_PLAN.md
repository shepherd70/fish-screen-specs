# UI review and implementation plan

Reviewed 2026-09-17. Scope: the primary offline app, `fish-screen-tool.html`.
Three focused reviews covered visual/responsive presentation, accessibility, and
the intake-sizing workflow. The default page was rendered at 1280 px and 390 px
and printed to PDF; calculation/workflow cases marked below were exercised by
running the page's JavaScript functions in isolation. Other findings are code
traces. This was not a full interactive browser or user study.
A second pass on the same day re-ran every exercised case under node (see
*Second-pass verification* at the end), corrected three findings in place, and
added the gaps it found, labelled with the same evidence terms.

## Findings, in priority order

| Priority | Finding and evidence | User impact |
| --- | --- | --- |
| P0 | A fresh page creates a prefilled `Intake 2` and shows **PASS** before a user has assessed the site ([defaults](fish-screen-tool.html#L399), [verdict](fish-screen-tool.html#L784), [init](fish-screen-tool.html#L1759); exercised and visible in desktop/print output). The name itself is an off-by-one: the counter is incremented before it is read, so every intake is numbered one higher than expected ([name](fish-screen-tool.html#L402)). | A sample calculation looks like a completed compliance assessment. |
| P0 | Invalid inputs can also show **PASS**: fixed cylinder dimensions `D=-3`, `L=-3`; flow `50oops`; and `1.5` screen units, which calculates as 2 ([validation](fish-screen-tool.html#L475), [rounding](fish-screen-tool.html#L494), [numeric parser](fish-screen-tool.html#L761); exercised). The same parser also produces a false **FAIL**: a non-numeric site envelope such as `abc` is read as `0` and fails every dimension ([envelope](fish-screen-tool.html#L608); exercised). | The verdict can be based on unintended or impossible values, in either direction. |
| P0 | A still-water site can use elevated sweeping credit and show **PASS**: the velocity source has no environment gate, and the face-angle check is skipped entirely for still water ([velocity](fish-screen-tool.html#L447), [environment UI](fish-screen-tool.html#L841), [face angle](fish-screen-tool.html#L597); exercised). The elevated block renders its own sweeping field, so the input is not hidden; the missing gate is the defect. A SPOT value of `0.5 m/s` also remains eligible for PASS with only a note ([SPOT branch](fish-screen-tool.html#L441); exercised). | The result can overstate what the entered evidence supports. The exact SPOT cap needs criteria review before choosing a hard limit. |
| P1 | The optimizer can call a candidate compliant when the intake fails its 45° face-angle check, and its max-margin mode can silently reduce a dimension the user treated as fixed ([candidate checks](fish-screen-tool.html#L684), [dimension clamp](fish-screen-tool.html#L694), [apply](fish-screen-tool.html#L749); exercised). The Apply message names only the free dimension, so the change is invisible (exercised: `D` fixed at 1.0 with a 0.8 envelope is rewritten to 0.8). The optimizer also skips the range validation the card performs: a fouling factor of `1.5` gives CHECK INPUTS on the card while the optimizer still recommends a design ([optimizer de-rating](fish-screen-tool.html#L687); exercised). | A recommended design may fail the full intake checks or change an unselected dimension without saying so. |
| P1 | The sweeping ≥ 2× verdict can never fail: the elevated design velocity is derived as min(0.5 × V_sweep, 0.12), so the check is satisfied by construction yet displays as an independent PASS ([derivation](fish-screen-tool.html#L449), [check](fish-screen-tool.html#L586); exercised with `V_sweep = 0.1`). | A reviewer reads a verdict that verifies nothing. |
| P1 | Most site, intake, and optimizer inputs have adjacent text labels without a `for`/`id` association ([site fields](fish-screen-tool.html#L180), [intake fields](fish-screen-tool.html#L827), [optimizer](fish-screen-tool.html#L1255); code trace). Structural changes rebuild intake cards and lose keyboard focus ([render](fish-screen-tool.html#L772), [events](fish-screen-tool.html#L1322)). Save/import messages and changing errors/verdicts have no live announcement ([status](fish-screen-tool.html#L253), [errors](fish-screen-tool.html#L924)). | Keyboard and screen-reader users can lose their place or miss the result of an action. |
| P1 | At 390 px, the intake header visibly clips the Duplicate action. The header does not wrap, the name has a 220 px minimum width, and the card hides overflow ([CSS](fish-screen-tool.html#L71)). The chart and checklist grids have fixed minimum tracks (240 px and 290 px) that fit at 390 px but overflow at 320 px and at high zoom ([charts](fish-screen-tool.html#L126), [checklist](fish-screen-tool.html#L134); code trace). | Some controls and content become hard to reach on phones or at high zoom. |
| P1 | The default one-intake PDF spans six letter pages: the intake heading is separated from its fields, the calculation-chain heading from its content, and the roll-up heading/verdict from its table ([print CSS](fish-screen-tool.html#L136), [result](fish-screen-tool.html#L977), [roll-up](fish-screen-tool.html#L1426); rendered PDF). | The exported report is harder to review and can separate a verdict from its evidence. |
| P1 | A malformed saved JSON file changes site fields, the imperial toggle, and the product library before a later error reports "Load failed", and the surviving intakes then index into the file's product list ([restore](fish-screen-tool.html#L1565); exercised with `intakes:[null]`). A file whose intake carries an unknown `geometry` or `flowUnit` passes the schema checks, is assigned to state, and throws inside render, leaving the intake list empty ([flow unit](fish-screen-tool.html#L470), [geometry](fish-screen-tool.html#L512); exercised). The UI claims batch-CSV compatibility but rejects the batch `water_type` column, accepts a `flow_Ls` column the Python reader does not, and accepts `50oops` as 50 where Python rejects it ([claim](fish-screen-tool.html#L251), [columns](fish-screen-tool.html#L1615), [flow columns](fish-screen-tool.html#L1613), [numeric](fish-screen-tool.html#L1653); exercised). | Recovery and import results are surprising, and a failed load can damage an in-progress session. |
| P2 | Changing a flow unit keeps the typed number and reinterprets it (`50 L/s` becomes `50 cfs`). Both this and converting the value are common conventions; the defect is that the control does not say which applies ([unit event](fish-screen-tool.html#L1336); code trace). Editing a selected product changes its picker label but leaves copied intake values unchanged ([library edit](fish-screen-tool.html#L1454); code trace). | Users may not know which unit convention applies, or may trust a product label that no longer describes the intake values. |
| P2 | Save/Load claims to capture the whole session but omits checklist selections; loading another site leaves old checks visible ([save](fish-screen-tool.html#L1538), [checklist](fish-screen-tool.html#L1487)). Intake and product deletion have no undo ([intake action](fish-screen-tool.html#L1322), [product action](fish-screen-tool.html#L1461); code traces). | Work can be lost or falsely carried into another site's report. |
| P2 | Repeated action buttons lack intake/product context, intake cards lack navigable headings, and the chart's clean bar has 1.84:1 contrast against its track, below the 3:1 minimum for non-text graphics ([actions](fish-screen-tool.html#L818), [product delete](fish-screen-tool.html#L1450), [chart](fish-screen-tool.html#L991); code traces, contrast computed). Results sit below a long disclaimer and four intake fieldsets; the 390 px screenshot has not reached metrics after 3000 px of scrolling. Add intake scrolls a fixed 200 px instead of moving focus to the new card ([init](fish-screen-tool.html#L1762)). The criteria-conflict warning repeats its explanation. | Navigation and scanning take more effort, especially across multiple intakes. |
| P2 | Number formatting is locale-dependent in the metric tiles and tables, fixed-point in the SVG labels, and inputs accept only a period decimal ([fmt](fish-screen-tool.html#L763), [SVG ticks](fish-screen-tool.html#L1007), [parser](fish-screen-tool.html#L762); code trace). In a French-Canadian locale a report shows `0,035` in the tiles and `0.035` in the charts. | One report mixes decimal conventions, and a copied tile value does not parse when pasted into an input. |

## Implementation sequence

### 1. Make results trustworthy

Write the state model down before coding: the states, how each intake state
rolls up to the site verdict, and how each renders on screen and in print.
Phase 3's print work depends on it. Separate **example/unassessed**,
**invalid**, **needs review**, and **sizing pass/fail** states. Start with a
clearly marked example or an empty intake; never show a site-level PASS from
untouched defaults. Make the roll-up and print summary use the same state
model. Keep the tool's scoping disclaimer visible, but express missing site
evidence next to the relevant result. Fix the intake-name off-by-one.

Use one strict input-validation path before calculations and optimization (the
optimizer currently has its own, looser checks): consume the entire numeric
string, require positive flow and geometry dimensions, require an integer unit
count, validate fractions and angles, and treat a non-numeric envelope as an
error rather than zero. Reject invalid fields in place, preserve the typed value
for correction, and suppress PASS while any input is invalid. Gate elevated
sweeping credit by environment and required baseline evidence. Remove the
sweeping ≥ 2× verdict from the elevated case, where it cannot fail, and show the
ratio as information instead. Review the DFO rule for a SPOT value above
`0.12 m/s` before deciding whether to block it or mark it for documented review.

**Acceptance:** fresh load has no green site PASS; each reproduced invalid case
and still-water elevated case cannot PASS; a non-numeric envelope is an error,
not a FAIL; no verdict is displayed that cannot fail; the optimizer refuses the
same inputs the card refuses; valid existing worked examples retain their
expected sizing results; errors identify the specific field.

### 2. Make recommendations and state changes predictable

Run each optimizer candidate through the same applicable intake checks as the
main result, or label it explicitly as a sizing candidate until all checks pass.
Never alter a fixed dimension while searching; report an envelope conflict and
show every proposed change before Apply. Make JSON load transactional: validate
the entire file into temporary state, including enum fields (geometry, flow
unit, velocity source) and product-index bounds, then commit and render once.
Resolve CSV `water_type` against the site's environment before appending rows;
if rows mix environments, give row-specific guidance and leave the current site
unchanged. Publish one fixture CSV that the Python batch reader and the tool
must read identically, covering the flow columns and numeric strictness.

Decide whether a flow-unit change converts the value or reinterprets it, label
the control accordingly, and keep the canonical Q visible either way. Make
product presets either linked values or explicit snapshots with visible
per-intake overrides. Persist checklist answers with each saved site and clear
them when a different site loads. Add a short-lived undo action for intake and
product deletion.

**Acceptance:** an optimizer recommendation passes all displayed checks and
changes only declared fields; malformed JSON, including bad enum values, leaves
the current session intact; the shared fixture CSV imports identically in both
tools; Save/Load round-trips checklist state; the unit-switch behaviour matches
its label.

### 3. Make the app usable with keyboard, assistive tech, and small screens

Give every input a unique programmatic label, including repeated intake fields
and read-only values. Add an intake heading and consistent heading levels. Name
Duplicate, Remove, and product-delete actions with their target. Preserve focus
across card updates, especially select changes, add/duplicate/remove, and Apply,
and move focus to a newly added or duplicated intake instead of scrolling a
fixed distance.
Connect field errors to inputs and announce save/import results and verdict
changes through stable live regions.

Let the intake header wrap/stack, remove its hard minimum name width, and make
chart/checklist tracks fit their container. Give the product library a usable
small-screen presentation or an explicit horizontal scroll region. Improve chart
contrast and simplify the repeated criteria warning while retaining its citations.
Keep the short scoping warning visible and make the full disclaimer available on
demand. Pick one decimal convention for tiles, tables, charts, and inputs, or
format everything with a fixed locale, so a report never mixes `0,035` and
`0.035`. Promote a compact live verdict and key metrics near the top of each
intake; keep detailed calculation chains available after the primary result.

Give print its own pagination rules: keep section headings with their first
content block, allow long fieldsets and calculation chains to break between
children, and keep a roll-up verdict with its table. Remove the closed
optimizer's dangling explanatory sentence from print, and render long selected
input values as readable text where form controls truncate them.

**Acceptance:** at 320 px and 390 px (and 200% zoom), actions and key results
remain visible and operable; a keyboard-only user can complete sizing and
save/load without losing focus; screen-reader labels and status messages identify
the correct intake and result; a report uses one decimal convention throughout.
In default and multi-intake PDFs, headings, verdicts, and their evidence stay
together without large blank areas.

### 4. Verify the complete workflow

The page has no test harness, and the no-build, single-file constraint rules
out bundling. Extract the `<script>` block, run it under node's `vm` module with
a stubbed `document` (an element map exposing `value` and `checked`, no-op event
wiring), and call `calcIntake`, `optimizeIntake`, `applyOptimization`,
`restoreState`, and `intakeFromCSVRow` directly. This is how the second pass
reproduced every exercised case above; it needs no dependencies and can run in
CI beside pytest. Add focused regression cases there for the reproduced
false-PASS and false-FAIL inputs, environment gating, the sweeping verdict that
cannot fail, optimizer consistency, JSON rollback including bad enum values, CSV
parity with the Python reader, and the chosen unit-switch behaviour.

Print, mobile, and focus criteria need a real browser (Playwright). Exercise
fresh, valid, invalid, multi-intake, import, save/reload, mobile, keyboard, and
print/PDF workflows there. Review the print summary's pagination and confirm it
presents the same result state as the screen.

The first two phases should ship before cosmetic refinements because they change
what a PASS and a recommendation mean.

## Second-pass verification (2026-09-17)

Reproduced under node with a stubbed DOM, calling the tool's own functions:

- Fresh intake: named `Intake 2`, verdict PASS, solved `L = 3.989 m`.
- Fixed cylinder `D=-3`, `L=-3`: PASS with a positive gross area.
- Flow `50oops`: PASS with `Q = 0.05 m³/s`. Units `1.5`: PASS with 2 units.
- Envelope `abc`: FAIL against "site max 0.000 m" (not in the first pass).
- Still water, elevated credit at `0.24 m/s`, baseline confirmed: PASS at
  `V_design = 0.12`. SPOT `0.5 m/s`: PASS with a note only.
- Elevated at `V_sweep = 0.1`: the sweeping ≥ 2× check still passes (not in
  the first pass).
- Watercourse with a 60° face angle: card FAIL, optimizer recommends a
  compliant candidate. Max-margin with `D = 1.0` fixed and a `0.8` envelope:
  Apply rewrites `D` to `0.8` and reports only `L`.
- Fouling `1.5`: card CHECK INPUTS, optimizer still recommends (not in the
  first pass).
- JSON with `intakes:[null]`: project name, imperial toggle, and product
  library replaced before the throw. Unknown `geometry` or `flowUnit`:
  TypeError inside calculation after state is assigned (not in the first pass).
- CSV: `flow_Ls` accepted; `50oops` accepted as 50; `units 1.5` rejected.
- Chart clean bar against its track: 1.84:1 contrast.

Not re-verified, because no browser was available in the second pass: the
six-page PDF, the 390 px header clipping, and the 3000 px scroll to results.
The CSS is consistent with the clipping claim.
