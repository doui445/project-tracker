# ROADMAP — project-tracker

Prioritised synthesis. Raw detail (effort, value, technical notes) lives in
[`BACKLOG.md`](BACKLOG.md).

## Done

- **C1 — Standalone public repo** (2026-08-28): extracted from a private
  `~/.claude` skill into `github.com/doui445/project-tracker`.
- **C2 — English translation** (2026-08-29): every shipped string translated;
  machine values (frontmatter keys/values, file names, hook names, tags) left
  untouched.
- **C3 — Portfolio rework** (2026-08-30): single unified `PORTFOLIO.html`,
  category sections, configurable location (`portfolio.txt`) and title,
  deterministic hook-driven regeneration.
- **C4 — Plugin wiring** (2026-08-30): shipped as a Claude Code plugin
  (`hooks/hooks.json`), install-script path kept in parallel,
  `/project-tracker:config` command, `project:` pinned to the folder name.
  Released as **v0.3.0**. See [`CHANGELOG.md`](CHANGELOG.md).

## Current focus

No phase started yet — the backlog is short. Prioritised list:

### High

- **User-selectable output language (English / French)** for the tracking
  files and the portfolio. README stays whatever the user wrote it in.

### Low

- `SKILL.md` should state that tracking files are meant to be committed.
- Git release tags matching the manifest versions.

## Unprioritised ideas

None recorded yet — add to [`BACKLOG.md`](BACKLOG.md) as they come up.
