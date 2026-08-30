# JOURNAL — project-tracker

Dated chronological log. Append-only.

## 2026-08-30 — Self-tracking bootstrap

- Removed `/Users/manu/Documents/Code/project-tracker` from
  `~/.claude/project-tracker/trackignore.txt` — the tool now tracks its own
  repo as a real project (auto-detection on, not manual-only).
- Bootstrapped the nine standard files in `docs/project-tracker/` + optional
  `GLOSSARY.md`. `README.md` kept as-is (English, already good); `CLAUDE.md`
  created at the root.
- Tracking-file language chosen: **English** (consistent with the repo and
  README). Reminders list **"Project tracker"** created and linked.
  Category: **Skill Claude**.
- Recorded the four completed build workstreams (C1–C4) and the v0.3.0 state
  in `STATUS.md` / `ROADMAP.md` / `CHANGELOG.md` / `DECISIONS.md`, grounded in
  git history and the local `_dev-history/` specs.
- Logged the requested improvement in `BACKLOG.md`: a user-selectable output
  language (English / French) for the tracking files and the portfolio.
- Decided: tracking files are committed, not gitignored (see `DECISIONS.md`).
  Added a backlog item to make `SKILL.md` say so explicitly.
- Created three Reminders in "Project tracker" from the `STATUS.md` next
  actions (backfill at linking).
- README gap fixed: `superpowers` was an undocumented optional dependency
  (phase plans via `writing-plans`). Added it to Requirements and a
  "Backlog & phases" bullet to "What it does".
- Full README audit against `SKILL.md` / `hooks.json` / `config.md`. Added:
  retrofit path, no-git mode, optional `ARCHITECTURE`/`GLOSSARY`, follow-up
  questions on tracked projects, concurrent-session handling, `~`/`$VAR`
  expansion, a `STATUS.md` frontmatter example. Fixed two `SKILL.md` issues
  (step 6 → 7; the `title:` line of `portfolio.txt` was undocumented in its
  own § Portfolio). Installer regenerated; manifest tests pass.
- README restructured for a first-time reader: the audit had turned it into a
  spec. Now opens with a plain hook + Quick start; "What you get" trimmed to
  the file table + four capabilities; edge cases (no-git, retrofit, concurrent
  sessions, optional files, frontmatter) collected under a "Details" section.
  Same substance, reordered.
- New `references/writing-tracking-files.md`: per-file writing guidance for all
  nine standard files + `ARCHITECTURE.md` / `GLOSSARY.md`. README and CLAUDE.md
  get good/poor contrasts; STATUS a belongs/doesn't-belong list; the
  append-only files get structure templates; ROADMAP/BACKLOG defer to
  `backlog-phases.md` for structure and only add prose notes; ARCHITECTURE
  also carries a lens for judging the architecture itself; GLOSSARY is framed
  as a real project dictionary (project meaning + usage context per entry).
  `SKILL.md` points to it from "The standard files".
- Fixed a latent bug found on the way: `build_installer.sh` had a hardcoded
  reference-file list — now globs `references/*.md`.
- Cleared the three low-priority items and cut **v0.3.1**:
  - `SKILL.md` now states the tracking files are committed (narrow
    sensitive-content exception).
  - Retroactive git tags `v0.1.0` / `v0.2.0` / `v0.3.0` at the last commit of
    each version line; `v0.3.1` tagged on this release.
  - Dogfood friction captured: the `build_installer.sh` bug is written up in
    `ERRORS.md`; the bootstrap itself and the hook chain (portfolio regen +
    reminders trigger firing on every `STATUS.md` write during a heavy dev
    session) worked as intended, just chatty by design.
  - `plugin.json` / `marketplace.json` → `0.3.1`, installer regenerated,
    `CHANGELOG` `[0.3.1]` dated.
- Versioning policy written down (decided against a dedicated file): the
  scheme lives in the `CHANGELOG.md` header, the step-by-step release routine
  in `CLAUDE.md` § Releasing. `writing-tracking-files.md` now points future
  projects to those two homes. Sits in `CHANGELOG [Unreleased]` — rides the
  next real release rather than triggering a 0.3.2 for two lines.
- Dogfooding review. The machinery worked; the frictions were doc gaps, and
  all the ones that were fixable are now fixed this session: `build_installer.sh`
  hardcoded list, the `title:` line missing from SKILL.md § Portfolio, the
  step 6→7 cross-reference, the silence on committing tracking files, the
  README drifting into spec. Two remaining threads logged to `BACKLOG.md`:
  `GLOSSARY.md` lazy creation + enrichment loop (medium), and offering to
  un-exclude a `trackignore.txt` folder when the user asks to track it (low).
- Correction to the entry above: the "hook chattiness / chatty by design"
  note was wrong. Checked the hooks — `portfolio_regen.sh` throttles to one
  run per 10s and injects no context (bar the once-per-session
  unconfigured-portfolio note); `reminders_sync_trigger.sh` fires once per
  session per project. Not a friction; the BACKLOG item was dropped. The
  `GLOSSARY.md` trigger list also gained "Claude spots a domain vocabulary
  while reading the code/docs → proposes the glossary then".
- New BACKLOG item (medium): a "fresh eyes" readability pass — after a
  substantial rewrite of README / ARCHITECTURE / GLOSSARY / CLAUDE, a
  subagent (fallback inline) reviews it against the reader definition and
  `writing-tracking-files.md`, advisory only. Prompted by this session's
  three README passes.

## 2026-08-30 — Output-language feature: design

- Brainstormed the user-selectable output language (EN/FR) and wrote the
  design spec at `_dev-history/specs/2026-08-30-output-language-design.md`
  (gitignored, French, per the project's `_dev-history/` convention).
- Key decisions: `language.txt` global default + `language:` overrides in
  `STATUS.md` frontmatter (per project) and `portfolio.txt` (portfolio only);
  reminders always follow the global; chat follows the conversation. Full
  localisation of the tracking files via a per-language catalogue
  `references/i18n/{en,fr}.md`; `generate_portfolio.py` gets its own `STRINGS`
  table. Language change → proposed full retranslation (append-only entries
  included, dates preserved) with an autonomous subagent review loop.
- Set `phase_model: "superpowers"` (records the de-facto workflow; specs/plans
  stay in `_dev-history/`, no migration). Targets v0.4.0.
- Next: user reviews the spec, then `writing-plans`.
