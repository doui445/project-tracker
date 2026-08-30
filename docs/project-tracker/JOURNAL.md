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
- Open question raised: whether the versioning policy deserves its own file
  (see next action 2).
