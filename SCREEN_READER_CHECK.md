# Manual screen-reader verification

Status: **not run**. This checklist prepares the remaining Milestone V session;
it is not evidence that the app has passed a human accessibility review.

Use the actual offline `fish-screen-tool.html` with a screen reader and keyboard.
Record the commit, operating system, browser and screen-reader versions, locale,
and any non-default navigation or verbosity settings. Use synthetic data only.
Reload the file before each numbered case so it starts with the default Intake 1.

Use the reader's heading, form-control, and table navigation as well as Tab and
Shift+Tab. Listen to status changes and revisit controls to read their labels,
values, and errors. Record unexpected silence, repeated announcements, ambiguous
names, or lost focus even when the visible result is correct. Exact spoken
wording may vary; the check is whether the information and task remain usable.

## Cases

1. **Initial navigation and labels.** Navigate the site, Intake 1, site roll-up,
   product library, and inspection-checklist headings. Read the intake's initial
   status: UNASSESSED, with the example-input explanation. Visit Project name,
   Diverted flow Q, Flow units, Geometry, opening size, and confirmation controls.
   Verify that their names, current values, and checked states are understandable.
   Read the site roll-up table with its column headings and intake association.

2. **Input errors and recovery.** Check “I have checked these inputs for this
   intake and site”; the intake and site should become SIZING PASS. Replace
   Diverted flow Q with `50oops`. Expect CHECK INPUTS, an error identifying the
   flow field, and confirmation cleared. Revisit the field to hear its invalid
   state and explanation. Correct it to `50`: the error clears and the result
   returns to UNASSESSED. Confirm again, then set Opening size (mm) to `10`:
   expect SIZING FAIL and a readable failed opening-size check. Restore `2` and
   confirm; expect SIZING PASS. Verify that changing verdicts are announced
   without moving focus to the results or trapping the user in announcements.

3. **Typing and changing controls.** Type `25` into Diverted flow Q one character
   at a time. Verify that focus and text entry remain usable after each update.
   Change Flow units to cfs; the value converts and Q (canonical) remains
   `0.02500` m³/s. Change Geometry and the design-velocity source, listening for
   the selected values and navigating the resulting fields. Focus should stay
   on the changed selector and the newly relevant controls should be reachable.

4. **Evidence needed for review.** Select “From SPOT (species-specific)” and
   enter SPOT velocity `0.5`. Expect NEEDS REVIEW and readable explanations for
   missing species, basis, and review confirmation. In the Site panel, enter
   `Test species` as the governing species; enter `Test calculation record` as
   the intake's SPOT source / design basis. Check the QEP-review control and the
   input-confirmation control. Expect SIZING PASS. Change the basis: the review
   and input confirmations clear, returning to NEEDS REVIEW. Verify that the
   reader conveys the missing evidence and identifies the affected intake.

5. **Multiple intakes and deletion undo.** Activate Duplicate Intake 1. Focus
   should move to Rename Intake 1 (copy), and the copy should be unassessed.
   Navigate its heading and confirm that Duplicate/Remove name the correct
   intake. Remove the copy: focus should move to the surviving intake's rename
   field, and the removal plus the 30-second undo opportunity should be
   announced. Activate Undo deletion within that window. The copy and focus
   should return. Activate + Add intake and verify focus on its rename field.
   On a fresh reload, remove the only intake: focus should move to + Add intake
   and the empty site should be described as unassessed. Record whether Undo is
   discoverable and reachable in time using the reader's normal navigation.

6. **Save and reload.** Set Project name to `Reader test` and check “Confirm
   complete submergence of the effective screen area.” Use Save site (JSON) and
   keep the downloaded file. Expect an announced save result. Uncheck the
   inspection item and change the project name. Use Load site (JSON), select the
   saved file, and accept replacement. Verify the dialog is operable, the load
   result is announced, and the original name and checked item are restored.
   Record where focus resumes after the file picker and replacement dialog and
   whether the restored page can be navigated without a mouse.

7. **Failed load.** Prepare a text file named `invalid-site.json` containing
   only `{}`. Set Project name to `Keep this site` and check an inspection item.
   Load the invalid file and accept replacement when asked. Expect an announced
   “Load failed” message; the project name, intake, and inspection answer must
   remain intact. Verify that the error is understandable and normal navigation
   can continue.

## Session record

Copy this record for each tested browser/screen-reader pairing. Leave untested
cases as not run; do not infer speech or navigation results from browser tests.

- Tester and date:
- Commit:
- Operating system / version:
- Browser / version:
- Screen reader / version:
- Locale and relevant settings:

| Case | Result (pass / fail / not run) | Observed speech, focus, and issue reference |
| --- | --- | --- |
| 1. Initial navigation and labels | Not run | |
| 2. Input errors and recovery | Not run | |
| 3. Typing and changing controls | Not run | |
| 4. Evidence needed for review | Not run | |
| 5. Multiple intakes and deletion undo | Not run | |
| 6. Save and reload | Not run | |
| 7. Failed load | Not run | |

For failures, include the starting state, action, expected result, actual speech
and focus, and reproduction steps. Link the completed record and any fixes from
`TASKS.md`. Close the human-verification item only after a recorded session has
passed these cases, including retesting any fixes. State the tested pairing;
one passing session does not verify other readers, browsers, or devices.
