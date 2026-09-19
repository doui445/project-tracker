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

## 2026-09-01 — Repo privacy: names sweep + history scrub

- New `CLAUDE.md` convention: **no real project names or personal data
  anywhere in the repo**, self-tracking files included — generic placeholders
  only (`doui445` in the manifests is the sole exception). Run this "names
  sweep" by eye alongside the French sweep before every commit.
- One pre-existing leak (a project folder name in `STATUS.md`, present across
  the v0.8.0–v0.11.0 line) scrubbed from **all git history** with
  `git-filter-repo`, then force-pushed. `main` + tags v0.8.0/v0.9.0/v0.10.0/
  v0.11.0 were rewritten. A pre-rewrite backup bundle was kept.

## 2026-09-02 — Discussion: a public website for the plugin

Brainstorm only — nothing built, no design validated. Outcome captured as two
linked `BACKLOG.md` items (Open): **Brand / visual identity ("DA")** and
**Public website**, the DA to be spec'd first.

- Agreed shape: an Astro site with bespoke design in a `site/` sub-folder of
  this repo (own `package.json`; the plugin root stays dependency-free — the
  "no deps" rule scopes to the shipped plugin, to be recorded in
  `DECISIONS.md` when built). Host: Cloudflare Pages, free,
  `project-tracker.pages.dev` to start. Goal: marketing + docs.
- User's firm constraints: visually striking (at least as clean as
  `impeccable.style`) and 100% free for now. Nothing else fixed.
- Visual direction left open (leaning technical/terminal and/or
  marketing/lively), to settle during the DA spec. i18n via a languages
  dropdown (en + fr, extensible). Analytics: Cloudflare Web Analytics
  (free, cookieless) or none — decide in the spec.
- Two process notes from the user, to fold into the skill's behaviour:
  every discussion should be logged even when the idea is later dropped
  (a backlog item to make that explicit in `SKILL.md`); and this session
  made a second avoidable edit to `BACKLOG.md` — batch tracking-file writes.

## 2026-09-02 — Discussion: design as a tracked dimension

Brainstorm only — nothing built. A third spec-worthy item alongside the two
website ones. Full detail in `BACKLOG.md` (**Design as a tracked dimension**).

- **Two tiers.** N1: one light always-on `IDENTITY.md` (name, one-liner,
  audience, tone, active tier, pointers), filled passively during normal
  sessions, owned by `track`. N2: a **new skill `project-tracker:design`**
  under `docs/project-tracker/design/` (`PRODUCT.md` + `DESIGN.md`,
  `VOICE.md` at brand tier, `logo.md` / `applications.md` for the brand
  layer). Triggered by explicit request, a UI being built (the portfolio
  counts), or "this is a brand" declared at bootstrap.
- Brand layer = **superset** of the product DA, progressive ladder.
- `track` keeps N1 + detection + hand-off. New `DECISIONS.md` entry —
  revisits the 2026-08-31 "one coherent workflow": one workflow to track,
  a new entry point to create.
- **Tool integration** (delegate creative work to installed design skills,
  like phase plans go to `superpowers`): per-category prefs
  (`design_skills_<category>:`, 2 max), asked lazily per category, curated
  suggestion catalogue, install-on-yes. A/B = both on the first task →
  favourite → alternative on request; favourite is per project.
- **Assets**: binaries in `brand/` at the repo root; light inventory in
  `design/assets.md`; version SVG/favicon/OG, fonts only if the licence
  allows, no heavy sources.
- **Parked**: exact per-file content inventory (user is researching first).
  **Open**: whether the standard files move under
  `docs/project-tracker/track/` (recommendation: no); i18n; migration of
  tracked projects; portfolio surfacing a project's DA.
- Also raised, its own small task: move `_dev-history/` to a gitignored
  `docs/superpowers/` (the `superpowers` default path). Backlog item added.

## 2026-09-02 — Design/branding research pass (23 videos)

Research only — nothing built. The user fed 23 YouTube videos on brand strategy,
logo design, visual identity, personal branding, marketing, product psychology,
design thinking, layout, and presentation. Broken down one by one into
`_dev-history/research/2026-09-02-design-branding-videos.md` (gitignored, FR,
detail + source per video), then distilled into
`_dev-history/research/2026-09-02-design-branding-SYNTHESE.md` (context-free
rules, multi-validated points ranked by convergence, contradictions with
resolutions, and concrete implications for the three specs).

- Feeds the **Brand / visual identity (DA)** and **Design as a tracked
  dimension** backlog items (and the website spec).
