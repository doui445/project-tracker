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

_(nothing open)_

## Completed

- [x] **Git release tags** (0.3.1) — retroactive `v0.1.0` / `v0.2.0` /
  `v0.3.0` added at the last commit of each version line; `v0.3.1` tagged on
  release. Tagging folded into the release routine.
- [x] **`SKILL.md` states that tracking files are committed** (0.3.1) — added
  to "The standard files", with the narrow sensitive-content exception. See
  `DECISIONS.md` (2026-08-30 — tracking files committed).

## How to use this backlog

Cycle: start a phase (pick coherent items, group them) → track progress
(`[~]`) → archive on closure (`[x]`, then move to a **Completed** section at
the bottom of this file). Phases are proposed, never automatic — see
`skills/project-tracker/references/backlog-phases.md`.
