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

## Medium priority

- [ ] **`GLOSSARY.md`: lazy creation + enrichment loop** — effort M,
  value ⭐⭐
  Today `GLOSSARY.md` is created only if the user opts in at bootstrap step 7.
  Change to: not in the unconditional nine, but **created the first time an
  entry earns it** — same "materialise on need" logic as `phase_model` /
  phases. Triggers (any of):
  - the user asks Claude what a *project-specific* term means (jargon, coined
    term, overloaded common word — not general industry vocabulary) → Claude
    answers, then proposes adding it, with the project meaning + where it
    shows up + a usage example;
  - Claude, reading the code or docs (at bootstrap/retrofit or later on),
    sees the project carries a domain vocabulary of its own → proposes
    starting the glossary then, with the terms it already spotted;
  - Claude hits a recurring undefined term while working.
  Replaces the bootstrap step 7 question ("any domain jargon…?") with
  Claude's own judgment + a proposal. Single list, thematic grouping only if
  it grows (guidance already says this). Touches `SKILL.md` (§ Detecting a
  project's root, bootstrap step 7), `references/writing-tracking-files.md`,
  and the "nine standard files" framing in `README.md` / `SKILL.md`.

## Low priority

- [ ] **Excluded project: offer to un-exclude when the user asks to track it**
  — effort S, value ⭐
  A folder in `trackignore.txt` currently gets "do nothing unless the user
  brings it up". When the user *does* bring it up ("track this"), the skill
  should offer to remove the `trackignore.txt` line and run the bootstrap,
  rather than leaving the user to edit the file by hand (dogfooding friction,
  2026-08-30).

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
