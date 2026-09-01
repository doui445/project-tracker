# CLAUDE.md — project-tracker

Instructions for Claude working in this repo. This repo **is** the
`project-tracker` plugin; it also tracks itself (see `docs/project-tracker/`).

## What this is

A Claude Code plugin that bootstraps and maintains nine standard Markdown
tracking files for projects under configured scope roots, manages GitHub repo
creation, and regenerates a unified `PORTFOLIO.html`. Behaviour spec:
`skills/track/SKILL.md`.

## Layout

- `skills/track/SKILL.md` — the full behaviour specification (source
  of truth for how the skill acts).
- `skills/track/references/` — `backlog-phases.md`,
  `reminders-sync.md`, `writing-tracking-files.md`, and `i18n/{en,fr}.md`
  (the output-language catalogue).
- `skills/track/hooks/` — `session_start.sh`, `reminders_sync_trigger.sh`,
  `portfolio_regen.sh` (+ their `test_*.sh`). **Self-relative** — never
  hardcode `~/.claude/...` paths in them.
- `skills/track/scripts/` — `generate_portfolio.py` (stdlib only,
  no deps) + `test_generate_portfolio.py`, `build_installer.sh`.
- `.claude-plugin/{plugin,marketplace.json}`, `hooks/hooks.json` — plugin
  manifests. `test_plugin_manifest.py` at the root validates them.
- `commands/config.md` — the `/project-tracker:config` command.
- `install-project-tracker.sh` — generated installer for the no-marketplace
  path. Regenerate with `skills/track/scripts/build_installer.sh`,
  never hand-edit.
- `_dev-history/` — gitignored local specs and plans; keep French, do not ship.

## Conventions

- **Shipped strings are English.** Prose, comments, messages, generated HTML.
  Keep test fixtures ASCII/English. This is a review discipline (a "French
  sweep" you run by eye), not an automated in-repo gate.
- **No real names or personal data anywhere in the repo** — including the
  self-tracking files under `docs/project-tracker/`, which are committed and
  public. When a note needs to refer to one of the user's other projects,
  use a generic placeholder ("a dogfood project", "an external project", "a
  git sub-repo"), never the actual name, folder path, or Reminders-list name.
  `doui445` (the GitHub handle in the manifests and URLs) is the sole
  exception. Run this "names sweep" by eye alongside the French sweep before
  every commit.
- Deliberate French exceptions, whitelisted by any "is the shipped skill
  all-English" review:
  - `skills/track/references/i18n/` except `en.md` (the `fr.md`
    catalogue and any future non-English catalogue);
  - the `STRINGS["fr"]` table in
    `skills/track/scripts/generate_portfolio.py` (the portfolio's
    French UI strings);
  - the French assertions in
    `skills/track/scripts/test_generate_portfolio.py` (they check
    the `fr` rendering).
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
python3 -m unittest discover -s skills/track/scripts -p 'test_*.py'
bash skills/track/hooks/test_session_start.sh
bash skills/track/hooks/test_reminders_sync_trigger.sh
bash skills/track/hooks/test_portfolio_regen.sh
bash skills/track/scripts/build_installer.sh   # regenerate the installer after skill changes
```

## Git / GitHub

- `uses_git: true`, remote `origin` → `github.com/doui445/project-tracker`,
  default branch `main`.
- Never commit or push without explicit confirmation. Conventional-commit
  style messages (`skill:`, `hooks:`, `portfolio:`, `plugin:`, `docs:`,
  `test:`, `release:`).

## Releasing

**Version scheme** (this is a `0.x` project — major stays `0` until the skill
is declared stable):

- **minor** (`0.N.0`) — a new command, hook, config knob, or standard file, or
  any change to how the skill behaves.
- **patch** (`0.x.N`) — fixes, doc and guidance changes, refactors with no
  behaviour change.

**Routine** (every release):

1. Bump `version` in **both** `.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json` — kept equal, `test_plugin_manifest.py`
   enforces it.
2. Regenerate the installer: `bash skills/track/scripts/build_installer.sh`.
3. In `docs/project-tracker/CHANGELOG.md`: rename `[Unreleased]` to
   `[X.Y.Z] — YYYY-MM-DD`, add a fresh empty `[Unreleased]` above it.
   Update `STATUS.md` (version, next actions), append to `JOURNAL.md`, move
   any completed `BACKLOG.md` items, add a `DECISIONS.md` entry if the
   release settled a structural choice.
4. Run the tests (see Build / test).
5. Commit `release: vX.Y.Z — <summary>`, then
   `git tag -a vX.Y.Z -m "<summary>"`, then
   `git push origin main --follow-tags`.

## Phases

`phase_model: "superpowers"` — this repo uses the spec → plan flow, but the
specs and plans live in `_dev-history/{specs,plans}/` (gitignored, French),
not `docs/superpowers/`. Project preference; existing files are not migrated.

## Dogfooding note

This repo tracks itself. After a significant change, update
`docs/project-tracker/STATUS.md` (+ `JOURNAL.md`, and `CHANGELOG.md` /
`DECISIONS.md` / `ERRORS.md` where relevant) like any other tracked project.
