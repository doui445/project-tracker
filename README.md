# project-tracker

A Claude Code skill that bootstraps and maintains a standard set of Markdown
tracking files for every project under configured scope roots — automatically
when you open a Claude Code session in a tracked folder, and on demand.

## What it does

- **Auto-detection** (`SessionStart` hook): when you open a Claude Code session
  in a folder covered by `scopes.txt`, a reminder is injected telling Claude
  whether the project is already tracked (and its current state) or new
  (bootstrap to propose). On an already-tracked project it may still ask once
  for anything never set (Reminders link, category, portfolio location).
  Folders listed in `trackignore.txt` stay silent.
- **Bootstrap**: asks about the goal, stack, git/GitHub handling, the Reminders
  link and a category — never guesses — then creates the nine standard files
  (plus optional `ARCHITECTURE.md` / `GLOSSARY.md`) from your answers.
- **Retrofit**: a project that already has ad-hoc tracking files (an existing
  `CLAUDE.md` / `JOURNAL.md`, `.pages` docs, a home-grown `BACKLOG.md`) is
  adopted by reusing what's there rather than starting from scratch.
- **Continuous upkeep**: during a session, keeps `STATUS.md` current (state +
  next actions) and logs to `JOURNAL.md` / `CHANGELOG.md` / `DECISIONS.md` /
  `ERRORS.md` as appropriate.
- **Concurrent sessions**: before rewriting `STATUS.md` it checks for an
  out-of-session change (via `git`, or the file's mtime) and asks rather than
  clobbering; the append-only files are only ever appended to.
- **Git / GitHub** (optional): works fully without git (`uses_git: false`,
  staleness detected from file timestamps); or creates a private GitHub repo on
  request, or grafts onto an existing one — never commits or pushes without
  confirmation.
- **Apple Reminders sync** (optional, macOS): if a project is linked to a
  Reminders list, a `PostToolUse` hook triggers a deterministic sync check the
  first time `STATUS.md` / `ROADMAP.md` changes each session.
- **Portfolio**: regenerates a single unified `PORTFOLIO.html` (all scopes,
  grouped by category) at the folder you configure in `portfolio.txt`.
- **Backlog & phases**: `BACKLOG.md` is a raw reservoir of every idea;
  coherent items get grouped into `ROADMAP.md` phases (always proposed, never
  automatic). Phase plans are written with the `superpowers` `writing-plans`
  skill when that plugin is available, otherwise as a lightweight
  `PHASE_N_SPEC.md`.

## The nine standard files

| File | Purpose |
|---|---|
| `README.md` (project root) | What, why, stack, install/run, links |
| `CLAUDE.md` (project root) | Instructions for Claude: conventions, build/test commands, known pitfalls |
| `docs/project-tracker/ROADMAP.md` | Prioritised synthesis: past phases, current phase, anticipated phases |
| `docs/project-tracker/STATUS.md` | Snapshot of the current state + machine-readable frontmatter (status, stack, category, …). Rewritten every session |
| `docs/project-tracker/JOURNAL.md` | Dated chronological log. Append-only |
| `docs/project-tracker/CHANGELOG.md` | Keep a Changelog format |
| `docs/project-tracker/DECISIONS.md` | Why each structural technical choice, alternatives rejected. Append-only |
| `docs/project-tracker/ERRORS.md` | Bug → cause → fix, searchable. Append-only |
| `docs/project-tracker/BACKLOG.md` | Raw reservoir of every envisaged idea/feature. Append-only |

Two more are created only if the bootstrap asks and you say yes:
`docs/project-tracker/ARCHITECTURE.md` and `docs/project-tracker/GLOSSARY.md`.

`STATUS.md` carries a machine-readable frontmatter block — the only structured
part, and what the portfolio reads:

```yaml
---
project: my-app          # always the folder name
status: active           # active | paused | blocked | archived
uses_git: true
repo: https://github.com/you/my-app
stack: [Python, FastAPI]
last_updated: 2026-08-30
next_milestone: "Ship the import flow"
reminders_list: "My app"   # or "non"
category: "Work"           # or "non"
backlog_model: "adopté"
phase_model: "superpowers" # or "leger"; absent until a phase is proposed
---
```

## Requirements

- **Claude Code**
- **Python 3** — standard library only, no dependencies
- **macOS + the `apple-reminders` MCP server** — only for the optional Reminders
  sync
- **The `gh` CLI** — only for the optional GitHub repo automation
- **The `superpowers` plugin** — only if you want phase plans written via its
  `writing-plans` skill; without it, phases fall back to a lightweight
  `PHASE_N_SPEC.md` format

## Install

### As a Claude Code plugin (recommended)

```
/plugin marketplace add doui445/project-tracker
/plugin install project-tracker@project-tracker
```

Restart Claude Code. The plugin bundles the skill and its three hooks
(`SessionStart` + two `PostToolUse`) — no manual `settings.json` edit.

Third-party marketplaces don't auto-update by default. To pick up a new
version: `/plugin marketplace update project-tracker` then
`/plugin update project-tracker` (or set `FORCE_AUTOUPDATE_PLUGINS=1`).

### With the install script (no marketplace)

```bash
git clone https://github.com/doui445/project-tracker ~/src/project-tracker
bash ~/src/project-tracker/install-project-tracker.sh
```

The installer:

- copies the skill to `~/.claude/skills/project-tracker/`
- registers the two `PostToolUse` hooks and the `SessionStart` hook in
  `~/.claude/settings.json` with an idempotent merge
- creates `~/.claude/project-tracker/scopes.txt` and `trackignore.txt`
- runs the test suites

The `/project-tracker:config` command is only available with the plugin install.

Either way, then open a Claude Code session in a folder under one of your
scope roots.

## Configuration

Up to three files in `~/.claude/project-tracker/`. The plugin/installer creates
the first two; `portfolio.txt` is created the first time you set a portfolio
location (its absence is the "not configured yet" signal). In all three, `~`
and `$VAR` are expanded, and `#` comments and blank lines are ignored.

- **`scopes.txt`** — one path per line. Everything under these roots gets
  auto-detection.
- **`trackignore.txt`** — one path per line, to skip. An entry equal to a scope
  root ignores only that exact folder, not the projects inside it.
- **`portfolio.txt`** — the folder where the unified `PORTFOLIO.html` is written
  (a path ending in `.html` is taken as an explicit file path); an optional
  `title:` line sets its heading (default: "My projects").

Run `/project-tracker:config` (plugin install only) to view and change any of
this in plain language.

## How it behaves

The full behaviour specification lives in
[`skills/project-tracker/SKILL.md`](skills/project-tracker/SKILL.md).

## License

MIT — see [`LICENSE`](LICENSE).
