# JOURNAL — project-tracker

Dated chronological log. Append-only.

## 2026-08-30 — Self-tracking bootstrap

- Removed this repo's own path from
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

## 2026-08-30 — Output-language feature shipped (v0.4.0)

- Implemented per `_dev-history/plans/2026-08-30-output-language.md`:
  `language.txt` + `language:` overrides, `references/i18n/{en,fr}.md`
  catalogue, localized `generate_portfolio.py`, retranslation + subagent
  review loop, `/project-tracker:config` language action.
- `phase_model: "superpowers"` recorded; specs/plans stay in `_dev-history/`.

## 2026-08-30 — Output-language feature landed on main (v0.4.0)

- Executed `_dev-history/plans/2026-08-30-output-language.md` via
  subagent-driven development in an isolated worktree: 10 tasks, one
  fresh implementer + task review each, an opus whole-branch review, one
  fix wave (2 Critical + 5 Important + minors) and a scoped re-review.
- The worst bug the whole-branch review caught: `load_portfolio_target()`
  ignored the new `language:` reserved key, so a `language:` line above the
  path in `portfolio.txt` silently redirected `PORTFOLIO.html` into a bogus
  directory. Fixed with a shared `_RESERVED_PORTFOLIO_PREFIXES` + a
  regression test writing the `language:` line first.
- Fast-forwarded to `main`, tagged `v0.4.0`, pushed. 87 portfolio tests +
  8 manifest + 3 hook suites green on the merged result.
- `BACKLOG.md`: the output-language item moved to Completed.
  `DECISIONS.md`: added the D1–D15 rationale entry.

## 2026-08-30 — Post-v0.4.0 residual cleanup

- Final-review residuals cleared: `generate_portfolio.py` now routes every
  HTML escape through `_attr()` / `_txt()` helpers picked by context, so
  adding a locale can't get attribute-vs-text escaping wrong (new
  `test_escaping_convention_text_vs_attribute` guards it). The vestigial
  "French repo → French tracking files" heuristic in
  `writing-tracking-files.md` — dead since the resolution cascade always
  resolves — is reframed as a hint for the first-run question only.
- 88 portfolio tests + 8 manifest + hook suites green; installer regenerated.

## 2026-08-30 — Last two low-priority residuals cleared

- `_normalise_lang`: removed the off-spec `eng`/`fra` aliases (ISO 639-2);
  the tolerance list now matches the spec exactly, with a test.
- `references/i18n/en.md`: declared the source of truth for heading wording
  (structure still owned by `SKILL.md` / `writing-tracking-files.md` /
  `backlog-phases.md`); its ROADMAP keys reconciled with `backlog-phases.md`
  — added `roadmap.heading.in_progress` and `.after` (was a bare `.next`),
  noted that headings 2–3 depend on whether a phase has started. `fr.md`
  follows; parity guard green (89 portfolio tests).

## 2026-08-30 — v0.4.1 released

- Patch release: the four post-v0.4.0 cleanup entries from `[Unreleased]`
  (escaping helpers, French-repo heuristic, `en.md` source of truth,
  `_normalise_lang` spec alignment). No behaviour change. `v0.4.1` tagged
  and pushed; 89 portfolio + 8 manifest + hook suites green.

## 2026-08-30 — v0.5.0: GLOSSARY.md lazy creation

- `GLOSSARY.md` no longer asked at bootstrap. Created on first need:
  proactive first-session check (Claude glances at code/README, proposes it
  with spotted terms) + in-session triggers (user asks a term's meaning, or
  a term recurs undefined). Single term → created + announced, no question;
  proactive batch → proposed. New `glossary` frontmatter key
  (`"non"` = scan declined, absent = not checked, unset once the file
  exists). `ARCHITECTURE.md` keeps its bootstrap question.
- Touched `SKILL.md` (detection bullet, bootstrap step 7, frontmatter,
  Continuous updates), `writing-tracking-files.md`, `references/i18n/{en,fr}.md`
  (glossary.title/intro), `README.md`. `DECISIONS.md` entry added.
