# Worked example: unit-scale (`* 1000`) assert bug

Placeholders only. This is not a packaged gold case, not a real Diags log,
and not proprietary. Use it to see the shape of a fail-fix loop, then apply
the skill against a real checkout.

## Scene

| Slot | Placeholder |
| --- | --- |
| Recipe | `<recipe>` |
| SKU | `<sku>` |
| Asserting module | `harness/<module>.py` |
| Asserting function | `assert_min_rate` |
| Gate | `min_gbps=900.0` |
| Measured | `952.3 GB/s`, above the gate |

Triage from a short fail log:

- Recipe `<recipe>` demands `min_gbps=900.0`.
- Measured `952.3 GB/s` meets that gate.
- Innermost frame: `harness/<module>.py` in `assert_min_rate`.
- Message: `measured 952.3 GB/s below minimum 900.0 GB/s`. That contradicts
  the numbers.

Verdict: `SUSPECT_HARNESS_ASSERT`.

## Before and after

Names are stand-ins. The defect scales the gate on one side and still prints
the unscaled value in the message.

**Before.**

```python
def assert_min_rate(measured_gbps: float, min_gbps: float, *, label: str = "rate") -> None:
    """Fail if measured_gbps is below min_gbps. Both values are GB/s."""
    threshold = min_gbps * 1000
    if measured_gbps < threshold:
        raise GateFailure(
            f"{label}: measured {measured_gbps:.1f} GB/s below minimum {min_gbps:.1f} GB/s"
        )
```

**After.**

```python
def assert_min_rate(measured_gbps: float, min_gbps: float, *, label: str = "rate") -> None:
    """Fail if measured_gbps is below min_gbps. Both values are GB/s."""
    if measured_gbps < min_gbps:
        raise GateFailure(
            f"{label}: measured {measured_gbps:.1f} GB/s below minimum {min_gbps:.1f} GB/s"
        )
```

Keep the public signature, exception type, and message format. Leave every
neighboring helper unchanged. Do not edit recipe or SKU XML.

Root cause in the report shape: trigger (gate 900 enters), then defect
(`* 1000` before compare), then symptom (a healthy measurement fails with a
message that contradicts the numbers).

## Filled report template

```text
Verdict:         SUSPECT_HARNESS_ASSERT
Contract:        <recipe> gate min 900.0 GB/s; measured 952.3 GB/s
Asserting fn:    harness.<module>.assert_min_rate (harness/<module>.py:<line>)
Root cause:      gate 900 GB/s enters -> gate scaled * 1000 before compare -> healthy link fails with self-contradictory message
Test:            tests/test_<module>.py::test_passes_when_measured_above_gate
Red:             <failing-sha>, `python3 -m unittest tests.test_<module> -v`, GateFailure: ... 952.3 GB/s below minimum 900.0 GB/s
Fix:             Compare measured_gbps to min_gbps directly. Drop the * 1000 scale.
Green:           <fixed-sha>, `python3 -m unittest tests.test_<module> -v`, all assertions pass
Adjacent:        nearest harness test module, same pass set as before
Unchanged:       public signature; recipe/SKU XML; neighboring assert helpers
Declined:        none
Not covered:     none
```

## Wrong fixes

- Rescale the measured side (`measured_gbps * 1000 < threshold`). For this
  one call the arithmetic matches the real fix, but it adds a second unit
  error. The next cleanup can bring the bug back. The focused test cannot
  tell the two diffs apart, so read the diff.
- Edit the recipe or SKU gate in XML. The gate was right. The comparison was
  wrong.
- Flip the operator (`<` to `<=`, or the reverse) or loosen the boundary.
- Rename or reorder the public helper so callers break.
- Edit a neighbor or reformat the file in the same diff.

## First real gold case

This skill does not ship a `fail.log`. Build one against the checkout you
have open:

1. A redacted real log. Short text with recipe name, gate, measured values,
   and the innermost harness frame. Strip hostnames, serials, and anything
   proprietary beyond what the assert needs.
2. The module at the failing SHA. Open `harness/<module>.py` (or the real
   path) at the revision that produced the log. Record `PUBLIC_SIGNATURE`
   and `CALLERS`.
3. A focused test command. Smallest unittest or pytest that feeds the log's
   exact values. Capture `VALID_RED` before you patch.
4. Run the workflow in `SKILL.md`. You can also run
   `scripts/check_fix_scope.py --before ... --after ... --function ...`.
