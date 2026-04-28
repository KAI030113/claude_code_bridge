# CCB workflow profiles

A **workflow profile** is a bundle of project-level files that configure a
CCB project for a specific multi-agent workflow. The bundle includes:

- `.ccb/ccb.config` (which providers, what agent names)
- `CLAUDE.md` (planner / claude-side rules)
- `AGENTS.md` (critic / executor / shared rules)
- A `.gitignore` block (idempotent, marked)

Profiles ship with the CCB install at
`<install-prefix>/config/profiles/<name>/` and are applied with the
`ccb-profile-apply` command.

## Available profiles

| Name | Layout | Notes |
|---|---|---|
| `pm-dev` | `planner:claude; critic:codex; executor:codex` | Strict plan → review → implement → verify loop. |
| `brainstorm` | `claude:claude; codex:codex` | Idea validation and feasibility debate before implementation. |

(Add new profiles by dropping a directory under `config/profiles/<name>/`.)

## Apply a profile

```bash
cd /path/to/your/project
ccb-profile-apply --name pm-dev
```

Use `brainstorm` when the goal is to compare approaches or test feasibility
before implementation:

```bash
ccb-profile-apply --name brainstorm
```

If `ccb-profile-apply` is not on PATH (the CCB installer normally
symlinks it into `~/.local/bin`), call it through the install prefix:

```bash
~/.local/share/codex-dual/bin/ccb-profile-apply --name pm-dev
```

If you used a custom install prefix, replace
`~/.local/share/codex-dual` with `$CODEX_INSTALL_PREFIX`.

## Switching profiles

If a project already has a running CCB namespace or was previously started
with another profile, overwrite the profile files and rebuild the runtime
layout before sending `ccb ask` jobs:

```bash
cd /path/to/your/project
ccb-profile-apply --name brainstorm --force
ccb config validate
ccb kill -f
ccb -n
ccb ps
```

`ccb ps` should show the selected profile's agent names with live bindings
before dispatch. If it shows stale agents, `partial`, `failed`, or only a
`cmd` pane, restart/rebuild the runtime first; do not submit the job yet.

## Options

| Flag | Effect |
|---|---|
| `--name <profile>` | Profile to apply. Required unless `--list`. |
| `--target <dir>` | Target project directory. Defaults to current directory. |
| `--force` | Overwrite existing files. Default is to skip existing files and report them. |
| `--dry-run` | Print planned actions without writing. |
| `--list` | List available profiles and exit. |

## Idempotence

- File copies are skipped if the destination already exists (use `--force` to overwrite).
- The `.gitignore` block is appended once with `# >>> ccb-profile <name>` / `# <<< ccb-profile <name>` sentinels. Re-running is a no-op.

## Boundary: what profiles do NOT carry

Profiles only emit **project-level** rules. They never embed:

- user-global rules from `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`,
- machine-specific paths (e.g. `/Users/<name>/...`, `/opt/homebrew/...`),
- server inventories, SSH host tables, proxies,
- API base URLs, tokens, or any secret.

Carry those in your outer task brief or in your global agent
configuration, not in the profile.

## Relationship to `config/claude-md-ccb.md`

CCB also ships static reference templates at `config/claude-md-ccb.md`
and `config/agents-md-ccb.md` describing a different role layout
(`designer / inspiration / reviewer / executor`). Profiles under
`config/profiles/` are an alternative path: pre-canned bundles that
`ccb-profile-apply` can drop into a project. The two mechanisms are
independent — pick the one you prefer; do not mix.
