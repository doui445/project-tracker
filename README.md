# project-tracker

A Claude Code skill that bootstraps and maintains a standard set of Markdown
tracking files for every project under configured scope roots — automatically
when you open a Claude Code session in a tracked folder, and on demand.

## What it does

- **Auto-detection** (`SessionStart` hook): when you open a Claude Code session
  in a folder covered by `scopes.txt`, a reminder is injected telling Claude
  whether the project is already tracked (and its current state) or new
  (bootstrap to propose). Folders listed in `trackignore.txt` stay silent.
- **Bootstrap**: asks about the goal, stack and git/GitHub handling — never
  guesses — then creates the nine standard files from your answers.
- **Continuous upkeep**: during a session, keeps `STATUS.md` current (state +
  next actions) and logs to `JOURNAL.md` / `CHANGELOG.md` / `DECISIONS.md` /
  `ERRORS.md` as appropriate.
- **GitHub** (optional): creates a private repo on request, or grafts onto an
  existing one — never commits or pushes without confirmation.
- **Apple Reminders sync** (optional, macOS): if a project is linked to a
  Reminders list, a `PostToolUse` hook triggers a deterministic sync check the
  first time `STATUS.md` / `ROADMAP.md` changes each session.
- **Portfolio**: regenerates a static `PORTFOLIO.html` at each scope root,
  listing every tracked project.

## The nine standard files

| File | Purpose |
|---|---|
| `README.md` (project root) | What, why, stack, install/run, links |
| `CLAUDE.md` (project root) | Instructions for Claude: conventions, build/test commands, known pitfalls |
| `docs/project-tracker/ROADMAP.md` | Prioritised synthesis: past phases, current phase, anticipated phases |
| `docs/project-tracker/STATUS.md` | Snapshot of the current state + machine-readable frontmatter. Rewritten every session |
| `docs/project-tracker/JOURNAL.md` | Dated chronological log. Append-only |
| `docs/project-tracker/CHANGELOG.md` | Keep a Changelog format |
| `docs/project-tracker/DECISIONS.md` | Why each structural technical choice, alternatives rejected. Append-only |
| `docs/project-tracker/ERRORS.md` | Bug → cause → fix, searchable. Append-only |
| `docs/project-tracker/BACKLOG.md` | Raw reservoir of every envisaged idea/feature. Append-only |

## Requirements

- **Claude Code**
- **Python 3** — standard library only, no dependencies
- **macOS + the `apple-reminders` MCP server** — only for the optional Reminders
  sync
- **The `gh` CLI** — only for the optional GitHub repo automation

## Install

```bash
git clone https://github.com/doui445/project-tracker ~/src/project-tracker
bash ~/src/project-tracker/install-project-tracker.sh
```

The installer:

- copies the skill to `~/.claude/skills/project-tracker/`
- registers the two hooks (`SessionStart`, `PostToolUse`) in
  `~/.claude/settings.json` with an idempotent merge
- creates `~/.claude/project-tracker/scopes.txt` and `trackignore.txt`
- runs the test suites

Then open a Claude Code session in a folder under one of your scope roots.

## Configuration

Two files in `~/.claude/project-tracker/`:

- **`scopes.txt`** — one absolute path per line. Everything under these roots
  gets auto-detection.
- **`trackignore.txt`** — one absolute path per line, to skip. An entry equal to
  a scope root ignores only that exact folder, not the projects inside it.

## How it behaves

The full behaviour specification lives in
[`skills/project-tracker/SKILL.md`](skills/project-tracker/SKILL.md)
*(currently in French — English translation in progress).*

## License

MIT — see [`LICENSE`](LICENSE).
