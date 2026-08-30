# project-tracker

Open a Claude Code session in one of your projects and it keeps a small set of
Markdown files — `STATUS.md`, `ROADMAP.md`, `JOURNAL.md`, `CHANGELOG.md`,
`DECISIONS.md` and a few more — current as you work, so you and Claude always
have the project's context in one predictable place. It also builds a single
`PORTFOLIO.html` across every project you track.

It's a Claude Code plugin (a skill + three hooks). It never guesses: anything it
doesn't know, it asks.

## Quick start

```
/plugin marketplace add doui445/project-tracker
/plugin install project-tracker@project-tracker
```

Restart Claude Code, then tell it which folders to watch — either run
`/project-tracker:config`, or edit `~/.claude/project-tracker/scopes.txt`
directly (one path per line, e.g. `~/code`).

Now open a session in any project under one of those folders. If it's new,
Claude offers to set it up (a handful of questions — goal, stack, git); if it's
already tracked, Claude picks up where the files left off.

## What you get

| File | Purpose |
|---|---|
| `README.md` *(project root)* | What, why, stack, install/run, links |
| `CLAUDE.md` *(project root)* | Instructions for Claude: conventions, build/test commands, pitfalls |
| `docs/project-tracker/STATUS.md` | Snapshot of the current state + next actions. Rewritten every session |
| `docs/project-tracker/ROADMAP.md` | Prioritised synthesis: past / current / anticipated phases |
| `docs/project-tracker/JOURNAL.md` | Dated log of what was done and why. Append-only |
| `docs/project-tracker/CHANGELOG.md` | Keep a Changelog format |
| `docs/project-tracker/DECISIONS.md` | Why each structural choice, alternatives rejected. Append-only |
| `docs/project-tracker/ERRORS.md` | Bug → cause → fix, searchable. Append-only |
| `docs/project-tracker/BACKLOG.md` | Raw reservoir of every envisaged idea. Append-only |

Plus, on top of the files:

- **A unified portfolio** — one `PORTFOLIO.html` aggregating every tracked
  project across all your scope roots, grouped by category, regenerated
  automatically whenever a `STATUS.md` changes.
- **Optional GitHub automation** — creates a private repo or grafts onto an
  existing one, on request. Never commits or pushes without confirmation.
- **Optional Apple Reminders sync** (macOS) — links a project to a Reminders
  list and keeps its next actions in sync both ways.
- **User-selectable EN/FR output** — the tracking files and the portfolio can
  be written in English or French, set once and overridable per portfolio or
  per project.
- **Never guesses** — a field it can't fill stays marked "to fill in" rather
  than invented.

## Requirements

- **Claude Code** — that's the only hard requirement.
- **Python 3** — standard library only, no dependencies (bundled, used by the
  portfolio generator).
- **The `gh` CLI** — only for the optional GitHub repo automation.
- **macOS + the `apple-reminders` MCP server** — only for the optional
  Reminders sync.
- **The `superpowers` plugin** — only if you want roadmap-phase plans written
  via its `writing-plans` skill; without it, phases use a lightweight
  `PHASE_N_SPEC.md` instead.

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

The installer copies the skill to `~/.claude/skills/project-tracker/`,
registers the three hooks in `~/.claude/settings.json` with an idempotent
merge, creates `scopes.txt` and `trackignore.txt`, and runs the test suites.
The `/project-tracker:config` command is only available with the plugin
install.

## Configuration

Up to four files in `~/.claude/project-tracker/`. The plugin/installer creates
`scopes.txt` and `trackignore.txt`; `portfolio.txt` appears the first time you
set a portfolio location, `language.txt` the first time you're asked for an
output language. In all of them, `~` and `$VAR` are expanded and `#` comments
are ignored.

- **`scopes.txt`** — one path per line. Everything under these roots gets
  auto-detection.
- **`trackignore.txt`** — one path per line, to skip. An entry equal to a scope
  root ignores only that exact folder, not the projects inside it.
- **`portfolio.txt`** — the folder where `PORTFOLIO.html` is written; an
  optional `title:` line sets its heading (default, locale-dependent: "My
  projects" / "Mes projets"), and an optional `language:` line (`en`/`fr`)
  overrides the output language for the portfolio only.
- **`language.txt`** — the machine-global output language for the tracking
  files and portfolio: `en` or `fr`, default `en`, asked once at first
  bootstrap.

`/project-tracker:config` (plugin install only) views and changes all of this
in plain language.

## Details

- **Works without git.** Pick "no git" at setup (`uses_git: false`) and
  everything still works — staleness is detected from file timestamps instead
  of `git log`.
- **Retrofit.** A project that already has ad-hoc tracking files (an existing
  `CLAUDE.md` / `JOURNAL.md`, `.pages` docs, a home-grown `BACKLOG.md`) is
  adopted by reusing what's there.
- **Concurrent sessions.** Before rewriting `STATUS.md`, it checks for an
  out-of-session change (via `git`, or the file's mtime) and asks rather than
  overwriting. The append-only files are only ever appended to.
- **Optional files.** `ARCHITECTURE.md` and `GLOSSARY.md` are created only if
  you ask for them at setup.
- **`STATUS.md` frontmatter.** The one structured part — what the portfolio
  reads:

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
  ---
  ```

The full behaviour specification lives in
[`skills/project-tracker/SKILL.md`](skills/project-tracker/SKILL.md).

## License

MIT — see [`LICENSE`](LICENSE).
