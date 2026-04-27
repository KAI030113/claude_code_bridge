# pm-dev workflow profile

An alternative CCB workflow profile that uses three agents in a strict
plan -> review -> implement -> verify loop:

| Agent | Provider | Role |
|---|---|---|
| `planner` | `claude` | Owns the plan and the final user-facing summary; verifies executor output. |
| `critic` | `codex` | Adversarial reviewer. Must not edit files. |
| `executor` | `codex` | Implements only the approved plan. Must not commit or push. |

This profile is independent from the `designer/reviewer/executor` role
mapping defined in `config/agents-md-ccb.md` and `config/claude-md-ccb.md`.
Pick whichever fits your project; do not mix them in the same project.

## What this profile applies

When you run `ccb-profile-apply --name pm-dev` in a project, it writes:

- `.ccb/ccb.config` with `planner:claude; critic:codex; executor:codex`
- `CLAUDE.md` with the planner workflow rules (analyze, plan, critic review, executor delegation, final verification, final summary)
- `AGENTS.md` with the critic/executor/boundary/shared rules
- A `.gitignore` block (idempotent) ignoring `.ccb/` runtime state while keeping `.ccb/ccb.config` trackable, plus `.claude/` and Python bytecode

By design this profile only emits **project-level** rules. It does NOT
embed any user-global rules, machine-specific paths, server inventories,
proxy URLs, or API base URLs. Carry those in your outer task brief or
your global agent settings, not in the profile.

## Boundary

- `pm-dev` is one workflow shape. Other CCB users may prefer the
  `designer/reviewer/executor` shape from the static templates under
  `config/`. They coexist; users choose at apply time.
- The applier never touches files it did not create unless invoked with
  `--force`. The `.gitignore` fragment is appended once with sentinel
  markers and is idempotent.
