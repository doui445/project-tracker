# ROADMAP — project-tracker

Prioritised synthesis. Raw detail (effort, value, technical notes) lives in
[`BACKLOG.md`](BACKLOG.md).

## Done

Extraction and packaging (v0.1.0 – v0.3.1):

- **C1 — Standalone public repo** (2026-08-28): extracted from a private
  `~/.claude` skill into `github.com/doui445/project-tracker`.
- **C2 — English translation** (2026-08-29): every shipped string translated;
  machine values left untouched.
- **C3 — Portfolio rework** (2026-08-30): single unified `PORTFOLIO.html`,
  category sections, configurable location (`portfolio.txt`) and title,
  deterministic hook-driven regeneration.
- **C4 — Plugin wiring** (2026-08-30): shipped as a Claude Code plugin
  (`hooks/hooks.json`), install-script path kept in parallel,
  `/project-tracker:config` command, `project:` pinned to the folder name.
- **v0.3.1**: retroactive git tags, `SKILL.md` states tracking files are
  committed, `build_installer.sh` globs the reference files.

Features (v0.4.0 – v0.7.0):

- **v0.4.0 — User-selectable output language (EN/FR)**: `language.txt`
  machine default + `language:` overrides in `STATUS.md` frontmatter and
  `portfolio.txt`; per-language catalogue `references/i18n/{en,fr}.md`;
  localised `PORTFOLIO.html`; retranslation flow with a subagent review loop.
- **v0.4.1**: post-release cleanup — context-picked HTML escaping helpers,
  `en.md` as wording source of truth, spec-aligned language aliases.
- **v0.5.0 — Lazy `GLOSSARY.md`**: no longer asked at bootstrap; created on
  first need (proactive check + in-session triggers). New `glossary`
  frontmatter key.
- **v0.6.0 — Fresh-eyes readability pass**: after a substantial onboarding-file
  write/rewrite, a subagent (inline fallback) reviews it against the file's
  reader definition. Advisory.
- **v0.7.0 — Un-exclude on request**: an excluded folder the user asks to
  track is offered an un-exclude + bootstrap.

Detail for each: [`CHANGELOG.md`](CHANGELOG.md), [`DECISIONS.md`](DECISIONS.md).

## Current focus

No phase started. The `BACKLOG.md` reservoir is empty — every planned item has
shipped. The next themes will come from real use and dogfooding.

One soft item, not yet in the backlog: a full "fresh eyes" pass on
`README.md`, which grew across the v0.4.x–v0.7.0 releases.

## Unprioritised ideas

None recorded — add to [`BACKLOG.md`](BACKLOG.md) as they come up.
