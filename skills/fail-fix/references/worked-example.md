# Worked example: unit-scale (`* 1000`) assert bug

**ILLUSTRATIVE** — placeholders only. Not a packaged gold case, not a real Diags
log, and not proprietary. Use this to see the shape of a fail-fix loop; apply
the skill against a real checkout.

## Scene (placeholders)

| Slot | Placeholder |
| --- | --- |
| Recipe | `<recipe>` |
| SKU | `<sku>` |
| Asserting module | `harness/<module>.py` |
| Asserting function | `assert_min_rate` (neutral stand-in name) |
| Gate | `min_gbps=900.0` |
| Measured | `952.3 GB/s` (healthy; clearly above the gate) |

Triage sketch from a short fail log:

- Recipe `<recipe>` demands `min_gbps=900.0`.
- Measured `952.3 GB/s` satisfies that gate.
- Innermost frame: `harness/<module>.py` in `assert_min_rate`.
- Message: `measured 952.3 GB/s below minimum 900.0 GB/s` — self-contradictory.

Verdict: `SUSPECT_HARNESS_ASSERT`.

## ILLUSTRATIVE before / after (~6-line assert)

Neutral names only. The defect is a one-sided scale on the gate while the
message still prints the unscaled value.

**Before (buggy):**

```python
def assert_min_rate(measured_gbps: float, min_gbps: float, *, label: str = "rate") -> None:
    """Fail if measured_gbps is below min_gbps. Both values are GB/s."""
    threshold = min_gbps * 1000  # BUG: gate already GB/s
    if measured_gbps < threshold:
        raise GateFailure(
            f"{label}: measured {measured_gbps:.1f} GB/s below minimum {min_gbps:.1f} GB/s"
        )
```

**After (minimal fix):**

```python
def assert_min_rate(measured_gbps: float, min_gbps: float, *, label: str = "rate") -> None:
    """Fail if measured_gbps is below min_gbps. Both values are GB/s."""
    if measured_gbps < min_gbps:
        raise GateFailure(
            f"{label}: measured {measured_gbps:.1f} GB/s below minimum {min_gbps:.1f} GB/s"
        )
```

Keep the public signature, exception type, and message format. Leave every
neighboring helper byte-for-byte. Do not touch recipe/SKU XML.

Root cause in the report shape: `trigger` (gate 900 enters) → `defect`
(`* 1000` before compare) → `symptom` (healthy measurement fails with a
self-contradictory message).

## Filled report template (illustrative)

```text
Verdict:         SUSPECT_HARNESS_ASSERT
Contract:        <recipe> gate min 900.0 GB/s; measured 952.3 GB/s
Asserting fn:    harness.<module>.assert_min_rate (harness/<module>.py:<line>)
Root cause:      gate 900 GB/s enters -> gate scaled * 1000 before compare -> healthy link fails with self-contradictory message
Test:            tests/test_<module>.py::test_passes_when_measured_above_gate
Red:             <failing-sha>, `python3 -m unittest tests.test_<module> -v`, GateFailure: ... 952.3 GB/s below minimum 900.0 GB/s
Fix:             Compare measured_gbps to min_gbps directly; drop the * 1000 scale.
Green:           <fixed-sha>, `python3 -m unittest tests.test_<module> -v`, all assertions pass
Adjacent:        nearest harness test module, same pass set as before
Unchanged:       public signature; recipe/SKU XML; neighboring assert helpers
Declined:        none
Not covered:     none
```

## Tempting wrong fixes (do not land these)

- **Rescale the measured side** (`measured_gbps * 1000 < threshold`). Same
  arithmetic as the real fix for this one call, but a second unit error; the
  next cleanup reintroduces the bug. The focused test cannot tell them apart —
  review the diff.
- **Edit the recipe/SKU gate** in XML. The gate was right; the comparison was
  wrong.
- **Flip the operator** (`<` → `<=` or the reverse) or loosen the boundary.
- **Rename or reorder** the public helper so callers break.
- **Touch a neighbor** or reformat the file in the same diff.

## Your first real gold case (checklist)

No packaged `fail.log` ships with this skill. Build one against the checkout
you have open:

1. **Redacted real log** — short text with recipe name, gate, measured values,
   and the innermost harness frame. Strip hostnames, serials, and anything
   proprietary beyond what the assert needs.
2. **Module at failing SHA** — open `harness/<module>.py` (or the real path) at
   the revision that produced the log; freeze `PUBLIC_SIGNATURE` and `CALLERS`.
3. **Focused test command** — smallest unittest/pytest that feeds the log's
   exact values; capture `VALID_RED` before you patch.
4. Run the workflow in `SKILL.md`; optionally
   `scripts/check_fix_scope.py --before ... --after ... --function ...`.