- 89 portfolio + 8 manifest + hook suites green; installer regenerated.

## 2026-08-30 — v0.6.0: fresh-eyes readability pass

- After a substantial write/rewrite of an onboarding file (README /
  CLAUDE.md / ARCHITECTURE.md / GLOSSARY.md), Claude runs a readability
  pass: a subagent (inline fallback) checks it against the file's reader
  definition — clear hook, reachable quick start, jargon-before-intro,
  drift from purpose, concreteness, over-long sections. Advisory, never a
  gate. Runs at bootstrap and on later rewrites; STATUS.md is excluded.
- New `## The fresh-eyes readability pass` section in
  `writing-tracking-files.md`; `SKILL.md` points to it from the bootstrap
  flow and `## Continuous updates`. `DECISIONS.md` records the
  subagent-not-inline / advisory-not-gate choices.
- 89 portfolio + 8 manifest + hook suites green; installer regenerated.
- Backlog reservoir is now down to one Low item (trackignore un-exclude).

## 2026-08-30 — v0.7.0: un-exclude on request

- The **Excluded** state now acts when the user asks to track the folder:
  if its own path is the `trackignore.txt` line, Claude offers to remove it
  and bootstrap (symmetric with bootstrap step 1); if an ancestor is the
  ignored line, Claude explains that un-ignoring the whole subtree is the
  only option and asks. Bringing the folder up for anything else is
  unchanged. `SKILL.md` only; no test, no i18n.
- **Backlog reservoir is now empty** — every item planned this session
  (v0.4.0 output language, v0.4.1 cleanup, v0.5.0 lazy glossary, v0.6.0
  fresh-eyes pass, v0.7.0 un-exclude) has shipped. Next themes will come
  from real use.

## 2026-08-30 — Full repo audit (clean-up pass)

- Personal-info sweep: one absolute home path in `JOURNAL.md`'s first entry,
  genericised. Nothing else — no emails, no other-project names, no session
  URLs, no secrets in tracked files (installer base64 blobs decoded and
  checked too).
- `ROADMAP.md` was four releases stale — full rewrite (v0.1–v0.3 grouped,
  v0.4.0–v0.7.0 listed, current focus = empty backlog).
- `CLAUDE.md`: reference-file list completed (`writing-tracking-files.md`,
  `i18n/`), `test_generate_portfolio` command fixed, release routine now
  names the STATUS/JOURNAL/BACKLOG/DECISIONS updates.
- `README.md`: install commands were printed twice → deduped; frontmatter
  example completed (all 12 keys); fresh-eyes + un-exclude behaviours added;
  ROADMAP row reworded. Ran the fresh-eyes pass inline — otherwise clean.
- Version consistency verified: `plugin.json` == `marketplace.json` == tag
  `v0.7.0` == `CHANGELOG` top == `STATUS`. Installer regeneration produces no
  diff. All suites green (8 + 89 + 3 hooks).

## 2026-08-31 — v0.7.1 released

- The repo-audit fixes from `[Unreleased]` shipped as a patch: `JOURNAL.md`
  home-path genericised, `ROADMAP.md` / `CLAUDE.md` unstaled, `README.md`
  tidied. No behaviour change. `v0.7.1` tagged and pushed.

## 2026-08-31 — v0.8.0: proactive tracking prompt

- First real dogfood attempt on another project surfaced this: on an
  untracked folder the `SessionStart` hook only injected a passive "not
  tracked" note — Claude didn't open with the question, and asked in prose
  when it did.
- Fix: the hook's new-project message is now an explicit opening-move
  instruction — invoke the skill and ask, before anything else, via
  `AskUserQuestion`: **Yes, set it up** / **No, don't ask again**
  (→ `trackignore.txt`) / **Not now** (→ nothing, re-asked next session).
  `SKILL.md § Bootstrapping` step 1 and `test_session_start.sh` updated;
  `README.md` Quick start reworded. `DECISIONS.md` records the choice.
