# CCB pm-dev workflow rules

This project uses the `pm-dev` CCB workflow profile with three agents:

```text
planner:claude; critic:codex; executor:codex
```

## Planner responsibilities

When `CCB_CALLER_ACTOR=planner`, follow this workflow for every non-trivial task:

1. Analyze the request and inspect the relevant files.
2. Write a concise implementation plan.
3. Send the plan to `critic` for adversarial review before any code change.
4. Revise the plan if the critic finds real issues.
5. Send the approved plan to `executor` for implementation.
6. After the executor reply arrives, the planner must NOT stop at "submitted". Re-read the changed files, inspect both `git diff` AND `git status --short` (untracked files do not show in `git diff`), run the smallest relevant verification command, and confirm the actual output matches the approved plan.
7. Output a final summary covering: which files changed, why this change, verification results (commands run + their output), and any residual risks or follow-ups.

## Delegation policy

- Use `ccb ask critic ...` / `ccb ask executor ...`.
- If `ccb` is not on PATH, ensure the CCB install's `bin/` directory is on PATH (typically `~/.local/bin`). Do NOT modify shell PATH from inside the workflow.
- Do not write the implementation directly when `executor` can perform it.
- Do not skip the critic step for non-trivial changes.

## Final verification

Before concluding a task, the planner must:

- read the changed files,
- inspect `git diff` AND `git status --short` (untracked files do not appear in `git diff`),
- if a target file is untracked, read its full content directly and confirm it matches the approved plan,
- run the smallest relevant test or command,
- state whether the executor output matches the approved plan.
