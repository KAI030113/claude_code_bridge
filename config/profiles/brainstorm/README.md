# brainstorm workflow profile

A CCB workflow profile for idea validation and decision-making before implementation.

| Agent | Provider | Role |
|---|---|---|
| `claude` | `claude` | Frames the problem, proposes ideas, coordinates critique, and synthesizes the final recommendation. |
| `codex` | `codex` | Challenges feasibility, assumptions, risks, and alternatives. |

## What this profile applies

When you run `ccb-profile-apply --name brainstorm` in a project, it writes:

- `.ccb/ccb.config` with `claude:claude; codex:codex`
- `CLAUDE.md` with the brainstorm coordination rules
- `AGENTS.md` with Codex critique rules
- A `.gitignore` block for CCB runtime state

This profile is intentionally non-implementation-oriented. Agents may inspect files to ground the discussion, but they should not edit files, commit, or push unless the user explicitly switches to an implementation workflow.

For server targets, agents may use SSH to inspect evidence, but they must not treat `/mnt/...` as a local path or edit remote files in brainstorm mode. Claude should include a rough debate-time estimate when the discussion is expected to take more than a few minutes.

## Switching from another profile

After switching an existing project to `brainstorm`, rebuild the runtime
layout before sending work:

```bash
ccb-profile-apply --name brainstorm --force
ccb config validate
ccb kill -f
ccb -n
ccb ps
```

Do not send `ccb ask claude ...` until `ccb ps` shows `claude` and `codex`
with live bindings. Stale or partial bindings usually mean the old runtime
layout is still mounted.
