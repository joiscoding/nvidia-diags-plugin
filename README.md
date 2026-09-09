# NVIDIA Diags plugin

Cursor plugin with three skills for the NVIDIA Diags enablement. Templates Diags
testers can mimic for recipe / SKU workflows.

## Skills

| Skill | What it does |
| --- | --- |
| `pattern-clone` | Sibling complete recipe/gate → incomplete target. Match XML style. Diff only. Keep target sku / thresholds. |
| `fail-fix` | Fail log to a minimal assert or harness patch. Do not rewrite the recipe. |
| `multi-file-rename` | Rename a Python symbol across callers. No behavior change. Read the diff. |

## Install

Local: clone this repo, then add it as a local Cursor plugin (`.cursor-plugin/plugin.json` at the root).

Team marketplace: publish when you are ready to share beyond the room.

## Status

- `pattern-clone` has a full skill body, including workflow and report.
- `fail-fix` and `multi-file-rename` ship `SKILL.md`, a `references/` worked
  example, and one inspect-only script each. They do not ship `evals/` or gold
  trees (`fail.log`, before/after fixtures). Point them at the Diags checkout
  you have open.
