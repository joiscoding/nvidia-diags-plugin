# NVIDIA Diags plugin

Cursor plugin with three skills for the NVIDIA Diags enablement. Templates Diags
testers can mimic for recipe / SKU workflows.

## Skills

| Skill | What it does |
| --- | --- |
| `pattern-clone` | Sibling complete recipe/gate → incomplete target. Match XML style. Diff only. Keep target sku / thresholds. |
| `fail-fix` | Fail log → minimal assert/harness patch. Do not rewrite the recipe. |
| `multi-file-rename` | Rename a symbol / step id across callers. No behavior change. Read the diff. |

## Install

Local: clone this repo, then add it as a local Cursor plugin (`.cursor-plugin/plugin.json` at the root).

Team marketplace: publish when you’re ready to share beyond the room.

## Status

v0.1.0 — all three skills have usable recipe bodies for the enablement. Fill examples
from the live demo fixtures (sibling/target XML, fail log, rename sites) as needed.
