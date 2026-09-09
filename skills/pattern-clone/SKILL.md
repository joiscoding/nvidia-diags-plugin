---
name: pattern-clone
description: >-
  Copy a missing diagnostic gate or recipe step from a complete sibling into
  an incomplete target. Follow local XML and shell style, and keep the target's
  identifiers and values.
---

# Pattern clone

Use Pattern Clone when a complete sibling has a gate, step, provider, or recipe
block that another target lacks.

Copy structure and style from the sibling. Keep the target's identity and
product values.

Do not use this workflow to refactor, clean up, rename, or redesign files. It
does not repair incorrect behavior in an existing block.

## Required inputs

Before editing, identify:

1. The complete sibling file and exact source block.
2. The target file and its missing capability.
3. The values that the target must keep.
4. The expected location and the blocks that should precede and follow it.

If the target lacks a required value, do not copy the sibling's value. Ask
which value applies.

If siblings implement the pattern differently, ask which one to follow.

## Sources of truth

- The sibling defines block shape, order, control flow, and local style.
- The target defines product identifiers, versions, counts, thresholds,
  addresses, feature settings, and existing transitions.
- The repository schema or parser defines valid XML.
- Nearby target code defines indentation, quoting, CDATA, and shell style.

Do not turn the target into a renamed copy of the sibling.

## Workflow

### 1. Confirm the missing block

Read both files before editing.

List the block IDs that the sibling has and the target lacks:

```bash
python3 <skill-dir>/scripts/inventory_holes.py \
  <sibling.xml> <target.xml>
```

Verify that the requested block exists in the sibling but not in the target.

### 2. State the plan

Before editing, write one sentence:

> Copy `<block-id>` from `<sibling>` into `<target>` between `<before>` and
> `<after>`, and change only `<known target differences>`.

Do not include cleanup or restructuring.

### 3. Copy the pattern

Copy the missing block only.

Match the sibling's block structure and the target's local style for:

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

Keep every existing target value.

Use the sibling's block ID and error code only if the recipe family shares
them. If each target allocates its own codes, follow the target's rules.

Use target variables instead of sibling literals. For example, use
`$WANT_ADAPTER_FW`, not the sibling's `12.40.1000`.

Do not change adjacent blocks unless one transition must point to the new
block.

### 5. Validate

Run the flow graph check:

```bash
python3 <skill-dir>/scripts/check_flow_graph.py <edited-target.xml>
```

Inspect the target-only diff. Confirm:

- the diff contains only the requested block and any required transition
- existing target blocks keep their order and content
- product identifiers, versions, counts, thresholds, and addresses stay intact
- the target contains no sibling-only literals
- every transition points to an ID present in the target or to `stop`
- the new block has the same relative position as in the sibling

These scripts read files. They do not modify recipes.

## Recipe conventions in the starter example

The example uses placeholder values in a Stage B firmware flow:

- `<flow>` has `<vars>` and ordered `<step>` elements.
- Steps may use `timeout`, `retry`, `when`, `on_pass`, `on_fail`, `on_skip`,
  and `code`.
- `stop` is a terminal transition.
- CDATA bodies contain shell commands plus `ERROR:`, `SET NAME=value`, and
  `RESULT PASS` or `RESULT FAIL`.
- The fixture does not define gate syntax. Copy `<gate>` grammar from the
  sibling or schema.

When this skill moves into a production repository, replace this section with
that repository's grammar.

## Worked example

The example has three files:

- `references/gold-pair/sibling_sku_recipe.xml`
- `references/gold-pair/target_sku_recipe.xml`
- `references/gold-pair/expected.diff`

`expected.diff` records the expected target change. The XML values are
placeholders.

## Stop conditions

Stop before editing if:

- no complete sibling exists
- the target-specific value is unknown
- siblings disagree on the pattern
- a transition destination is missing from the target
- the change requires new XML grammar
- the request has expanded into cleanup, renaming, or redesign

## Report

Return:

1. The sibling and target paths.
2. The block added and its location.
3. The target values kept.
4. Validation results.
5. The target-only diff.
