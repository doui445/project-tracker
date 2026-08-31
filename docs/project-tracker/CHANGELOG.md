# Changelog — project-tracker

All notable changes to this project. Format based on
[Keep a Changelog](https://keepachangelog.com/).

**Versioning.** A `0.x` project — `major` stays `0` until the skill is declared
stable. `minor` (`0.N.0`) = a new command, hook, config knob or standard file,
or any change to how the skill behaves. `patch` (`0.x.N`) = fixes, docs and
guidance, no-behaviour-change refactors. The version lives in
`plugin.json` / `marketplace.json` (kept equal); the release routine is in
`CLAUDE.md` § Releasing.

## [Unreleased]

## [0.8.0] — 2026-08-31

### Changed
- **Untracked project → the tracking question is asked automatically.** The
  `SessionStart` hook on a new folder now instructs Claude to open the
  session with a selectable **Yes / No, don't ask again / Not now** prompt
  (`AskUserQuestion`), instead of a passive "not tracked" note the user had
  to act on. "No" adds the folder to `trackignore.txt`; "Not now" writes
  nothing and the prompt returns next session. Excluded folders are
  unchanged — silent unless the user raises it.

## [0.7.1] — 2026-08-31

### Fixed
- `docs/project-tracker/JOURNAL.md` carried an absolute home path in the
  first bootstrap entry — genericised.
- `ROADMAP.md` was four releases stale (stuck at the v0.3.0 era) — rewritten
  to cover v0.4.0–v0.7.0.
- `CLAUDE.md` layout section listed only two reference files — added
  `writing-tracking-files.md` and `references/i18n/`; fixed the
  `test_generate_portfolio` command; the release routine now names the
  tracking-file updates.

### Changed
- `README.md` tidied: the install commands are no longer printed twice, the
  `STATUS.md` frontmatter example shows every key, and the fresh-eyes pass /
  un-exclude behaviours are listed.

## [0.7.0] — 2026-08-30

### Changed
- An **excluded** folder (in `trackignore.txt`) that the user asks to track
  is now offered an un-exclude + bootstrap, instead of leaving a manual
  `trackignore.txt` edit. If it is an *ancestor* that is ignored, Claude
  explains that un-ignoring the whole subtree is the only option and asks.
  Bringing the folder up for anything else is unchanged.

## [0.6.0] — 2026-08-30

### Added
- **Fresh-eyes readability pass.** After substantially writing or rewriting
  an onboarding file (`README.md` / `CLAUDE.md` / `ARCHITECTURE.md` /
  `GLOSSARY.md`), Claude runs a review pass — a subagent (inline fallback)
  checks it against the file's reader definition for a clear hook, a
  reachable quick start, jargon introduced before use, drift from the
  file's purpose, concreteness, and over-long sections. Advisory, never a
  gate; runs at bootstrap and on later rewrites. See
  `references/writing-tracking-files.md`.

## [0.5.0] — 2026-08-30

### Changed
- `GLOSSARY.md` is no longer asked at bootstrap. It is created on first
  need: a proactive check on the first session (Claude glances at the code
  / `README`, proposes the file with the terms it spotted if the project
  has a real vocabulary), plus in-session triggers — the user asks what a
  project-specific term means, or a term keeps coming up undefined. A
  single term is added and announced without a question; the proactive
  batch is proposed. New `glossary` frontmatter key (`"non"` = proactive
  scan declined; absent = not yet checked). `ARCHITECTURE.md` is still
  offered at bootstrap.

## [0.4.1] — 2026-08-30

### Changed
- `generate_portfolio.py` HTML escaping goes through `_attr()` / `_txt()`
  helpers chosen by context (attribute vs element text), so a future
  locale's apostrophes and quotes can't break an attribute or clutter a
  text node. No change to the rendered output for `en` / `fr`.
- `writing-tracking-files.md`: the stale "French repo → French tracking
  files" heuristic is replaced — the language is resolved from the
  settings, and a French repo is only a hint for the first-run question.
- `references/i18n/en.md` is stated as the source of truth for heading
  wording, its ROADMAP keys reconciled with `backlog-phases.md`
  (`in_progress` / `after` added, phase-dependence noted).
- `_normalise_lang` drops the off-spec `eng` / `fra` aliases; the accepted
  set is exactly the spec's (`en`/`english`/`anglais`,
  `fr`/`french`/`francais`/`français`), now covered by a test.

