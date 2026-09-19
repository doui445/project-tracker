# BACKLOG — project-tracker

Raw reservoir of every idea/feature envisaged. Never purged — enriched and
archived. Statuses: `[ ]` to do · `[~]` in progress · `[x]` done · `[-]`
abandoned. Effort S/M/L, value ⭐–⭐⭐⭐.

## Open

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
    or "this is a brand" declared at bootstrap via the **`kind:` frontmatter
    key** — decided: `kind: tool | app | library | brand` (one key, four
    values; drives the logo strategy and the DA tier proposed; `brand`
    triggers the full brand layer).
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

  **Decided 2026-09-03:**
  - **No `docs/project-tracker/track/` subfolder** — the core files stay
    flat at the namespace root, only `design/` nests (see `DECISIONS.md`).
  - **i18n**: same as the standard files — section headings in
    `references/i18n/{en,fr}.md`, content in the project's language.
  - **`PORTFOLIO.html` surfacing a project's DA**: **v2**, after the
    portfolio detail sub-pages item — not part of this spec.
  - **Migration / re-prompt** for already-tracked projects: reuse the
    re-prompt infra built with nested tracking (v0.12.0). N1 `IDENTITY.md`
    fills passively (no re-prompt); the N2 opt-in can be lazy.
  - **Ships as v0.13.0**, reusing that infra. Its own spec → plan cycle.

  **Still to define in the spec**: the N2 workflow itself (research →
  strategy → 2 named art directions → logo → … → presentation with an
  adjective rubric + targeted questions — sketched in
  `docs/superpowers/research/2026-09-02-design-branding-SYNTHESE.md` § 5);
  the exact category list + question wording for tool integration; the
  curated `design-skills.md` catalogue contents.

