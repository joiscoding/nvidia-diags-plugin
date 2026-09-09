# NVIDIA Diags plugin

Cursor plugin with three skills for the NVIDIA Diags enablement. Templates Diags
testers can mimic for recipe / SKU workflows.

## Why

The Diags room (~20 eng) runs three live demos. Packaging them as skills means
the same moves are reusable after the session, and you can drop this into a team
marketplace later.

## Skills

| Skill | What it does |
| --- | --- |
| `pattern-clone` | Sibling complete recipe/gate → incomplete target. Match XML style. Diff only. Keep target sku / thresholds. |
| `fail-fix` | Fail log → minimal assert/harness patch. Do not rewrite the recipe. |
| `multi-file-rename` | Rename a Python symbol across callers. No behavior change. Read the diff. |

Skills vs Agents vocabulary is **not** in this plugin — that framing is slides-only.

## Install

Local: clone this repo, then add it as a local Cursor plugin (`.cursor-plugin/plugin.json` at the root).

Team marketplace: publish when you’re ready to share beyond the room.

## Status

- `pattern-clone` — full skill body (workflow + report).
- `fail-fix` and `multi-file-rename` — middle-ground packages: `SKILL.md` +
  `references/` worked example + one inspect-only script each. No `evals/`, no
  gold trees (`fail.log`, before/after fixtures). Point them at the Diags
  checkout you have open.