- Cardinal finding: the whole corpus independently converges on
  project-tracker's own thesis — *a strategy/identity that isn't written down
  doesn't exist*. Strongest single takeaway: **differentiation / anti-conformity
  is the core** (~11 videos).
- The "logo shouldn't please you" vs the planned A/B mechanic **tension is
  resolved**: options are framed by the strategy and evaluated against an
  adjective rubric signed *before* seeing the work, plus targeted questions —
  never "which do you prefer?".
- Design-skill N2 workflow and the website "Why" page structure are sketched
  in the synthèse; to formalise when the DA spec starts.
- Follow-up same day: the **N2 file model is now frozen** — `FOUNDATIONS.md`
  (durable character sheet) + `STRATEGY.md` (revisable map) split out along
  the strategy-vs-branding line, `DESIGN.md`, a **separate**
  `design/DECISIONS.md`, and `VOICE.md` / `logo.md` / `applications.md` /
  `assets.md` at brand tier. Detail in SYNTHÈSE § 5; BACKLOG item updated.

## 2026-09-03 — Decisions round: the open items closed

Nothing built. A Q&A pass closed the items parked over the last two days.

- **`_dev-history/` → gitignored `docs/superpowers/`** — done (`git mv`,
  `.gitignore` comment, `CLAUDE.md` § Phases, `DECISIONS.md`). The research
  notes + synthèse now live at `docs/superpowers/research/`.
