# BACKLOG — project-tracker

Raw reservoir of every idea/feature envisaged. Never purged — enriched and
archived. Statuses: `[ ]` to do · `[~]` in progress · `[x]` done · `[-]`
abandoned. Effort S/M/L, value ⭐–⭐⭐⭐.

## Open

- [ ] **Skill: log every discussion, even ideas later abandoned** (S, ⭐⭐) —
  surfaced 2026-09-02. The user wants the skill to always record a design /
  scoping discussion in the tracking files (`JOURNAL.md`, and `BACKLOG.md`
  for anything actionable) *at the time it happens* — even when no decision
  is made and even if the idea is dropped later. Nothing said in a session
  should be lost because it wasn't validated. Make this explicit in
  `SKILL.md` (`## Continuous updates` / the journaling guidance): a
  substantive discussion is itself a trackable project event. Small edit,
  no i18n impact beyond wording.

- [ ] **Design as a tracked dimension (new `project-tracker:design` skill)**
  (L, ⭐⭐⭐) — surfaced 2026-09-02. Give the plugin the ability to own a
  project's design / brand direction, the way it owns state and progress.
  Two tiers:
  - **N1 — always-on, in `track`.** One light file
    `docs/project-tracker/IDENTITY.md` (name + working name, one-liner,
    audience, 3–5 tone adjectives + a "not this" list, which tier is
    active, pointers to N2 files). Filled **passively during normal
    sessions** — same discipline as glossary enrichment, needs a clear
    trigger. Synergy with the "log every discussion" item above.
  - **N2 — a new skill `project-tracker:design`.** Full direction under
    `docs/project-tracker/design/`. **File model FROZEN 2026-09-02** (from
    the 23-video research pass — full detail in
    `docs/superpowers/research/2026-09-02-design-branding-SYNTHESE.md` § 5):
    - `FOUNDATIONS.md` — *durable* character sheet: the brand's purpose
      (why→how→what), personality/values/vision + archetype, core emotion,
      brand story (StoryBrand: customer = hero, brand = guide, an enemy),
      tone essence.
    - `STRATEGY.md` — *revised, like STATUS.md*: objectives, personas (demo +
      psychographic + emotional starting state, revisited periodically),
      competitive landscape + mapping + the gap, differentiators, positioning
      statement, the "mechanism", non-goals.
    - `DESIGN.md` — visual system (universe/concept + rationale, adjective
      sliders, colour = 5 layers + jobs + OKLCH + saturation/contrast
      register + rationale, type, grid/layout + temporal-flow notes, motion,
      iconography, component conventions, signature treatments, stylistic
      latitude, do/don't). Splits by section when it grows.
    - `DECISIONS.md` — **separate** from the project's main `DECISIONS.md`;
      3P structure (tried → why rejected → chosen); heritage notes for rebrands.
    - Brand-tier: `VOICE.md` (detaches from `FOUNDATIONS.md`), `logo.md`,
      `applications.md`, `assets.md`, plus `brand/` (binaries at repo root).
    Triggered by: explicit request, a UI being built (the portfolio counts),
    or "this is a brand" declared at bootstrap (a `kind:` frontmatter key).
  - **Brand layer = superset** (progressive ladder: N1 `IDENTITY` →
    N2 product `FOUNDATIONS` + `STRATEGY` + `DESIGN` + `DECISIONS` →
    N2 brand + `VOICE` + `logo.md` + `applications.md` + `assets.md` +
    `brand/`), not a separate track.
  - `track` keeps the always-on N1, the detection, and the hand-off to
    `design`. New `DECISIONS.md` entry — revisits the 2026-08-31 "one
    coherent workflow / no skill split": one workflow to *track*, a new
    entry point to *create*.
  - **Anti-duplication rule** (cousin of "never guess"): a fact lives in
    exactly one file. `FOUNDATIONS` = the why + who we are; `STRATEGY` =
    where we play + against whom; `DESIGN` = visual only; `VOICE` = verbal;
    `IDENTITY` = the seed (keeps only name + tagline + one-liner + tier +
    pointers once `design/` exists). Colour/type: `DESIGN.md` only.
  - Still to define when the spec starts: the N2 workflow itself (research →
    strategy → 2 named art directions → logo → … → presentation with an
    adjective rubric + targeted questions), sketched in SYNTHÈSE § 5.

  **Tool integration.** The creative work is delegated to installed design
  skills (`impeccable`, `ui-ux-pro-max`, `dataviz`, `apple-design`,
  `emil-design-eng`, the animation family), the way phase plans are
  delegated to `superpowers`. Never a hard-coded priority list.
  - Per-category prefs in `~/.claude/project-tracker/prefs.txt`, flat keys
    `design_skills_<category>:` (categories: identity, screens, charts,
    animation), up to **2 skills each**.
  - Asked **lazily, per category**, the first time that category's work
    comes up — one `AskUserQuestion`: installed matching skills, then the
    curated suggestion ("install & use …") if absent, then "none / handle
    inline" at the bottom; pick 2 max; a one-line explanation of the
    category. Curated catalogue in `skills/design/references/design-skills.md`
    (i18n'd, deliberately tiny, advisory, dismissible, flags "you already
    have X which does similar").
  - The plugin **can** run the install command on an explicit yes; Claude
    Code built-ins (`dataviz`) need no install.
  - Routing: identity → `impeccable` (brand mode); screens → `ui-ux-pro-max`;
    charts → `dataviz`; nothing installed → inline.
  - **A/B**: both skills on the first significant task of a category → user
    picks a favourite → then only the favourite, the other on "show me an
    alternative". Favourite is **per project** (global `design_skills_*`
    order = default, per-project frontmatter override, changeable on
    request), same cascade as `language`. Only meaningful when 2 are set.

  **Assets.** Binaries (`logo.svg`, `favicon`, `og.png`, fonts) in
  `brand/` at the **repo root**, not under `docs/`. `design` frames the
  specs first (`logo.md`); can propose the design tool for actual logo
  work, user chooses. Version in a public repo: SVG logos / favicon / OG
  image — yes; fonts only if the licence permits redistribution (skill
  **warns**, prefers CDN/package); no heavy rasters or design-source files
  (`.fig` / `.ai` / `.sketch` / `.psd`). Track them with a **light
  inventory** (`design/assets.md`: file → purpose, spec, status), which
  `design` reconciles whenever it touches `brand/`.

  **Open / spec-level:** whether the 7 standard files + `IDENTITY.md` move
  to `docs/project-tracker/track/` for symmetry with `design/`
  (recommendation: **no** — the detection path is deeply wired into hooks /
  retrofit / every tracked project; keep the core at the namespace root,
  only `design/` is a subfolder); i18n of the new files (headings only,
  like the others); migration / re-prompt for already-tracked projects
  (reuse the retro-question infra, cf. the nested-tracking item); whether
  `PORTFOLIO.html` surfaces a project's DA (a card in its own palette, a
  design status) — resist scope creep, likely v2. **Decompose the spec**:
  N1 + tool-integration mechanism first (small, immediately useful), N2 in
  its own spec.

