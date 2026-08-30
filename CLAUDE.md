# CLAUDE.md — project-tracker

Instructions for Claude working in this repo. This repo **is** the
`project-tracker` plugin; it also tracks itself (see `docs/project-tracker/`).

## What this is

A Claude Code plugin that bootstraps and maintains nine standard Markdown
tracking files for projects under configured scope roots, manages GitHub repo
creation, and regenerates a unified `PORTFOLIO.html`. Behaviour spec:
`skills/project-tracker/SKILL.md`.

## Layout

- `skills/project-tracker/SKILL.md` — the full behaviour specification (source
  of truth for how the skill acts).
- `skills/project-tracker/references/` — `backlog-phases.md`, `reminders-sync.md`.
- `skills/project-tracker/hooks/` — `session_start.sh`, `reminders_sync_trigger.sh`,
  `portfolio_regen.sh` (+ their `test_*.sh`). **Self-relative** — never
  hardcode `~/.claude/...` paths in them.
- `skills/project-tracker/scripts/` — `generate_portfolio.py` (stdlib only,
  no deps) + `test_generate_portfolio.py`, `build_installer.sh`.
- `.claude-plugin/{plugin,marketplace.json}`, `hooks/hooks.json` — plugin
  manifests. `test_plugin_manifest.py` at the root validates them.
- `commands/config.md` — the `/project-tracker:config` command.
- `install-project-tracker.sh` — generated installer for the no-marketplace
  path. Regenerate with `skills/project-tracker/scripts/build_installer.sh`,
  never hand-edit.
- `_dev-history/` — gitignored local specs and plans; keep French, do not ship.

## Conventions

- **Shipped strings are English.** Prose, comments, messages, generated HTML.
  A "French-sweep" gate guards this — keep test fixtures ASCII/English.
- **Never translate machine values**: frontmatter keys and enum values
  (`active`, `"non"`, `"adopté"`, `"leger"`, `"superpowers"`, …), standard
  file names, hook names, `#tracker-sync`.
- **Never guess.** If a needed fact is missing, ask — a section stays marked
  "to fill in" rather than filled by assumption. This is the skill's own first
  principle; hold to it when editing the skill too.
- Version lives in **both** `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` — keep them in sync (a test enforces it).
  Bump on every release.

## Build / test

```bash
python3 -m unittest test_plugin_manifest
python3 -m unittest skills.project-tracker.scripts.test_generate_portfolio   # or run the file directly
bash skills/project-tracker/hooks/test_session_start.sh
bash skills/project-tracker/hooks/test_reminders_sync_trigger.sh
bash skills/project-tracker/hooks/test_portfolio_regen.sh
bash skills/project-tracker/scripts/build_installer.sh   # regenerate the installer after skill changes
```

## Git / GitHub

- `uses_git: true`, remote `origin` → `github.com/doui445/project-tracker`,
  default branch `main`.
- Never commit or push without explicit confirmation. Conventional-commit
  style messages (`skill:`, `hooks:`, `portfolio:`, `plugin:`, `docs:`,
  `test:`).

## Dogfooding note

This repo tracks itself. After a significant change, update
`docs/project-tracker/STATUS.md` (+ `JOURNAL.md`, and `CHANGELOG.md` /
`DECISIONS.md` / `ERRORS.md` where relevant) like any other tracked project.