- **DA decisions** (for project-tracker's own identity): keep the name
  **`project-tracker`**; the **"reduce" visual pole** (Muji / Apple); a
  **tool brand with a light personal touch**; **re-skin `PORTFOLIO.html`** as
  part of the DA work; portfolio surfacing a project's DA is **v2**.
- **Design capability**: `kind: tool | app | library | brand`; the core
  tracking files **stay at the `docs/project-tracker/` root** (no `track/`
  subfolder); new design files get the **same headings-only i18n** as the
  standard ones; N2 workflow still to spec.
- **Release plan**: not one big batch, not `1.0`. **v0.12.0** = nested
  tracking + reusable re-prompt infra + portfolio sub-pages + the small
  "log every discussion" rider; **v0.13.0** = the `design` skill, reusing
  that infra; **v1.0.0** later, deliberate. DA + website run in parallel,
  no plugin bump. Recorded in `DECISIONS.md`.
- **Site analytics**: Cloudflare Web Analytics.
- `STATUS.md` next-actions, `ROADMAP.md` (v0.8–v0.11 backfilled + current
  focus) updated. Two new Reminders created for the release-scope decision
  (now settled) and the DA spec.

## 2026-09-14 — Discussion: Obsidian integration

Brainstorm only — nothing built, no decision. The user asked what Obsidian
is/does/a vault means, and whether it could fit project-tracker.

- Obsidian = local-first Markdown note app; a **vault** is just a plain
  folder of `.md` files it manages (plus a `.obsidian/` config subfolder).
  No proprietary format, no cloud lock-in — the standard tracking files are
  already vault-compatible as-is, zero changes needed. Confirmed
  `https://obsidian.md` is the real site.
- Assessed as a complement, not a replacement: project-tracker automates
  generation/upkeep of the tracking files plus the GitHub/portfolio side,
  none of which Obsidian does. Obsidian would only add an optional
  reading/linking/graph layer on top.
- Integration angles raised, none decided: (a) zero-effort — just document
  the vault-compatibility; (b) ship an optional, gitignored `.obsidian/`
  config template so a scope root opens cleanly as a vault (opt-in, never a
  dependency); (c) cross-link tracking files with `[[wikilinks]]` for the
  graph/backlinks — flagged as in tension with the plain-Markdown/
  no-lock-in ethos, since wikilinks aren't standard Markdown and don't
  render as links on GitHub. Leaning against (c) unless a strong case
  emerges. Captured in `BACKLOG.md` (Open) for a future real brainstorm.
- Process note: from this session on, discussion logging to JOURNAL/BACKLOG
  is automatic (no permission asked), batched to one entry per concluded
  topic rather than per exchange — recorded in memory.

## 2026-09-15 — Skill stays quiet when there's nothing to report

The user noticed a chatter pattern: at session start Claude was announcing
"tracking files are up to date" every time, even when there was nothing to
act on. Broader ask: the skill's own bookkeeping should run as
transparently as possible, so the conversation stays focused on the user's
real topic — file edits can't be hidden, but spoken narration around
nothing-to-report checks can.

- Agreed and implemented directly (small, low-risk doc change, no need for a
  separate spec/plan). New `## Staying in the background` section in
  `SKILL.md`: the session-opening staleness check is silent when files are
  current; the skill speaks up only for an actual proposal, question, or
  something the user needs to see or decide — everything already spec'd
  elsewhere (proposed updates, bootstrap/detection questions, commit offers,
  collisions, glossary additions) is unaffected.
- `CHANGELOG.md` `[Unreleased]` entry added (this is a behaviour change, so
  it rides the next minor release — no version bump today).

## 2026-09-16 — Nested tracking shipped

Built per the spec/plan at
`docs/superpowers/{specs,plans}/2026-09-16-nested-tracking*.md`, across seven
tasks, all committed and reviewed clean:

- `subprojects:` / `nested_model:` frontmatter keys, plus a general
  `## Retroactive frontmatter questions` principle covering every frontmatter
  key that follows this absent → signal-detected → resolved-once shape
  (`backlog_model`, `phase_model`, `category`, `glossary`, and now
  `nested_model`).
- The new `## Sub-projects` section: what a sub-project is, its two states
  (`tracked: false` / `tracked: true`), the fixed flat file set for a tracked
  one (`README.md`, `CHANGELOG.md`, `DECISIONS.md`, `ERRORS.md` always, plus
  optional `ARCHITECTURE.md`), and the new `SUBPROJECTS.md` as a third
  optional file, created on first need.
- Detection/attachment reusing the existing 3-way bootstrap choice, plus the
  one-time `nested_model` migration check for projects tracked before this
  feature existed.
- Dual-context loading for a session opened inside a tracked sub-project, a
  git/freshness check matrix per active sub-project (with and without its
  own git), and an anti-duplication principle keeping the parent's
  `STATUS.md`/`JOURNAL.md`/`ROADMAP.md` global once sub-projects exist.
- `references/writing-tracking-files.md` guidance for `SUBPROJECTS.md` and
  sub-project-scoped files.
- Along the way, a real bug surfaced and got fixed in
  `generate_portfolio.py`'s `parse_frontmatter`: it read the new nested
  `subprojects:` YAML list line-by-line as if it were flat top-level
  frontmatter, so an indented `status: archived` inside a sub-project entry
  could silently override the project's own top-level `status:`. Fixed
  (skip indented lines) with two regression tests; full suite now 91/91.
- Full verification sweep (all five test suites, names/French sweep) green;
  installer regenerated and committed. This entry plus the matching
  `CHANGELOG.md`/`BACKLOG.md`/`STATUS.md` updates close out the feature.
  Not yet released — bundled into v0.12.0 alongside the still-open portfolio
  sub-page item and the "log every discussion" rider.

## 2026-09-17 — Self-audit of `SKILL.md`

Prompted by an external video on skill engineering (framework: name/trigger,
outputs, tools, step-by-step process, accumulated rules, continuous
correction). Cross-checked that framework, plus the `superpowers:writing-skills`
size/SDO guidance, against the actual `SKILL.md` (not just the video's
generic claims). Findings, all verified rather than assumed:

- The "log every discussion" behaviour (open backlog item since 2026-09-02)
  is confirmed still absent from `SKILL.md` — grepped, no trace.
- `SKILL.md` is 382 lines / ~45k chars, all loaded on every trigger; `##
  Sub-projects` (~57 lines) is the largest still-inline subsystem, a natural
  extraction candidate (same pattern as `backlog-phases.md`).
- No dangling references — every `references/*.md` cited in `SKILL.md`
  exists, i18n included.
- No centralized "lessons learned" section — corrections are woven into the
  relevant section instead of collected in one place; open question, not a
  clear defect.
- Frontmatter description reads as a workflow summary (lists all nine file
  names) rather than a pure trigger — the documented SDO anti-pattern.
- No behavioural test coverage: hooks/portfolio/manifest are tested, but the
  skill's own prose rules (never guess, stay quiet, ask once) have never
  been pressure-tested with subagents per the writing-skills RED/GREEN method.

Four items added to `BACKLOG.md` (Open) for later: extract `##
Sub-projects`, lighten the frontmatter description, consider a lessons-
learned section, pressure-test the behavioural rules. None actioned yet.

## 2026-09-17 — "Log every discussion" rider shipped

Implemented the backlog item surfaced 2026-09-02: new bold paragraph in
`SKILL.md`'s `## Continuous updates`, right after the "significant change"
trigger clarification. A substantive design/scoping discussion is now
logged independently of that trigger — one `JOURNAL.md` entry per
*concluded* topic (never mid-discussion), plus a `BACKLOG.md` item for
anything actionable, written automatically with no permission asked first.
`BACKLOG.md` item moved to Completed; `CHANGELOG.md` `[Unreleased]` entry
added. Rides v0.12.0 alongside nested tracking and the still-open portfolio
sub-page item.

## 2026-09-17 — Portfolio detail sub-pages shipped

Implemented the last open v0.12.0 item across an 11-task plan (spec/plan
under `docs/superpowers/{specs,plans}/2026-09-17-portfolio-detail-subpages*.md`).
`generate_portfolio.py` gained a dependency-free Markdown→HTML fragment
renderer and `build_subpage()`, writing each tracked project's own
`portfolio/<project>.html` (state, next actions, current roadmap phase,
recent journal entries, latest changelog version, a direct GitHub link)
linked from its card in `PORTFOLIO.html`; a new `--changed <project_root>`
flag lets a targeted run regenerate only one project's sub-page, with
orphan sub-pages cleaned up on every run. `portfolio_regen.sh` now passes
`--changed "$PROJECT_ROOT"` so an ordinary `STATUS.md` edit regenerates
only that project's sub-page; a manual/config-triggered run still
regenerates all of them. `SKILL.md` `## Portfolio` documents the new
behaviour. Full verification sweep (all five test suites, names/French
sweep) green. `STATUS.md`/`CHANGELOG.md`/`BACKLOG.md` updated; all three
v0.12.0 code items are now done — only the release routine remains.

## 2026-09-19 — v0.12.0 released

Closed out the portfolio sub-pages work and cut the release:

- Final whole-branch review (opus) on the sub-pages branch found and fixed
  4 more Important issues beyond the per-task reviews: a back-link
  hardcoded to `PORTFOLIO.html` (broke custom `portfolio.txt` filenames),
  a `SKILL.md` paragraph left stale by the sub-projects work, unsafe
  orphan cleanup (now marker-based — never deletes a file it didn't
  generate), and intraword `_` mangling `snake_case` prose. Merged to
  `main` (142/142 + 8 + 3 hook suites green on the merged result).
- Went through the final review's 7 deferred Minor findings one by one
  with the user rather than batch-deciding: fixed all 7 — a vacuous test
  assertion, a missing defensive fallback, a missing `aria-label`, a
  `.strip()` inconsistency, equal card height in a grid row, sub-page
  filename sanitisation (path-traversal-safe, `render_card` now reuses
  the same sanitiser so a card's link can never diverge from the file
  written), and 6 new tests for edge cases already traced as safe but
  left uncovered. 151/151 scripts tests green.
- **Released v0.12.0**: `plugin.json`/`marketplace.json` bumped, installer
  regenerated, `CHANGELOG.md` `[Unreleased]` rolled into a dated entry.

## 2026-09-19 — Session-start check was being deferred

- A dogfood session opened on an unrelated request ("run the app"); Claude
  finished that task, then only *mentioned* the hook's staleness check and
  asked whether to run it. Cause: the hook wording ("propose an update if
  needed") read as optional, and nothing said to do it alongside the
  user's request.
- Fixed the hook message and added an explicit "instruction, not a
  suggestion" paragraph in `SKILL.md` (`## Detecting a project's root`).
  Unreleased; no version bump yet.
- **Released v0.12.1**: manifests bumped, installer regenerated,
  `CHANGELOG.md` `[Unreleased]` rolled into a dated entry.

## 2026-09-19 — Self-audit cleanups on SKILL.md

- Extracted `## Sub-projects` into `references/subprojects.md` and trimmed
  the frontmatter `description` to trigger conditions (the two small
  self-audit items). `SKILL.md` keeps a stub with the in-session attach
  trigger so the behaviour still fires without loading the reference.
  Cross-references inside the moved text now say "in `SKILL.md`". The
  installer globs `references/*.md`, so it picked the new file up
  automatically. Unreleased (patch-level, no behaviour change).
- **Released v0.12.2**: manifests bumped, installer regenerated,
  `CHANGELOG.md` `[Unreleased]` rolled into a dated entry.

## 2026-09-19 — Open backlog items discussed while the DA waits

- Went through the open items not blocked on the DA, one at a time.
  Nothing built.
- **Centralized "lessons learned" section**: abandoned. A rule sits best
  in the section where it applies; a central list would duplicate them, and
  the history of corrections is already in `DECISIONS.md` / `ERRORS.md`.
- **Pressure-testing the prose rules with subagents**: kept but scoped
  down to 3 rules (session-start check not deferred, silence when up to
  date, retroactive question asked once); on demand, no CI, no date.
- **Obsidian integration**: abandoned entirely (never used; already works
  as a vault; wikilinks break GitHub rendering).
- New idea captured: a graph / overview views in the portfolio, to be
  discussed during the DA work — needs a decision on which relationship it
  would show. Still open: the DA spec and the `project-tracker:design` skill.
