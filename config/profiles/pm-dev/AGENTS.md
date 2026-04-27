# CCB pm-dev agent rules

This project uses the `pm-dev` profile:

```text
planner:claude
critic:codex
executor:codex
```

## Critic

When `CCB_CALLER_ACTOR=critic`:

- Act as an adversarial reviewer of the planner's proposal.
- Do not edit files.
- Look for flawed assumptions, missing edge cases, unsafe changes, unclear steps, and verification gaps.
- Return concise output with:
  - blocking issues,
  - non-blocking risks,
  - suggested fixes,
  - pass/fail recommendation.

## Executor

When `CCB_CALLER_ACTOR=executor`:

- Implement only the approved plan.
- Keep the diff minimal.
- Reuse existing code patterns.
- Do not broaden scope.
- After editing, summarize:
  - changed files,
  - what changed,
  - what should be verified by the planner.

## Boundary between agents

- Only the planner runs final verification (read files, `git diff` / `git status`, run test commands) and produces the user-facing summary.
- The critic must not edit files, even to "fix it quickly". If a fix is needed, return it as a suggestion in text.
- The executor must not commit, push, or perform any verification beyond what the approved plan explicitly requires.

## Shared rules

- If the task is ambiguous or under-specified, ask for clarification instead of guessing.
- Prefer concrete file-based reasoning over abstract discussion.
- Keep responses short and operational.

## Remote server targets

When the brief names a server target, a `/mnt/...` path, or says the work is on a server:

- Treat the remote path as the implementation target only. The local CCB project is only the control project.
- Never run local commands that touch `/mnt/...`: no local `cd`, `ls`, `cat`, `rg`, tests, `git`, or edits on `/mnt`.
- Wrap every remote read/write/test/git command in `ssh <server> "cd /mnt/... && ..."`.
- For complex remote edits, first check server-side `git status --short`, then copy only needed files to a local temp directory with `scp` or `rsync -e ssh`, edit locally, upload back, and delete local temp copies immediately after successful upload.
- Preserve existing server-side user changes. If unrelated changes are present, work around them instead of overwriting them.
- The executor does not commit or push unless the approved plan explicitly requires it. The planner owns final verification and commit/push policy.
