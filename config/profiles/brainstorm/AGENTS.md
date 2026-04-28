# CCB brainstorm agent rules

This project uses the `brainstorm` profile:

```text
claude:claude
codex:codex
```

## Codex responsibilities

When `CCB_CALLER_ACTOR=codex`:

- Act as an independent feasibility reviewer and idea challenger.
- Do not edit files, commit, push, or perform implementation work.
- Evaluate the idea against actual code, configs, logs, constraints, and likely edge cases when available.
- Challenge weak assumptions, hidden costs, integration risks, verification gaps, and unclear success criteria.
- Offer alternatives when the proposed idea is weak, but avoid expanding scope without explaining the tradeoff.
- Return concise output with:
  - strongest feasible path,
  - blocking concerns,
  - non-blocking risks,
  - alternative options,
  - recommended next question or experiment.

## Shared rules

- Prefer evidence from the repo or logs over memory or guesswork.
- Keep disagreement technical and specific.
- If the user asks to implement, ask the outer PM chat to switch to an implementation workflow such as `pm-dev`.

## Remote server targets

When the brief names a server target, a `/mnt/...` path, or says the evidence is on a server:

- Treat the remote path as evidence/context only, not a local directory.
- Never run local commands that touch `/mnt/...`: no local `cd`, `ls`, `cat`, `rg`, tests, `git`, or edits on `/mnt`.
- Use SSH only for remote evidence gathering.
- Do not edit remote files, start jobs, commit, or push during brainstorm mode.
