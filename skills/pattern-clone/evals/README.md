# Pattern Clone evals

These are authoring tests for the skill, not runtime instructions.

Each entry in `evals.json` contains:

- `prompt`: the task given to the agent
- `files`: input files supplied with that task
- `expected_output`: a short description of success
- `expectations`: statements used to grade the result

Run each prompt twice: once with `pattern-clone/SKILL.md` available and once
without it. Compare whether the skill prevents sibling values, unrelated
cleanup, and invalid transitions from entering the target.

These evals are intended for authoring and grading the skill by comparing
results with and without the skill enabled.

Do not give `expected.diff` to the executing agent. Reserve it for the grader
or human reviewer.
