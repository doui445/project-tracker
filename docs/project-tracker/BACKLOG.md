# BACKLOG — project-tracker

Raw reservoir of every idea/feature envisaged. Never purged — enriched and
archived. Statuses: `[ ]` to do · `[~]` in progress · `[x]` done · `[-]`
abandoned. Effort S/M/L, value ⭐–⭐⭐⭐.

## High priority

- [ ] **User-selectable output language (English / French)** — effort M,
  value ⭐⭐⭐
  The tracking files and the generated portfolio should follow a language the
  user picks; for now English or French only. `README.md` is out of scope — it
  stays in whatever language the user wrote it.
  Open questions:
  - Where does the setting live? Machine-global
    (`~/.claude/project-tracker/language.txt`, same family as
    `scopes.txt` / `trackignore.txt` / `portfolio.txt`) vs. per-project
    (`STATUS.md` frontmatter key, e.g. `language: "fr"`) vs. both (global
    default, per-project override).
  - How does the skill consume it? A short instruction block near the top of
    `SKILL.md` selecting the prose language for everything it writes.
  - How does `generate_portfolio.py` consume it? It already has translatable
    strings (status labels, tagline, empty states, counts) — needs a small
    string table keyed by language, read from the config.
  - Default when unset: English (current behaviour), no migration of existing
    files.
  - Interaction with the "French-sweep gate" test — that gate exists to keep
    the *shipped skill* English; a French *tracking output* is a separate axis
    and must not trip it.

## Low priority

- [ ] **Git release tags** — effort S, value ⭐
  `plugin.json` / `marketplace.json` carry `0.1.0`…`0.3.0` but the repo has no
  tags. Tag retroactively and on every future bump.

- [ ] **`SKILL.md` should state that tracking files are meant to be committed**
  — effort S, value ⭐⭐
  The skill is currently silent on version-controlling `docs/project-tracker/`.
  Every user asks. Document the default (commit all nine), the reason (they are
  project memory + the collision safeguard needs `git diff` on `STATUS.md`),
  and the exception (gitignore `STATUS`/`JOURNAL`/`BACKLOG` only when the
  content is sensitive for a public repo). See `DECISIONS.md`
  (2026-08-30 — tracking files committed).

## How to use this backlog

Cycle: start a phase (pick coherent items, group them) → track progress
(`[~]`) → archive on closure (`[x]`, then move to a **Completed** section at
the bottom of this file). Phases are proposed, never automatic — see
`skills/project-tracker/references/backlog-phases.md`.
