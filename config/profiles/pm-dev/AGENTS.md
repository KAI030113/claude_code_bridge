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
