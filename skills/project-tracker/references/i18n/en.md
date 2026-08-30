# i18n catalogue — English (`en`)

Canonical key list for the tracking-file headings and template phrases the
`project-tracker` skill writes. `fr.md` (and any future `<code>.md`) mirrors
this file: **same keys, same order**. A guard test enforces it.

**This file is the source of truth for the wording.** `SKILL.md`,
`references/writing-tracking-files.md` and `references/backlog-phases.md`
describe the *structure* of each file; wherever they name a heading, that
text must match a value here. When either side changes, reconcile the other.
`generate_portfolio.py` keeps its own `STRINGS` table (portfolio UI only) —
that one is not derived from this file.

**Never translated** (not listed here, kept verbatim in every language):
frontmatter keys and their enum values (`status: active|paused|blocked|archived`,
`"non"`, `"adopté"`, `"leger"`, `"superpowers"`), standard file names, hook
names, the tag `#tracker-sync`, language codes.

## STATUS.md

- status.title: STATUS — {project}
- status.intro: Snapshot of the current state. Fully rewritten each session.
- status.heading.where_it_stands: Where it stands
- status.heading.what_works: What works
- status.heading.known_gaps: Known gaps
- status.heading.next_actions: Next 3 actions

## ROADMAP.md

Structure is phase-dependent (see `references/backlog-phases.md`): with no
phase started, `current_focus` holds a simple prioritised list; once a phase
is running, `in_progress` and `after` replace it.

- roadmap.title: ROADMAP — {project}
- roadmap.intro: Prioritised synthesis. Raw detail lives in BACKLOG.md.
- roadmap.heading.done: Done
- roadmap.heading.current_focus: Current focus
- roadmap.heading.in_progress: Phase {n} — in progress
- roadmap.heading.after: After Phase {n}
- roadmap.heading.unprioritised: Unprioritised ideas

## JOURNAL.md

- journal.title: JOURNAL — {project}
- journal.intro: Dated chronological log. Append-only.
- journal.entry_heading: {date} — {topic}

## CHANGELOG.md

- changelog.title: Changelog — {project}
- changelog.intro: Format based on Keep a Changelog.
- changelog.heading.unreleased: Unreleased
- changelog.group.added: Added
- changelog.group.changed: Changed
- changelog.group.fixed: Fixed
- changelog.group.removed: Removed

## DECISIONS.md

- decisions.title: DECISIONS — {project}
- decisions.intro: Why each structural choice, and what was rejected. Append-only.
- decisions.label.context: Context
- decisions.label.decision: Chosen
- decisions.label.rejected: Rejected
- decisions.label.downside: Accepted downside

## ERRORS.md

- errors.title: ERRORS — {project}
- errors.intro: Bug then cause then fix, searchable. Append-only.
- errors.empty: No entries yet.
- errors.label.symptom: Symptom
- errors.label.cause: Root cause
- errors.label.fix: Fix
- errors.label.recognise: Recognise it again

## BACKLOG.md

- backlog.title: BACKLOG — {project}
- backlog.intro: Raw reservoir of every idea. Never purged, only archived.
- backlog.heading.high: High priority
- backlog.heading.medium: Medium priority
- backlog.heading.low: Low priority
- backlog.heading.completed: Completed
- backlog.heading.how_to_use: How to use this backlog
- backlog.none_open: (nothing open)

## Shared

- shared.to_fill_in: to fill in
- shared.none_yet: No entries yet.
