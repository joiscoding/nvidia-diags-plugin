---
name: fail-fix
description: >-
  Turn a short Diags fail log into a minimal, test-verified harness fix. Use
  when a recipe reports FAIL but the log shows the measurement meets the
  printed gate, or a harness assert or threshold helper looks wrong. Do not
  edit recipe or SKU XML. Not for refactors or cleanup.
---

# Fail-fix

A Diags run reports FAIL and the user gives you a short log. Decide whether
the harness compared the wrong values. If it did, change only that comparison
and add a focused test that failed before the change and passed after.

Do not rewrite recipe or SKU XML to make a run pass. Do not rename or reshape
public assert helpers that recipes call. Do not mix cleanup into the same
change.

## When

- A recipe FAILs and the log shows a gate and measured values that meet it
  (for example `952 GB/s below minimum 900 GB/s`).
- The innermost traceback frame is in a harness assert, threshold, or
  unit-conversion helper.
- The same SKU and recipe passed recently and only the harness changed.
- The user asks for a fix and a test for a harness assertion bug.

## When not

- Measured values are outside the gate. Report that and leave the harness
  alone.
- The ask is to loosen, tighten, or re-tune a gate. That belongs in the
  recipe or SKU.
- The ask is to refactor, rename, reformat, or modernize assertlib. That is
  a separate change.
- Diagnosis needs telemetry you do not have, such as fleet data, Splunk, or
  baselines.
- No executable harness is in reach. Triage only. Do not claim a fix.

## Required inputs

Find all of these before you edit. If one is missing, say which one and stop
at triage.

1. The fail log as short text.
2. The harness checkout at the failing revision.
3. The asserting function name from the traceback.
4. How harness tests run (`pytest`, `unittest`, or a runner script).
5. Any extras the user also wants.

## Sources of truth

Ranked. When they disagree, the higher one wins. Say so in the report.

1. The log's measured values and printed gate.
2. The recipe or SKU the log names. Read it. Do not edit it.
3. The asserting function's docstring and call sites.
4. The focused test you write.
5. Your reading of the code until a red test confirms it.

## Workflow

Each step ends with a check. Do not move on until that check holds.

### 1. Triage the log

By hand, or with `rg` and reading the file:

- Pull the recipe name, gate kind, value, unit, and every measured value.
- Find the innermost traceback frame in harness code.
- Check whether the failure message contradicts itself.

Verdict: `SUSPECT_HARNESS_ASSERT`, `GENUINE_GATE_FAILURE`, `MIXED`, or
`UNCLEAR`.

**Validation.** Write one sentence for what the recipe demanded, one for what
was measured, and one for which function raised. If the verdict is
`GENUINE_GATE_FAILURE`, report and stop.

### 2. Record the contract

Write this block and keep it unchanged through the fix:

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

**Validation.** `EXPECTED` and `OBSERVED` disagree on a specific input in the
same units. You know `PUBLIC_SIGNATURE` and `CALLERS`.

### 3. Localize the defect

Open the asserting function. Check these first:

- A constant scale on one side (`* 1000`, `/ 1024`, `* 8`) when both inputs
  share a unit.
- A comparison against a local that is not the value printed in the message.
- A flipped or off-by-one operator at the boundary.
- An argument-order swap at the call site.

Name the trigger, the defect, and the symptom. Point at one line that turns
the log's inputs into the log's message before you edit.

### 4. Write the focused test and prove red

Write the smallest test that feeds the asserting function the log's exact
values and checks the intended behavior:

- Log inputs pass.
- Input exactly at the gate passes.
- Input clearly below the gate still raises.
- Public signature matches callers (`inspect.signature`).

Run `FOCUSED_COMMAND` on the unmodified harness. You need `VALID_RED`, meaning
the failure text matches `OBSERVED`. If you get `GREEN_BASELINE` or
`WRONG_RED`, fix the hypothesis or the test. Do not patch yet.

### 5. Make the minimal fix

Change only the body of the asserting function so it compares what the
docstring and callers say. Keep:

- Name, parameters, order, defaults, and annotations.
- Exception type and message format.
- Neighboring functions byte-for-byte.
- Recipe and SKU XML untouched.

Do not rescale the other side to match. Do not edit the gate in XML. Leave
rename, cleanup, and XML edits out of this diff.

**Validation.** `git diff` touches only the asserting module and the new or
updated test. The signature is unchanged. No XML paths appear in the diff.
You can run `scripts/check_fix_scope.py` against before and after copies of
the module. The script only inspects.

### 6. Prove green

Run the same `FOCUSED_COMMAND`. All assertions pass. Run the nearest existing
harness test module. If the test changed after the fix, recapture `VALID_RED`
first.

### 7. Report

Use the format below.

## Stop conditions

Stop and report. Do not fix when:

- The verdict is `GENUINE_GATE_FAILURE`.
- You cannot obtain `VALID_RED`.
- The only fix changes the public signature or a recipe gate.
- The log does not localize to harness code.
- The log is too short and there is no harness checkout.
- The user insists extras ship in the same change. Deliver the fix and list
  the extras as declined in the report.

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
Not covered:     <gap, or none>
```

## References and scripts

- `references/worked-example.md` walks through a unit-scale (`* 1000`) bug
  with placeholders. It does not ship a fail.log or a gold tree.
- `scripts/check_fix_scope.py` inspects before and after copies of the module
  with the stdlib AST. It rejects signature changes, neighbor edits, XML
  edits, and oversized diffs.
