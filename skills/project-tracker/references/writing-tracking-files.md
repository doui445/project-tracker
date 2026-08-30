# Writing the tracking files well

Referenced from `SKILL.md` (`## The standard files`). The table there gives each
file's role and cadence; this file is the companion on *how to write each one*.
For `ROADMAP.md` and `BACKLOG.md` structure, `references/backlog-phases.md`
stays the single source of truth — only the prose notes below are added here.

## Principles that apply to every file

- **Never guess.** No invented rationale, no plausible-sounding filler. If a
  fact is missing, ask; leave the spot marked "to fill in" until you have it.
  A wrong entry is worse than an absent one.
- **Write for the reader of this file**, not for yourself now. Each file has a
  different reader (a stranger on GitHub, Claude next session, you in six
  months) — the sections below say who.
- **Every file earns its length.** Cut ceremony, restated context, and
  sentences that carry no information. Short is a feature.
- **Concrete over abstract.** Real names, paths, commands, error text — not
  "various files" or "some issues".
- **Match the project's voice and language.** If the repo and its `README`
  are in French, the tracking files are too (unless the user set otherwise).
- **Link, don't duplicate.** When one file already covers something, point to
  it rather than restating it — restated content drifts out of sync.

## `README.md` (project root)

**Reader:** someone who just landed on the repo and knows nothing.

- Open with a plain-language hook: what it does and why, in the first sentence,
  with no jargon the reader hasn't met yet.
- Put a **Quick start** near the top — the reader should reach "how do I run
  this" without scrolling far.
- **Progressive disclosure:** essentials first (what, quick start, the handful
  of headline capabilities), then reference and edge cases lower down (a
  "Details" section, or a link to deeper docs).
- Show, don't only tell: at least one concrete command or example.
- Keep "what it does" to a handful of bullets. A wall of bullets covering every
  edge case belongs lower or in another doc.
- Link out to the deeper specification instead of inlining all of it.

> **Poor:** *"project-tracker is a Claude Code skill that bootstraps and
> maintains a standard set of Markdown tracking files for every project under
> configured scope roots, with SessionStart auto-detection, PostToolUse hooks,
> and a deterministic portfolio regenerator."* — jargon-first, no "why", no
> entry point.
>
> **Better:** *"Open a Claude Code session in one of your projects and it keeps
> a small set of Markdown files — STATUS, ROADMAP, JOURNAL… — current as you
> work, so you and Claude always have the project's context in one place."*
> then a two-line Quick start.

## `CLAUDE.md` (project root)

**Reader:** Claude, loaded at the start of every session, on a tight context
budget.

- **Instructions, not narration.** Imperative and terse. This file is read
  every session — every wasted line has a recurring cost.
- Include **only what changes what Claude does**: code conventions, the exact
  build/test/lint commands, known pitfalls, the project's git/GitHub choice,
  a one-paragraph architecture orientation.
- **No history, no rationale, no decision log** — that is `JOURNAL.md` /
  `DECISIONS.md`. Link to them instead.
- Commands must be runnable verbatim, copy-paste ready.
- "Known pitfalls" = things Claude would otherwise get wrong (a non-obvious
  test setup, a file that must not be hand-edited, a naming rule).
- Routines Claude runs belong here too — e.g. a **release routine** (how to
  bump the version, regenerate artefacts, tag). Keep the versioning *scheme*
  (what counts as major/minor/patch) in the `CHANGELOG.md` header and the
  step-by-step here; don't create a separate file for either.

> **Poor:** *"This project was started in August after we decided against a
> Rails backend (see the discussion in the July notes). The architecture has
> evolved a lot since then…"* — history, belongs in `DECISIONS.md`.
>
> **Better:** *"Build: `make build`. Test: `python -m pytest -q`. Never
> hand-edit `install.sh` — regenerate it with `scripts/build_installer.sh`.
> Commits: conventional style, present tense."*

## `STATUS.md`

**Reader:** anyone (you, Claude, a collaborator) asking "where is this right
now?". Fully rewritten each time — it never accumulates.

**Belongs here:**

