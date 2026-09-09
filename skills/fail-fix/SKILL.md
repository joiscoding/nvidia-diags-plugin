---
name: fail-fix
description: >-
  Turn a short Diags fail log into a minimal, test-verified harness fix. Use
  when a recipe reports FAIL but the log shows the measurement satisfies the
  printed gate, or a harness assert/threshold helper is suspected. Do not touch
  recipe or SKU XML. Not for refactors or cleanup.
---

# Fail-fix

A Diags run says FAIL. The user hands you a short log. Find whether the harness
is lying; if it is, land the smallest change that makes it tell the truth, with
a focused test that was red before and green after.

Do not rewrite recipe or SKU XML to make a run pass. Do not rename or reshape
public assert helpers that recipes call. Do not mix in cleanup. Those are
separate changes.

## When

- A recipe FAILs and the log shows a gate and measured values that visibly
  satisfy it (for example `952 GB/s below minimum 900 GB/s`).
- A traceback's innermost frame is in a harness assert, threshold, or
  unit-conversion helper.
- The same SKU and recipe passed recently and only the harness moved.
- The user asks for "a fix and a test" for a harness assertion bug.

## When not

- Measured values are genuinely outside the gate — report; do not touch the
  harness.
- The ask is to loosen, tighten, or re-tune a gate (recipe/SKU ownership).
- Refactor, rename, reformat, or "modernize assertlib" — separate change.
- Diagnosis needs telemetry you do not have (fleet, Splunk, baselines).
- No executable harness in reach — triage only; do not claim a fix.

## Required inputs

Locate all of these before editing. If one is missing, say which and stop at
triage.

1. The fail log (short text).
2. The harness checkout at the failing revision.
3. The asserting function name (from the traceback).
4. How harness tests are run (`pytest`, `unittest`, or a runner script).
5. Any extras the user also wants.

## Sources of truth

Ranked. When they disagree, the higher one wins; say so in the report.

1. The log's measured values and printed gate (observations).
2. The recipe/SKU definition the log names — read only; do not edit.
3. The asserting function's docstring and call sites (public contract).
4. The focused test you write (encodes intended behavior).
5. Your reading of the code (hypothesis until red confirms it).

## Workflow

Each step ends with a validation. Do not move on until it holds.

### 1. Triage the log

By hand (or with `rg` / reading the file):

- Pull recipe name, gate kind/value/unit, and every measured value.
- Find the innermost traceback frame in harness code.
- Check whether the failure message contradicts itself.

Verdict: `SUSPECT_HARNESS_ASSERT`, `GENUINE_GATE_FAILURE`, `MIXED`, or
`UNCLEAR`.

**Validation:** one sentence each for what the recipe demanded, what was
measured, and which function raised. If `GENUINE_GATE_FAILURE`, report and
stop.

### 2. Freeze the contract

Write and keep unchanged through the fix:

```text
RECIPE:            <name>           GATE: <kind> <value> <unit>
MEASURED:          <value(s)> <unit>
ASSERTING_FN:      <module.function> at <file>:<line>
EXPECTED:          <what the function should do with these inputs>
OBSERVED:          <exact exception type and message from the log>
PUBLIC_SIGNATURE:  <def line, verbatim>
CALLERS:           <files that call ASSERTING_FN, from rg>
FOCUSED_COMMAND:   <exact test command>
OUT_OF_SCOPE:      <extras that are not this fix>
```

**Validation:** `EXPECTED` and `OBSERVED` disagree on a specific input in the
same units. You know `PUBLIC_SIGNATURE` and `CALLERS`.

### 3. Localize the defect

Open the asserting function. Usual suspects, in order:

- Constant scale on one side (`* 1000`, `/ 1024`, `* 8`) when both inputs share
  a unit.
- Comparison against a local that is not the value printed in the message.
- Flipped or off-by-one operator at the boundary.
- Argument-order swap at the call site.

Separate trigger, defect, and symptom. Point at one line that turns the log's
inputs into the log's message before editing.

### 4. Write the focused test and prove red

Smallest test that feeds the asserting function the log's exact values and
asserts intended behavior. Four checks work well:

- Log inputs pass (regression).
- Input exactly at the gate passes (boundary).
- Input clearly below the gate still raises (check not deleted).
- Public signature matches callers (`inspect.signature`).

Run `FOCUSED_COMMAND` on the unmodified harness. Need `VALID_RED` (failure text
matches `OBSERVED`). If `GREEN_BASELINE` or `WRONG_RED`, fix the model or the
test; do not patch yet.

### 5. Make the minimal fix

Change only the body of the asserting function so it compares what the
docstring and callers say. Keep:

- Name, parameters, order, defaults, annotations.
- Exception type and message format.
- Neighboring functions byte-for-byte.
- Recipe/SKU XML untouched.

Do not rescale the other side to match. Do not edit the gate in XML. Leave
extras (rename, cleanup, XML) out of this diff.

**Validation:** `git diff` touches only the asserting module and the new/updated
test; signature unchanged; no XML paths in the diff. Optionally run
`scripts/check_fix_scope.py` (inspect-only) against before/after copies of the
module.

### 6. Prove green

Same `FOCUSED_COMMAND` — all assertions pass. Run the nearest existing harness
test module. If the test changed after the fix, re-capture `VALID_RED` first.

### 7. Report

Use the format below.

## Stop conditions

Stop and report (do not fix) when:

- Verdict is `GENUINE_GATE_FAILURE`.
- You cannot obtain `VALID_RED`.
- The only fix changes the public signature or a recipe gate.
- The log does not localize to harness code.
- The log is too short and there is no harness checkout.
- The user insists extras ship in the same change — deliver the fix, decline
  the extras in the report.

## Report format

```text
Verdict:         <SUSPECT_HARNESS_ASSERT | GENUINE_GATE_FAILURE | MIXED | UNCLEAR>
Contract:        <recipe> gate <kind> <value> <unit>; measured <values> <unit>
Asserting fn:    <module.function> (<file>:<line>)
Root cause:      <trigger> -> <defect> -> <symptom>
Test:            <path>::<test name>
Red:             <revision>, `<command>`, <failure text>
Fix:             <one sentence>
Green:           <revision>, `<same command>`, <result>
Adjacent:        <module(s) run, result>
Unchanged:       public signature; recipe/SKU XML; <neighbors>
Declined:        <extras left out, or none>
Not covered:     <honest gap, or none>
```

## References and scripts

- `references/worked-example.md` — illustrative unit-scale (`* 1000`) walkthrough
  with placeholders (no packaged fail.log or gold tree).
- `scripts/check_fix_scope.py` — inspect-only AST scope check (stdlib). Compares
  before/after module copies; rejects signature changes, neighbor edits, XML
  touches, and oversized diffs.