- [ ] **Brand / visual identity (the project's "DA")** (M, ⭐⭐) — surfaced by
  the website discussion (2026-09-02). Prerequisite for the public website:
  the user wants that site "at least as clean as impeccable.style" and holds
  that a tool site's polish reflects on the skill's author. Today the
  project's identity is implicit and scattered across `SKILL.md` /
  `CLAUDE.md`. This item produces a durable identity the website, the
  generated `PORTFOLIO.html`, the `README`, and screenshots all share:
  likely a `PRODUCT.md` (who it's for, the problem, what it explicitly is
  *not* — not a task manager, not a Jira, the calm/terse voice, positioning)
  and a `DESIGN.md` (name / wordmark / logo, OKLCH palette, type scale,
  fonts, spacing, motion principles). Gets its **own spec → plan →
  implementation cycle, done before the website spec.** Open design
  questions for that brainstorm: do `PRODUCT.md` / `DESIGN.md` live at repo
  root or under `docs/`; does the public name stay `project-tracker` or
  gain a product name; visual direction leans **B** (technical / dense /
  terminal / dark, e.g. `bun.sh`, `ghostty`) and/or **C** (marketing /
  lively, before/after, animation, like impeccable) — not yet decided;
  whether to re-skin `PORTFOLIO.html` to match (touches
  `generate_portfolio.py` + its `STRINGS` table); use the `impeccable` skill
  as the execution tool. Prerequisite for the **Public website** item below.
  A 23-video research pass (2026-09-02) is distilled in
  `docs/superpowers/research/2026-09-02-design-branding-SYNTHESE.md` — § 5 sketches
  this spec's shape (constraint→identity, the "reduce" visual pole, the enemy
  for the "Why" page, and `design/{FOUNDATIONS,STRATEGY}.md` content).

