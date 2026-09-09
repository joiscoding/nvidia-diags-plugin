---
name: multi-file-rename
description: >-
  Rename one Python symbol across every definition, import, alias, attribute
  call, and string reference in a Diags checkout with zero behavior change,
  then prove the old name is gone. Use for /multi-file-rename or "rename X to
  Y everywhere". Not for recipe XML step ids.
---

# Multi-file rename

Rename a Python symbol everywhere it is referenced, change nothing else, and
end with evidence that the old name is gone from Python and that the result
still runs. Output is a mechanical diff plus a short report.

Scope: Python symbols only. Do not rename recipe XML step ids, recipe keys, or
YAML config keys.

## When

- Rename one Python symbol used in more than one file:
  `compute_summary` to `compute_summary_v2`, `ResultRow` to `SummaryRow`,
  `DEFAULT_BATCH` to `DEFAULT_SUMMARY_BATCH`.
- Callers must update, not just the definition.
- No behavior change in the same pass.

## When not

- Recipe XML step ids, recipe keys, YAML config keys. Leave them untouched and
  list them in the report.
- Rename plus behavior change. Split into two diffs.
- Renaming a module or moving a file. That changes import paths and review
  scope.
- Repo-wide blind `sed`. Inventory first, then edit per file.
- Keeping the old name as a compatibility alias. That is a separate API
  decision.

## Required inputs

- **Old name and new name.** Exact spelling. Confirm the new name is not
  already bound: `rg --word-regexp <new> <root>`.
- **Kind of symbol.** Function, class, module-level constant, or method (scope
  methods to the class: `Runner.run` vs every `.run`).
- **Root.** Directory bounding the rename (default: repo root). Paths outside
  it are reported, not edited.
- **Test command.** Prefer `python3 -m unittest discover` or `pytest`. If
  nothing runs, say so in the report.

## Sources of truth

1. **The inventory.** `rg -n --word-regexp <old> <root>`. Every line is either
   changed or explained. Grep is the authority over any hand-picked file list.
2. **The Python import graph.** `from m import old`, `m.old`,
   `from m import old as alias`, `__all__`, `getattr(m, "old")`,
   `mock.patch("m.old")` / `patch.object(m, "old")`, entry points like
   `[project.scripts] name = "m:old"`. All bind or resolve the symbol; all
   change.
3. **The user's stated scope.** Narrows edits; never widens past the root.

Do not treat an IDE rename as complete. It skips string references. Grep anyway.

## Workflow

### 1. Inventory

```bash
rg -n --word-regexp <old> <root>
```

Whole-word matching matters: do not match `<old>_legacy` or `pre_<old>`.

### 2. Classify every hit

| Bucket | Examples | Action |
| --- | --- | --- |
| Definition | `def old(`, `class old`, `old = ...` | Rename |
| Import | `from m import old`, `from m import old as x` | Rename the symbol; leave local alias after `as` |
| Attribute / call | `m.old(...)`, `old(...)` | Rename |
| Python string reference | `__all__`, `patch.object(m, "old")`, `getattr(m, "old")`, `"m:old"` entry point | Rename |
| Descriptive string | log message or docstring naming the function | Rename; list for reviewer veto |
| Derived identifier | `OldNameTest`, `old_name_legacy` | Leave alone |
| External contract | CLI subcommand, metric key, recipe `<step id>`, YAML key | Leave alone; list under Out of scope |
| Non-Python file | `.xml`, `.yaml`, `.md`, `.cfg` | Leave alone unless a Python entry point |

If unsure whether a string is a Python reference or an external contract, leave
it and flag it. See `references/call-site-shapes.md` for one illustration per
row.

### 3. Edit file by file

Replace whole-word occurrences only in Rename buckets. Prefer targeted edits.
If using a mechanical tool, scope to inventoried Python files and word
boundaries, then re-read every diff:

```bash
sed -i 's/\bold_name\b/new_name/g' <classified.py files...>
```

Change nothing else. Do not reformat, sort imports, or make extra edits.

### 4. Verify

By hand or with the inspect script:

```bash
rg -n --word-regexp <old> --glob '*.py' <root>   # must be 0
rg -n --word-regexp <new> --glob '*.py' <root>   # must hit
# optional:
scripts/verify_rename.sh <old> <new> <root>
```

Then:

- Run the test command; same pass/fail set as before.
- `python3 -m compileall -q <root>` or import each touched module.
- `git diff --stat`: file list matches inventory Python files;
  insertions and deletions are roughly balanced.

Print non-Python hits from `rg` as informational for the report.

### 5. Report

Use the format below.

## Stop conditions

Stop and say why when:

- The new name is already bound under the root.
- The user bundles a behavior change, recipe XML edit, or compatibility shim.
  Do the rename and hand back the rest as a separate request.
- The user asks for repo-wide `sed` without an inventory. Show non-Python hits
  first, then proceed per file.
- An occurrence is outside the root. Report the path and do not edit it.
- Tests were red before you started. Record which tests failed and continue
  only if unrelated.
- No test or import check can run. Finish the rename and mark verification as
  "grep only".

## Report format

```markdown
## Rename: `<old>` to `<new>`

**Kind:** <function | class | constant | method on Class>
**Behavior change:** none. <signature / defaults / return shape unchanged>

### Inventory (before)
<N> occurrences in <M> files (<n_py> Python, <n_other> other).

| File | Occurrences | Kind |
| --- | --- | --- |
| ... | ... | definition / import / attribute / string / out of scope |

### Files changed (<count>)
- `path`. What changed.

### String occurrences changed (<count>)
- `path`. Which literal changed, and why it is a Python reference.

### Out of scope, unchanged (<count>)
- `path:line`. What it is and who owns it.

### Verification
- old-name grep in *.py returned 0 hits
- new-name grep in *.py returned <n> hits in <m> files
- <test command> returned <result, same as before>
- `git diff --stat` returned <files>, <+n>/<-n>

### Not done
- no compatibility alias for `<old>`
- derived identifiers left as they were: <list>
```

## References and scripts

- `references/call-site-shapes.md`. One before/after illustration per
  classification-table row (placeholder names only).
- `scripts/verify_rename.sh`. Inspect-only; exit 1 if `<old>` remains in
  `*.py` or `<new>` is absent; prints non-Python hits as informational.

## Applying in a real checkout

This skill is a template. Point it at the Python symbol in the Diags tree you
have open. It does not ship stand-in fixtures; do not invent a fake repo just
to run it.