- The current state in the present tense: what works, what is broken.
- Exactly three next actions, each phrased as an action ("wire the export
  button to the API"), not a theme ("exports").
- Frontmatter correct on every rewrite — especially `last_updated`.

**Does not belong here:**

- History of how you got here → `JOURNAL.md`.
- Rationale for choices → `DECISIONS.md`.
- The full idea list → `BACKLOG.md`.
- Aspirational claims. Write what is true now, not "should work".

Keep it short. If a section is growing, the detail belongs in another file.

## `JOURNAL.md`

**Reader:** you or Claude reconstructing *why* something happened. Append-only,
newest entry at the bottom.

- One dated entry per significant session. Skip trivial changes.
- Record **what was done and why** — the *why* is the point; the *what* is
  already in `git log`.
- Past tense, factual, brief. Link to `DECISIONS.md` / `ERRORS.md` for depth
  rather than expanding inline.
- Never rewrite or reorder earlier entries. A later correction is a new entry.

## `CHANGELOG.md`

**Reader:** someone deciding whether to upgrade, or looking for when a change
landed. [Keep a Changelog](https://keepachangelog.com/) format.

- Group under **Added / Changed / Fixed / Removed**, per version.
- User-facing language: what changed for someone *using* the project, not a
  restatement of the diff.
- Keep an `[Unreleased]` section at the top that accumulates until a release,
  then rename it to the version with a date.
- One line per change, a noun phrase or an imperative.
- State the project's **versioning scheme** in the header (what a major /
  minor / patch bump means here) — this is its home, not a separate file.

## `DECISIONS.md`

**Reader:** someone about to change something and wondering why it is the way
it is. Append-only, one entry per structural decision.

- Structure each entry: **context → decision → alternatives rejected (and why)
  → the downside you accepted.**
- Only **structural or hard-to-reverse** choices — a library that shapes the
  code, a data model, a boundary. Not every small pick.
- Write it when the decision is made, while the reasoning is fresh.
- **Never guess a rationale.** If you don't know why a past choice was made,
  ask — don't reconstruct a plausible story.
- Dated. Never edit an entry later; if the decision is reversed, add a new
  entry that says so and references the old one.

## `ERRORS.md`

**Reader:** someone hitting a bug that smells familiar, searching this file.
Append-only.

- Make it **searchable**: include the actual error text or the concrete
  symptom, in the words it appears in.
- Structure: **symptom → root cause → fix → how to recognise it again.**
- Only non-trivial bugs that cost real time — not typos caught in a minute.
- The **root cause** is the value. "Added a null check" without the underlying
  reason helps no one.

## `ROADMAP.md`

**Reader:** someone asking "what's the plan?". Structure and phase mechanics:
`references/backlog-phases.md`. Prose notes only:

- It is a **synthesis derived from `BACKLOG.md`**, never a copy of it. No
  effort/value estimates, no technical detail — point to `BACKLOG.md` for
  that.
- One line per past phase. Detail lives in `STATUS.md` / `CHANGELOG.md`.
- Lists over paragraphs, except where a sentence of framing genuinely helps.

## `BACKLOG.md`

**Reader:** you, grooming ideas and picking what to do next. Structure:
`references/backlog-phases.md`. Prose notes only:

- Terse per item — a line or two, plus effort (S/M/L) and value (⭐–⭐⭐⭐).
  Deep design for an item goes in its phase spec, not here.
- Organised by **priority, not date**.
- Archive completed items to a "Completed" section — never delete them.
- It is allowed to be large and a little messy. It is a grooming tool, not a
  list of commitments.

## `ARCHITECTURE.md` (optional)

**Reader:** someone about to make a change and needing to not break things.
Created only if the project is complex enough to warrant it.

**Writing the doc:**

- **Big picture first:** the major components, one line each, and how they fit
  together — a diagram, or a plain component list plus the data flow.
- **Boundaries:** what each component is responsible for, and what it is
  explicitly *not*.
- The **key interfaces** between components, and **where state lives**.
- The load-bearing decisions → link to `DECISIONS.md`, don't restate them.
- What is **deliberately simple** or **deliberately deferred** (a YAGNI
  record — it stops future readers from "fixing" a non-problem).
- **Keep it current or delete it.** A stale architecture doc misleads more
  than no doc.

**A lens for judging the architecture itself** (guidance, not a rulebook —
context wins):

- Each unit has a single purpose you can state in one sentence.
- Units talk through defined interfaces, not shared internals. You can
  understand one without reading the internals of the others, and change its
  internals without breaking its consumers.
- Dependencies run in one direction (no cycles) and point toward the stable,
  general parts.
- Duplication of *knowledge* is removed; incidental, coincidental duplication
  is left alone.
- No speculative generality — an abstraction has to earn its place with a
  second real caller.
- Module/file size is a signal: when one grows large it is usually doing too
  much.
- The structure follows the domain, not the framework.
- Error handling is explicit at the boundaries.

## `GLOSSARY.md` (optional)

**Reader:** a newcomer (human or Claude) trying to read the code and docs
without guessing at the jargon. A real project dictionary.

- **Each entry:** the term → what it means *in this project* → where it shows
  up (a file, a module, a workflow) → a short example sentence or usage
  context.
- Give the **project meaning**, not the generic dictionary definition — unless
  the project's use differs from the common one, in which case say how.
- **Highest value:** common words that are *overloaded* here — a plain word
  that carries a specific meaning in this codebase, different from its everyday
  sense. Capture those first.
- Also include: domain jargon, terms the project coined, acronyms.
- **Exclude** standard industry terms used in the standard way — don't define
  "API" or "cache".
- Entries stay short (a sentence or two plus the context pointer). Order
  alphabetically or group by theme. Cross-link related terms.
- **Never guess a definition.** If you are not sure what a term means here,
  ask the user — a confidently wrong glossary entry is a trap.
