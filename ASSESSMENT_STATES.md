# Assessment states

The HTML tool uses the same intake state on screen, in the site roll-up, and
in print. A sizing PASS covers only the checks this tool calculates.

| State | When it applies | Presentation |
| --- | --- | --- |
| Invalid | A required input is malformed, out of range, or incompatible with its context | CHECK INPUTS; field errors; no calculated verdict |
| Fail | Valid inputs produce at least one failed sizing or installation check | SIZING FAIL; failed checks remain visible |
| Needs review | Calculations are valid but required velocity evidence is missing | NEEDS REVIEW; explain the missing evidence |
| Unassessed | Calculations are valid but the user has not confirmed the inputs for this intake | UNASSESSED; identify prefilled values as an example |
| Pass | All calculated checks pass, required evidence is recorded, and inputs are confirmed | SIZING PASS |

The site takes the first applicable state in the order above across all intakes.
An empty site is unassessed. Invalid intakes are excluded from totals and this
exclusion is stated. Calculated totals for unassessed intakes remain illustrative.
Editing assessment inputs or site environment/species clears confirmation.
Changing display units or converting a flow value between units does not.

Elevated sweeping credit is invalid for a still waterbody. In flowing or tidal
water it needs baseline confirmation. SPOT input needs a governing species and
a recorded source/basis. Above 0.12 m/s it additionally needs an explicit QEP
review confirmation. This is a review policy, not a new regulatory velocity cap:
DFO §3.1.1 and Table C-1 specify the 0.12 ceiling for sweeping credit, while
species-specific design uses SPOT. Verified against the
[DFO standard](https://www.dfo-mpo.gc.ca/pnw-ppe/standards-normes/fish-screen-grillage-poisson-eng.html)
on 2026-09-18.

Optimization uses the intake validator and evaluates every proposed design with
the complete calculation/check path. Candidates must pass all checks and have
the required velocity evidence. Recommendations list changes and preserve every
dimension except the selected free dimension. Applying a candidate clears input
confirmation; the user reviews the resulting design before a sizing PASS.

Saved files are validated into temporary state before any live state changes.
Older files without confirmation or checklist fields load as unassessed with
an empty checklist. Invalid numeric drafts can be saved and restored for
correction; malformed structure, enums, and product references reject the file.
