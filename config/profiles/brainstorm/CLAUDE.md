# CCB brainstorm workflow rules

This project uses the `brainstorm` CCB workflow profile:

```text
claude:claude; codex:codex
```

## Purpose

Use this profile for product, research, design, architecture, and implementation strategy discussions before code changes. The goal is to compare ideas, test feasibility, surface tradeoffs, and converge on a recommendation.

## Claude responsibilities

When `CCB_CALLER_ACTOR=claude`:

1. Restate the problem, decision to make, constraints, and success criteria.
2. Propose one or more candidate ideas or approaches, plus a rough debate-time estimate if the discussion may take more than a few minutes.
3. Ask `codex` to challenge feasibility, assumptions, risks, missing constraints, and alternatives.
4. Revise the ideas after the Codex critique.
5. If important disagreement remains, run one more focused exchange instead of forcing agreement.
6. End with a clear synthesis: recommended option, rejected options and why, open questions, and what would be needed before implementation.

## Boundaries

- Do not edit files, run migrations, start services, commit, or push unless the user explicitly converts the brainstorm into an implementation task.
- You may inspect relevant files, configs, logs, or git history to ground the discussion.
- Do not present speculation as fact. Separate verified evidence from assumptions.
- Keep the final synthesis concise enough for the outer PM chat to decide next steps.

## Remote server targets

When the brief names a server target, a `/mnt/...` path, or says the evidence is on a server:

- Treat the remote path as evidence/context only, not a local directory.
- Never run local commands that touch `/mnt/...`: no local `cd`, `ls`, `cat`, `rg`, tests, `git`, or edits on `/mnt`.
- Use SSH only for remote evidence gathering.
- Do not edit remote files, start jobs, commit, or push during brainstorm mode.
