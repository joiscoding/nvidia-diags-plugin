# NVIDIA Diags plugin

Cursor plugin with three skills for the NVIDIA Diags enablement. Templates Diags
testers can mimic for recipe / SKU workflows.

## Skills

| Skill | What it does |
| --- | --- |
| `pattern-clone` | Sibling complete recipe/gate → incomplete target. Match XML style. Diff only. Keep target sku / thresholds. |
| `fail-fix` | Fail log → minimal assert/harness patch. Do not rewrite the recipe. |
| `multi-file-rename` | Rename a Python symbol across callers. No behavior change. Read the diff. |

## Install

Local: clone this repo, then add it as a local Cursor plugin (`.cursor-plugin/plugin.json` at the root).

Team marketplace: publish when you’re ready to share beyond the room.

## Status

- `pattern-clone` — full skill body (workflow + report).
- `fail-fix` and `multi-file-rename` — middle-ground packages: `SKILL.md` +
  `references/` worked example + one inspect-only script each. No `evals/`, no
  gold trees (`fail.log`, before/after fixtures). Point them at the Diags
  checkout you have open.