- Plugin updated to v0.7.1 on this machine before the test; v0.8.0 tagged.
- 8 manifest + 89 portfolio + 3 hook suites green; installer regenerated.

## 2026-08-31 — v0.9.0: skill renamed to `track`

- Prompted by the ugly `project-tracker:project-tracker` invocation. The
  single skill is now `track` → `project-tracker:track`.
  `skills/project-tracker/` → `skills/track/` (git mv), `SKILL.md`
  `name: track`, `hooks.json` / `build_installer.sh` / `test_plugin_manifest.py`
  / `CLAUDE.md` / `README.md` / `commands/config.md` path refs updated, hook
  messages name `project-tracker:track` precisely.
- Considered and rejected splitting the plugin into multiple skills — it is
  one coherent workflow (see `DECISIONS.md`).
- Unchanged: plugin name, `/project-tracker:config`, `~/.claude/project-tracker/`
  config dir, `docs/project-tracker/` output namespace. Historical
  `DECISIONS.md` entries keep the old `skills/project-tracker/` path.
- 8 manifest + 89 portfolio + 3 hook suites green; installer regenerated.

## 2026-09-01 — v0.10.0: console-view preference

- The transcript diff-noise from the skill's per-session file writes: it now
  asks once per machine to fold Claude Code's view to "chat" —
  Everywhere / Only in tracked projects / No — recorded in `prefs.txt`
  (`console_view:`). New `## Console view preference` section in `SKILL.md`;
  bootstrap + detection wired; `/project-tracker:config` gains the action;
  `DECISIONS.md` records the settings-file-writing choice.
- Also updated the "don't over-edit tracking files" habit (memory) — this
  release batched the doc updates into one pass.
- 8 manifest + 89 portfolio + 3 hook suites green; installer regenerated.

## 2026-09-01 — v0.11.0: plain-language questions

- `SKILL.md` gains `## Asking questions` (assume the answerer isn't a power
  user: plain wording, one line per option on what it changes, a
  context-based **(recommended)** hint). Every question reworded to match:
  bootstrap git/Reminders/category/ARCHITECTURE, first-run portfolio/language/
  console-view, the phase + superpowers + backlog-model prompts (in
  `backlog-phases.md`), retranslation (`writing-tracking-files.md`), the
  un-exclude prompt.
- 8 manifest + 89 portfolio + 3 hook suites green; installer regenerated.

## 2026-09-01 — First external dogfood run: nested-tracking gap

First real dogfood of the v0.11.0 plugin, on an external project.

- Bootstrap ran on a **parent** folder (user's deliberate choice), French, a
  category, a linked Reminders list, `uses_git: false`. Nine standard files
  created.
- The proactive prompts (tracking, console-view, language) fired as designed;
  no friction reported on the bootstrap flow itself.
- **Gap surfaced:** the parent is *one* project, but the shipped code lives in
  a git sub-repo that is what gets pushed to GitHub. The skill has no model
  for micro-tracking such a sub-repo (repo-facing `README`, optional
  `ARCHITECTURE.md`, `CHANGELOG.md`) while the parent chaperones it and
  reports its progress. The git hooks only ever look at the tracked root, so
  with the parent at `uses_git: false` the collision diff / commit offer /
  staleness checks don't reach the sub-repo. Captured in `BACKLOG.md` (Open),
  to be brainstormed before building.

## 2026-09-01 — Planning: two more backlog items

Discussion off that run. Added to `BACKLOG.md` (Open):
- **Portfolio detail sub-page per project** — click through from
  `PORTFOLIO.html` to a per-project page (STATUS + current ROADMAP phase +
  recent JOURNAL + latest CHANGELOG + a GitHub link with the mark), instead
  of jumping to GitHub.
- Note on the nested-tracking item: a second project is an intended user of
  that model; the migration/re-prompt path for already-tracked projects is
  part of the item's scope.

Decision: hold the next release until 3–4 solid items have accumulated, then
ship one larger update with a single migration pass for tracked projects.