- [ ] **Brand / visual identity (the project's "DA")** (M, ⭐⭐) — surfaced by
  the website discussion (2026-09-02). Prerequisite for the public website:
  the user wants that site "at least as clean as impeccable.style" and holds
  that a tool site's polish reflects on the skill's author. Today the
  project's identity is implicit and scattered across `SKILL.md` /
  `CLAUDE.md`. This item produces a durable identity the website, the
  generated `PORTFOLIO.html`, the `README`, and screenshots all share:
  applying the frozen file model to project-tracker itself:
  `docs/project-tracker/design/{FOUNDATIONS,STRATEGY,DESIGN}.md` (+ a
  `design/DECISIONS.md`). Gets its **own spec → plan → implementation
  cycle, before the website spec** but **in parallel with the plugin
  releases** — no plugin version bump (docs + a `PORTFOLIO.html` re-skin).

  **Decided 2026-09-03:**
  - **Name**: keep **`project-tracker`** — descriptive is a feature for a
    dev tool; renaming a published marketplace plugin is costly.
  - **Visual direction**: the **"reduce" pole** (Muji / Apple: calm,
    restraint, air, near-monochrome) over "express" — coherent with the
    plugin's ethos (plain Markdown, terminal, never guess, stdlib only:
    the constraints *are* the identity).
  - **Brand type**: a **tool brand with a light personal touch** (a small
    maker's note on the "Why" page), not maker-forward personal branding.
  - **Re-skin `PORTFOLIO.html`**: **yes**, as part of this work — once
    `DESIGN.md` exists, apply its tokens to `generate_portfolio.py` + the
    `STRINGS` table.
  - Still open for the spec: the enemy for the "Why" page (context loss /
    re-explaining every session), the concept/mood, the palette, the type.
    `impeccable` is the execution tool.

  Prerequisite for the **Public website** item below. Pre-brief:
  `docs/superpowers/research/2026-09-02-design-branding-SYNTHESE.md` § 5.

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
  - **Analytics:** **Cloudflare Web Analytics** (decided 2026-09-03 — free,
    cookieless, no consent banner, one script; publishing blind otherwise).
  - Use the `impeccable` skill for the visual execution.
  - **Visual direction / concept**: settled by the DA spec — the "reduce"
    pole, so the site is calm and restrained, not the loud impeccable
    register.

- [ ] **Obsidian integration (optional)** (S/M, ⭐) — surfaced 2026-09-14,
  brainstorm only. The tracking files are plain Markdown, so any scope
  root already opens as a valid Obsidian vault today with zero changes —
  first question for the eventual brainstorm is whether project-tracker
  should do anything at all beyond saying so. Options raised, none decided:
  - Just document the vault-compatibility (README /
    `writing-tracking-files.md`) — no code, no risk.
  - Ship an optional, gitignored `.obsidian/` config template (sensible
    workspace/graph defaults) so opting in "just works" on a scope root —
    strictly opt-in, never a dependency of the skill.
  - Cross-link tracking files with `[[wikilinks]]` to use the graph/
    backlinks — tension with the plain-Markdown / no-lock-in ethos and with
    GitHub rendering (wikilinks don't render as links there); leaning
    against unless a strong case emerges.
  Low priority, nothing else depends on it; needs a real brainstorm before
  any of it is built.

- [ ] **Skill audit: consider a centralized "lessons learned" /
  common-mistakes section** (M, ⭐) — surfaced 2026-09-17. Behavioural
  corrections today get woven into the relevant section rather than
  collected in one place; there is no single spot to scan "what we've
  learned not to do". Worth a design discussion before building — may
  conflict with the current integrated style; not a clear-cut win, revisit
  rather than execute blindly.

- [ ] **Skill audit: pressure-test the skill's behavioural rules with
  subagents** (L, ⭐) — surfaced 2026-09-17. `SKILL.md`'s prose rules
  (`never guess`, staying silent when nothing to report, asking a
  retroactive question exactly once, ...) have never been verified with the
  RED/GREEN pressure-scenario methodology from `superpowers:writing-skills`
  — only the deterministic code (hooks, portfolio generator, manifests) has
  tests. Would need baseline-without-skill / with-skill subagent runs per
  rule to actually confirm compliance rather than assume it from real usage
  so far.

## Completed

- [x] **Skill audit: extract `## Sub-projects` into its own reference file**
  (2026-09-19) — the ~57-line subsystem moved verbatim (cross-references
  retargeted) to `references/subprojects.md`; `SKILL.md` keeps a short stub
  with the in-session attach trigger and a "read it before…" pointer
  (386 → 335 lines). No behaviour change.

- [x] **Skill audit: lighten the `SKILL.md` frontmatter description**
  (2026-09-19) — reduced to trigger conditions only (no enumeration of the
  nine file names, no workflow summary).

- [x] **Portfolio: a detail sub-page per project** (2026-09-17) — each
  card in `PORTFOLIO.html` now links to its own `portfolio/<project>.html`
  (one HTML file per project, no client-side routing), rendering
  `STATUS.md` state + next actions, current `ROADMAP.md` phase, recent
  `JOURNAL.md` activity, the latest `CHANGELOG.md` version, and a direct
  GitHub link (inline SVG mark). A dependency-free Markdown→HTML fragment
  renderer was added to `generate_portfolio.py` for this; `STRINGS` en/fr
  extended with the new labels. `portfolio_regen.sh` regenerates only the
  changed project's sub-page on a targeted `STATUS.md`-write run; a
  manual/config-triggered full run regenerates every sub-page and cleans up
  orphans. Rides v0.12.0.

- [x] **Skill: log every discussion, even ideas later abandoned** (2026-09-17)
  — new `## Continuous updates` paragraph in `SKILL.md`: a design/scoping
  discussion is itself a trackable event, logged independently of the
  "significant change" judgment, even with no decision reached or the idea
  later dropped. One `JOURNAL.md` entry per *concluded* topic (never
  mid-discussion), plus a `BACKLOG.md` item for anything actionable; done
  automatically, no permission asked first. Rides v0.12.0.

- [x] **Nested tracking: an umbrella project with lightly-tracked git
  sub-repos** (2026-09-16) — a tracked project can now chaperone
  sub-projects: `subprojects:`/`nested_model:` frontmatter, a `## Sub-projects`
  section with a fixed flat file set (README/CHANGELOG/DECISIONS/ERRORS
  always, plus optional ARCHITECTURE) and the new `SUBPROJECTS.md`, detection +
  attachment reusing the bootstrap 3-way choice plus a one-time migration
  check for already-tracked projects, dual-context loading and a
  per-sub-project git/freshness check matrix, and an anti-duplication
  principle. Spec + plan:
  `docs/superpowers/{specs,plans}/2026-09-16-nested-tracking*.md`. Not yet
  released — bundled into v0.12.0.

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
