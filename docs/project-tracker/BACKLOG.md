# BACKLOG — project-tracker

Raw reservoir of every idea/feature envisaged. Never purged — enriched and
archived. Statuses: `[ ]` to do · `[~]` in progress · `[x]` done · `[-]`
abandoned. Effort S/M/L, value ⭐–⭐⭐⭐.

## Medium priority

- [ ] **"Fresh eyes" readability pass on onboarding files after a substantial
  rewrite** — effort M, value ⭐⭐
  After Claude substantially rewrites `README.md` (or `ARCHITECTURE.md` /
  `GLOSSARY.md` / `CLAUDE.md`), run a review pass before moving on. Motivation:
  this session took three passes on the README because the spec-drift was only
  caught after the fact.
  - **Mechanism:** a subagent (fresh eyes — Claude re-reading what it just
    wrote sees what it *meant*, not what it wrote), given the new file + the
    diff + the reader definition and rules from
    `references/writing-tracking-files.md`. Returns a short list of concrete
    issues or "reads well". Fallback when subagents aren't available: an
    inline top-to-bottom re-read against the reader definition.
  - **Checks:** clear hook up top? target reader finds what they need fast?
    jargon used before it's introduced? drifted from the file's purpose
    (README → spec)? concrete enough? over-long anywhere?
  - **Advisory, never a gate.** Claude decides what to apply and shows the
    user.
  - **Trigger:** Claude's judgment — a substantial rewrite/restructure, not a
    one-line fix. Scope limited to README / ARCHITECTURE / GLOSSARY / CLAUDE.
  - Touches `SKILL.md` (§ Continuous updates) and
    `references/writing-tracking-files.md`.

## Low priority

- [ ] **Excluded project: offer to un-exclude when the user asks to track it**
  — effort S, value ⭐
  A folder in `trackignore.txt` currently gets "do nothing unless the user
  brings it up". When the user *does* bring it up ("track this"), the skill
  should offer to remove the `trackignore.txt` line and run the bootstrap,
  rather than leaving the user to edit the file by hand (dogfooding friction,
  2026-08-30).

## Completed

- [x] **`GLOSSARY.md`: lazy creation + enrichment loop** (0.5.0) — dropped
  the bootstrap question; the file is created on first need via a proactive
  first-session check plus in-session triggers (user asks a term's meaning,
  or a term recurs undefined). New `glossary` frontmatter key. See
  `DECISIONS.md` (2026-08-30 — GLOSSARY.md lazily created).
- [x] **User-selectable output language (English / French)** (0.4.0) —
  `~/.claude/project-tracker/language.txt` (machine default) + `language:`
  overrides in `STATUS.md` frontmatter (per project) and `portfolio.txt`
  (portfolio); reminders follow the global; chat follows the conversation.
  Per-language catalogue `references/i18n/{en,fr}.md` (+ key-parity guard);
  a separate Python `STRINGS` table (+ its own guard) localizes
  `PORTFOLIO.html`. Language change → proposed full retranslation with an
  autonomous subagent review loop. `/project-tracker:config` gains a
  "Change the language" action. Default and fallback: `en`. Spec +
  plan in `_dev-history/{specs,plans}/2026-08-30-output-language*`.
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
