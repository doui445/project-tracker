# BACKLOG — project-tracker

Raw reservoir of every idea/feature envisaged. Never purged — enriched and
archived. Statuses: `[ ]` to do · `[~]` in progress · `[x]` done · `[-]`
abandoned. Effort S/M/L, value ⭐–⭐⭐⭐.

## Open

- [ ] **Nested tracking: an umbrella project with lightly-tracked git
  sub-repos** (L, ⭐⭐⭐) — surfaced by a dogfood run (2026-09-01). The user
  deliberately set up tracking on a *parent* folder that holds **one
  project**, not several: the parent is the global project (full 9 files,
  sessions always opened here), and the actual shipped units live in
  versioned sub-folders (an app, later a v2 or a second app) — those are what
  get pushed to GitHub. Today the skill
  only knows two cases for a sub-folder (own `STATUS.md` = separate project,
  never merged / no `STATUS.md` = orphan detail files, consolidated up). This
  is a third case: the parent's tracking should be able to **chaperone
  several real sub-projects** and reference their progress, while each git
  sub-repo gets its own **micro-tracking** — only what belongs in a public
  repo (a repo-facing `README.md`, optionally `ARCHITECTURE.md`, a
  `CHANGELOG.md`), committed alongside the code. Open design questions for
  the eventual brainstorm: which files exactly in a sub-repo and how minimal;
  how the parent detects/enumerates the sub-repos and shows their state in
  `STATUS.md` / `ROADMAP.md`; how `uses_git` coexists (parent `false`, child
  `true`); interaction with the git hooks (collision diff, commit offer,
  staleness) which currently only look at the tracked root; how this differs
  from the existing "ignored ancestor / whole-subtree" trade-off (here it is
  one project, not many). **Migration path** is part of this item: when the
  feature ships, already-tracked projects must be detected as
  pre-nested-model and re-prompted — a session opening in an existing tracked
  parent should offer to scan for git sub-repos and set up their
  micro-tracking (same shape as the `backlog_model` / `phase_model` /
  `category` retro-questions on `## Detecting a project's root`). Likely a new
  frontmatter key to mark "nested model seen / declined". Build the re-prompt
  mechanism as reusable infra, not a one-off. The user also wants this model
  applied to a second project later, and will feed back on it — a second real
  user of the feature.

- [ ] **Portfolio: a detail sub-page per project** (M, ⭐⭐) — requested
  2026-09-01. Today `PORTFOLIO.html` is a single aggregated page; the user
  wants to click through to a per-project sub-page for "where I'm at" instead
  of going to GitHub. Content: render what is already written —
  `STATUS.md` (state + next 3 actions), current `ROADMAP.md` phase, the last
  few `JOURNAL.md` entries, the latest `CHANGELOG.md` version. A direct
  GitHub link with the GitHub mark (inline SVG; `repo:` is already in the
  frontmatter). Open design questions for the brainstorm: one HTML file per
  project beside `PORTFOLIO.html` (a sub-folder?) vs. a single page with
  client-side routing; Markdown→HTML with no dependency (`generate_portfolio.py`
  is stdlib-only and has no MD renderer today); the `STRINGS` en/fr table must
  cover the new labels; keep v1 minimal (render existing content, resist
  charts/history creep). Pairs with nested tracking — a sub-page could list a
  project's git sub-repos and their micro-tracking state.

## Completed

- [x] **Plain-language pass on every question the skill asks** (0.11.0) — new
  `## Asking questions` principle (plain wording, per-option effect, a
  context-based **(recommended)** hint) + every bootstrap / first-run /
  phase / retranslation / un-exclude question reworded to match. `SKILL.md`,
  `references/backlog-phases.md`, `references/writing-tracking-files.md`.

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
