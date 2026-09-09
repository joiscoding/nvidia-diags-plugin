# Pattern clone evals

These files test skill behavior. They are not runtime instructions.

Each entry in `evals.json` contains:

- `prompt`: the task the agent receives
- `files`: input files the agent receives
- `expected_output`: a short description of a correct result
- `expectations`: statements the grader checks

Run each prompt once with `pattern-clone/SKILL.md` available and once without
it. Compare the outputs. With the skill, the agent should not copy sibling-only
values, make unrelated edits, or create unresolved transitions.

Keep `expected.diff` out of the agent input. It is the answer key for the
grader.
