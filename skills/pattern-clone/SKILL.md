---
name: pattern-clone
description: >-
  Add a missing diagnostic gate or recipe step to an incomplete SKU, board,
  or firmware target by adapting a complete sibling while matching local
  XML and shell style and preserving target-specific identifiers and values.
---

# Pattern Clone

Use Pattern Clone when one complete sibling already contains a gate, step,
provider, or recipe block that an incomplete target should also contain.

The sibling is the source of structure and style. The target is the source of
identity and product-specific values.

Do not use this workflow for broad refactors, cleanup, renaming, redesign, or
fixing an existing block whose behavior is wrong.

## Required inputs

Identify before editing:

1. The complete sibling file and exact source block.
2. The incomplete target file and the missing capability.
3. The target-specific values that must remain unchanged.
4. The target's expected placement and control-flow neighbors.

If the target does not define a required value, do not copy the sibling's value
as a guess. Stop and ask which value applies.

If several siblings implement the pattern differently, stop and ask which one
is authoritative.

## Sources of truth

- Use the sibling for block shape, ordering, control flow, and local style.
- Use the target for SKU IDs, board names, firmware versions, counts,
  thresholds, addresses, feature settings, and existing transitions.
- Use the repository's schema or parser for supported XML grammar.
- Use surrounding target code to settle indentation, quoting, CDATA, and shell
  conventions.

Never make the target a renamed copy of the sibling.

## Workflow

### 1. Confirm the hole

Read the sibling and target before editing.

When available, inventory missing block IDs:

```bash
python3 <skill-dir>/scripts/inventory_holes.py \
  <sibling.xml> <target.xml>
```

Confirm that the requested block is present in the sibling and absent from the
target.

### 2. State the plan

Before editing, state one sentence:

> Copy `<block-id>` from `<sibling>` into `<target>` between `<before>` and
> `<after>`, adapting only `<known target deltas>`.

Do not add cleanup or restructuring to this plan.

### 3. Copy the pattern

Copy only the missing block.

Match the sibling and surrounding target in:

- element and attribute order
- indentation and blank lines
- quoting and variable expansion
- CDATA and shell layout
- `ERROR:` messages
- `RESULT PASS` and `RESULT FAIL` behavior
- `SET NAME=value` behavior
- `when`, `on_pass`, `on_fail`, and `on_skip` structure
- relative position in the recipe

Do not edit the sibling.

### 4. Adapt only proven differences

Preserve every existing target-specific value.

Use the sibling's new block ID and error code only when those values identify
the shared check across the recipe family. If codes are allocated per target,
use the target's allocation rules instead.

Reference target variables rather than copying sibling literals. For example,
copy `$WANT_ADAPTER_FW`, not the sibling's `12.40.1000`.

Do not change neighboring blocks unless the new block requires one explicit
transition update.

### 5. Validate

Check the edited target:

```bash
python3 <skill-dir>/scripts/check_flow_graph.py <edited-target.xml>
```

Then inspect the target-only diff and confirm:

- only the requested block and necessary transition changed
- no existing target block was reordered or rewritten
- SKU, board, firmware, count, address, and threshold values stayed intact
- no sibling-specific literal leaked into the target
- every transition points to an ID present in the target or to `stop`
- the new block occupies the same relative position as in the sibling

Scripts in this skill inspect files only. They never rewrite recipes.

## Recipe conventions in the starter example

The supplied example uses Dani's obfuscated Stage B conventions:

- `<flow>` contains `<vars>` and ordered `<step>` elements.
- Steps may use `timeout`, `retry`, `when`, `on_pass`, `on_fail`, `on_skip`,
  and `code`.
- `stop` is a terminal transition.
- CDATA bodies use shell plus `ERROR:`, `SET NAME=value`, and
  `RESULT PASS` or `RESULT FAIL`.
- Gate syntax was not provided. For a real `<gate>`, copy its grammar from the
  authoritative sibling or schema rather than inventing it.

Replace this section with the real repository grammar when available.

## Worked example

Before adapting this skill to a real repository, read:

- `references/gold-pair/sibling_sku_recipe.xml`
- `references/gold-pair/target_sku_recipe.xml`
- `references/gold-pair/expected.diff`

They demonstrate the intended change shape, not production firmware values.

## Stop conditions

Stop before editing when:

- no complete sibling exists
- the target-specific value is unknown
- siblings disagree on the pattern
- a transition destination is missing from the target
- the change requires new XML grammar
- the request has expanded into cleanup, renaming, or redesign

## Report

Return:

1. The sibling and target used.
2. The block added and its placement.
3. The target-specific values preserved.
4. Validation results.
5. The small target-only diff.
