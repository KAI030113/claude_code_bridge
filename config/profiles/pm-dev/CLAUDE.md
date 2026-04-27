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
- verify against actual files, config, logs, command output, and git state instead of relying on assumptions or memory.
- when asked about prior experiments or historical behavior, inspect the relevant git history with `git log` / `git show` before drawing conclusions.
- if the brief requires a commit or push, do it only after final verification, use a concise commit message, and do not include `Co-Authored-By` or AI attribution.

## Remote server targets

When the brief names a server target, a `/mnt/...` path, or says the work is on a server:

- Keep CCB running from the local control project. The remote path is the implementation target, not a local directory.
- Never run local commands that touch `/mnt/...`: no local `cd`, `ls`, `cat`, `rg`, tests, `git`, or edits on `/mnt`.
- Wrap every remote read/write/test/git command in `ssh <server> "cd /mnt/... && ..."`.
- Before remote edits, check server-side `git status --short` and preserve existing user changes.
- For complex remote edits, prefer: `scp` or `rsync -e ssh` only the needed files to a local temp directory, edit locally, upload back, delete local temp copies immediately after successful upload, then verify on the server through SSH.
- The planner owns final remote verification, `git diff`, `git status --short`, commit, and push policy. The executor should not commit or push unless the approved plan explicitly says so.