- [ ] **Public website** (L, ⭐⭐) — surfaced 2026-09-02, **depends on the
  brand / visual identity item above.** A marketing + docs site for the
  plugin. Firm constraints from the user: visually striking, at least as
  clean as `impeccable.style`; **100% free** for now (nothing else is
  fixed). Established in the discussion:
  - **Astro**, bespoke design (same stack impeccable uses: static, hand-written
    CSS). Lives in a `site/` sub-folder of **this repo** with its own
    `package.json`, so the plugin at the root stays dependency-free — needs a
    `DECISIONS.md` entry recording that the "no deps" rule scopes to the
    *shipped plugin*, not the site. Keep `site/` out of the generated
    installer (`build_installer.sh`) and the plugin manifests.
  - **Host: Cloudflare Pages** — free, `project-tracker.pages.dev` subdomain
    to start (clean subdomain, unlike a `github.io/project-tracker` subpath);
    a paid custom domain can be added later with no migration. GitHub Pages
    was the fallback; Vercel rejected (third-party account, free tier is
    non-commercial-only, features unneeded for a static site).
  - **Pages (not fixed):** landing (pitch; before/after — nine hand-kept files
    → one generated `PORTFOLIO.html`; screenshot or GIF; install one-liner);
    "how it works" (the flow, and the questions the skill asks); a detailed
    install guide; docs (the nine standard files explained, hooks,
    `/project-tracker:config`, phase model, backlog model); changelog
    generated from `CHANGELOG.md`; an optional "Philosophy / Why" page (flat
    Markdown over an app, "never guess" — gives the site character); repo link
    visible everywhere.
  - **Docs generated from the canonical Markdown** via Astro content
    collections — single source of truth, one PR changes behaviour + docs
    together.
  - **i18n:** a languages **dropdown button** (options unfold below), not a
    binary en/fr toggle — so more languages stay cheap to add later. Ships
    with en + fr. Tension to resolve in the spec: the repo convention is
    "shipped strings are English" — site copy is probably authored EN + FR,
    generated docs may lag behind in fr.
  - **Analytics:** optional. Cloudflare Web Analytics (free, cookieless, no
    consent banner) or none at all — decide in the spec.
  - Use the `impeccable` skill for the visual execution.

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

- [x] **Move `_dev-history/` to a gitignored `docs/superpowers/`** (2026-09-03)
  — `git mv` to the `superpowers` skill's default path, kept gitignored
  (French, working notes); research notes alongside in
  `docs/superpowers/research/`. `.gitignore` comment + `CLAUDE.md` § Phases
  simplified + `DECISIONS.md` entry (revises the 2026-08-30 custom-path
  choice).

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
  plan in `docs/superpowers/{specs,plans}/2026-08-30-output-language*`.
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