## [0.4.0] — 2026-08-30

### Added
- **User-selectable output language (English / French).**
  `~/.claude/project-tracker/language.txt` sets the machine default for the
  tracking files, the portfolio and the reminders; `language:` in a
  `STATUS.md` frontmatter overrides it for that project's files; a `language:`
  line in `portfolio.txt` overrides it for the portfolio. Per-language string
  catalogue `references/i18n/{en,fr}.md`; `generate_portfolio.py` renders its
  chrome (status labels, freshness, empty state, search, `<html lang>`) in the
  resolved language. Changing a project's language proposes a full
  retranslation (past append-only entries included, dates preserved) with an
  autonomous subagent review loop. Asked once at first bootstrap. `/project-tracker:config`
  gains a "Change the language" action. Default and fallback: `en`.
- Versioning policy written down: the scheme in this file's header, the
  release routine in `CLAUDE.md` § Releasing. `writing-tracking-files.md`
  points future projects to the same two homes (no dedicated file).

## [0.3.1] — 2026-08-30

### Added
- `references/writing-tracking-files.md` — per-file guidance on how to write
  each of the nine standard files (plus `ARCHITECTURE.md` / `GLOSSARY.md`):
  who the reader is, structure, what belongs and what doesn't, worked
  good/poor examples, and — for `ARCHITECTURE.md` — a lens for judging the
  architecture itself. `SKILL.md` points to it from "The standard files".
- `SKILL.md` now states that the tracking files are committed like any other
  source (with the narrow sensitive-content exception).
- Retroactive git tags `v0.1.0` / `v0.2.0` / `v0.3.0` (last commit of each
  version line); tagging is now part of the release routine.

### Fixed
- `SKILL.md` referenced "bootstrap step 6" for the optional
  `ARCHITECTURE.md` / `GLOSSARY.md` files — it is step 7.
- `build_installer.sh` had a hardcoded reference-file list; it now globs
  `references/*.md` so a new one is always bundled (see `ERRORS.md`).

### Changed
- README restructured for first-time readers: plain-language hook, a
  Quick start section up top, a tight "What you get", and the edge-case
  material (no-git mode, retrofit, concurrent sessions, optional files,
  frontmatter) moved into a "Details" section.
- README also documents `~`/`$VAR` expansion in the config files.
- `SKILL.md` § Portfolio now documents the `title:` line and the `.html`
  explicit-path tolerance of `portfolio.txt`.

## [0.3.0] — 2026-08-30

### Added
- `/project-tracker:config` command to view and change configuration
  (scopes, ignored paths, portfolio location/title, a project's category).
- Configurable portfolio title (`title:` line in `portfolio.txt`).

### Changed
- `project:` frontmatter is always the folder's own name — never asked.
- Skill no longer requests an `allowed-tools` grant.
- Audit fixes across the skill and hooks; installer regenerated.

## [0.2.0] — 2026-08-30

### Added
- Portfolio groups projects into sections by the `category` frontmatter
  field; bootstrap asks for a category.
- Portfolio location asked once at first bootstrap
  (`~/.claude/project-tracker/portfolio.txt`).

## [0.1.0] — 2026-08-30

### Added
- First Claude Code **plugin** release: `.claude-plugin/{plugin,marketplace}.json`
  + `hooks/hooks.json` bundle the skill and its three hooks (`SessionStart`,
  two `PostToolUse`). `install-project-tracker.sh` kept as a parallel path.
- Unified `PORTFOLIO.html` aggregating all tracked projects across every
  scope, regenerated by a deterministic `PostToolUse` hook.
- Self-relative hook scripts (work in plugin / skills-dir / script modes).
- `test_plugin_manifest.py`.

### Earlier

- 2026-08-29 — Full English translation of the shipped skill, hooks,
  portfolio generator and generated HTML.
- 2026-08-28 — Initial public release: extracted into the standalone repo
  `github.com/doui445/project-tracker`.
