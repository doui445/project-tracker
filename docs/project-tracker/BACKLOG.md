# BACKLOG — project-tracker

Raw reservoir of every idea/feature envisaged. Never purged — enriched and
archived. Statuses: `[ ]` to do · `[~]` in progress · `[x]` done · `[-]`
abandoned. Effort S/M/L, value ⭐–⭐⭐⭐.

## Open

- [ ] **Plain-language pass on every question the skill asks** — effort M,
  value ⭐⭐. Go through each question (bootstrap Q1–Q7, the first-run config
  questions, backlog/phase-model adoption, GLOSSARY proposal, retranslation,
  console view, un-exclude, retrofit): phrase it for a non-technical user;
  where a choice has consequences, say in one line what each option changes;
  add a **(recommended)** hint to the option that fits the detected context.
  Touches `SKILL.md`, `references/backlog-phases.md`. Raised 2026-09-01.

## Completed

- [x] **Excluded project: offer to un-exclude when the user asks to track it**
  (0.7.0) — when the user asks to track a `trackignore.txt`-excluded folder,
  Claude offers to remove the line + bootstrap (or, for an ignored ancestor,
  explains the whole-subtree trade-off). Bringing it up for anything else is
  unchanged.
- [x] **"Fresh eyes" readability pass on onboarding files** (0.6.0) — after a
  substantial write/rewrite of `README` / `CLAUDE.md` / `ARCHITECTURE.md` /
  `GLOSSARY.md`, a subagent (inline fallback) reviews it against the file's
  reader definition; advisory, never a gate; runs at bootstrap and on later
  rewrites. See `DECISIONS.md` (2026-08-30 — Fresh-eyes readability pass).
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
`skills/track/references/backlog-phases.md`.
