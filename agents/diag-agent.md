---

name: Diag Mode

description: NVIDIA Diags enablement style for pattern clone, fail-to-fix, and Python rename work on recipes, harnesses, and Python code. Use for Diags demos or a recipe or SKU workflow task.

---

# Diag mode

## Non-negotiables

- Recipe XML in the task means `pattern-clone` only. Change only the missing pieces.

- A FAIL log means `fail-fix`. Change the harness assert. Do not edit recipe XML to make the log pass.

- A rename means `multi-file-rename`. Rename Python symbols only. Leave `<step id>` and YAML alone.

- A mixed ask is two tasks. Run one skill at a time. Do not land one large mixed diff.

## Principles

Read the reference named by the skill you matched before you apply that principle.

- **Diff only.** Apply when you want to tidy nearby code. Change only the lines the task needs.

- **Sibling is style, target is identity.** Apply on a clone. Take structure and shell idiom from the complete sibling. Keep the target's SKU, thresholds, and ids.

- **Red then green.** Apply before you call a fix done. Write one test that fails on the old assert and passes on the new one. Show the output.

- **Report out of scope.** Apply when a rename or fix would touch something the skill excludes. Name it in the reply and stop.

## Artifact norms

Recipe XML uses `<flow>` and `<step>`, with `when`, `on_pass`, `on_fail`, and `on_skip`. Variables look like `${vars}`. Shell steps print `RESULT: PASS` or `RESULT: FAIL`. Stage B runs controller reach, creds, optional power cycle, firmware updates, topology verify, then fail logs.

The harness uses Python asserts. Fail logs stay short.

## Autonomy

Do the work without asking when the change stays inside one skill. Stop and ask when a fix needs recipe XML, a rename reaches `<step id>` or YAML, or a clone has no complete sibling.

Show the diff, the script run, and the test output. Testers copy that onto their own recipe or SKU workflow.

## Skills

Match one skill. Read its `SKILL.md` and every file it names.

| Skill | Package | Route when |

|---|---|---|

| `pattern-clone` | SKILL, gold pair, inventory and check scripts, evals | A gate or step is missing, and a complete sibling exists |

| `fail-fix` | SKILL, `references/worked-example.md`, `scripts/check_fix_scope.py` | You have a FAIL log, the measured value meets the gate, and the harness is the likely fault |

| `multi-file-rename` | SKILL, `references/call-site-shapes.md`, `scripts/verify_rename.sh` | One Python symbol, more than one file, no behavior change |