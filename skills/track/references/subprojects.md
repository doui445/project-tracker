# Sub-projects

Referenced from `SKILL.md` (`## Sub-projects`, `## Detecting a project's root`, `## The standard files`, `## Continuous updates`, `## Portfolio`). Read this file before attaching a sub-project, creating or updating a sub-project's files, running the one-time `nested_model` migration check, or acting on a nested `.git` noticed in-session.

A tracked project can chaperone one or more **sub-projects**: sub-folders that each hold a genuine project of their own (an app, a module, a version) — never just any sub-folder used to store something. This is purely an organisational concept of this skill, not a git relationship: a sub-project with its own git repo is a fully independent repo (no submodule, no subtree, no git-level link to the parent), and the parent itself does not need to be a git repo at all — a parent's `uses_git` and a sub-project's own git presence are entirely independent settings.

A sub-project cannot itself have sub-projects (no multi-level nesting).

Renaming or moving a sub-project's folder is not auto-detected — if the user mentions it, update its `path` in `subprojects:` by hand; there is no automatic re-scan for this.

### States

Recorded per sub-project in the parent's `subprojects:` frontmatter list (`### STATUS.md frontmatter` in `SKILL.md`):
- `tracked: false` — known and listed by the parent (name + path), no files of its own.
- `tracked: true` — gets the fixed file set below.
- `status: active` / `archived`, independent of `tracked`. Archiving is never automatic or inferred from a name pattern — always ask explicitly, typically when a replacement appears (e.g. a v2 supersedes a v1): *"`<old>` looks superseded by `<new>` — mark `<old>` as archived?"* An `archived` sub-project is excluded from every check in `## Continuous updates` in `SKILL.md`.

### File set for a tracked sub-project

Fixed, never variable, all at the **root of the sub-project's own folder** — no `docs/` sub-folder at this scale:
- `README.md`, `CHANGELOG.md` — always.
- `ARCHITECTURE.md` — optional, the same one-time question as bootstrap step 7 (`## Bootstrapping a new project` in `SKILL.md`).
- `DECISIONS.md`, `ERRORS.md` — always.

Never the full nine files — a sub-project that needs its own phases/backlog/roadmap has outgrown this model and should become an independent tracked project instead, with a pointer kept from the parent's `SUBPROJECTS.md`.

Committed by default, same rule as every tracking file in this model (`## The standard files` in `SKILL.md`) — the same narrow sensitive-content exception applies, never the default.

No frontmatter of its own: every machine-readable fact (`tracked`/`git`/`status`) lives only in the parent's `subprojects:` list. The sub-project's own `CHANGELOG.md` uses the same dated Keep a Changelog format as every other `CHANGELOG.md` here (`## [X.Y.Z] — YYYY-MM-DD`) — its latest entry date is the freshness reference used in `## Continuous updates` in `SKILL.md`, no extra field needed.

If the sub-project already has some of these files before being attached, reuse them rather than starting fresh — same logic as `## Retrofitting an existing project` in `SKILL.md`.

### GLOSSARY.md stays single

A term specific to a sub-project still goes in the parent's own `docs/project-tracker/GLOSSARY.md` — there is no per-sub-project glossary.

### SUBPROJECTS.md

`docs/project-tracker/SUBPROJECTS.md`, on the **parent** — created on first need, like `GLOSSARY.md`: not asked at bootstrap, created (with a short note that it was) the moment the first sub-project is attached. One prose section per sub-project: why it exists, a current one-line status, a pointer to its own files. This is where sub-project *detail* lives — `STATUS.md`, `JOURNAL.md` and `ROADMAP.md` on the parent never duplicate it (see `## Continuous updates` in `SKILL.md`).

### Detecting and attaching a sub-project

A signal (typically a nested `.git`) triggers a **proposal**, never a silent decision. Dependency and build directories are never candidates and are never descended into — skip `node_modules` and any folder whose name starts with a dot (`.venv`, `.git` itself, …), the same pruning `generate_portfolio.py` already applies when it walks a scope. Reuse the exact 3-way choice from bootstrap step 1 (`## Bootstrapping a new project` in `SKILL.md`), per candidate:

- **Yes, attach it** *(recommended when the folder clearly holds its own project — its own git history, its own README)* → ask whether to track it in detail (`### File set for a tracked sub-project`) or just list it (`tracked: false`); write the entry to `subprojects:`; create/update `SUBPROJECTS.md`.
- **No, don't ask again** → add the folder's path to `~/.claude/project-tracker/trackignore.txt` — this also suppresses it from any future sub-project scan, not just from top-level tracking (`trackignore.txt`'s scope is shared between the two purposes).
- **Not now** → ask again next session; nothing is written.

When several candidates surface at once (typically during the one-time migration check below), present them **together in one grouped question** — never one question per candidate: *"I found these folders with their own git repo — attach as sub-projects? `<name>` (`<path>`), `<name>` (`<path>`)..."*, then apply the same 3-way choice per item inside that one exchange.

Without a nested-`.git` signal, attaching a sub-project only happens on the user's **explicit** request, and only for a genuine project (this file's opening paragraph) — never to file away an arbitrary folder.

**Ongoing detection — in-session triggers.** This detection is opportunistic, never a scan: a candidate surfaces in the course of normal work, and you propose it then. When either happens, make the proposal above:
- you are working inside a sub-folder of the project and see that it has its own `.git`;
- the user mentions, creates, or points you at a new sub-project of theirs.

It is never a scheduled re-walk of the project's tree at session start — that recurring cost, paid by every tracked project that will never have a sub-project, is exactly what the one-time flag below exists to avoid.

**One-time migration check.** Governed by the `nested_model` frontmatter key (`## Detecting a project's root` in `SKILL.md`): scans the project's sub-folders for candidates not yet in `subprojects:` nor in `trackignore.txt`, presents them as one grouped question if any are found, and writes `nested_model: "non"` once resolved — regardless of the outcome. If no candidate is ever found, the question never comes up and the key is still written once the (empty) check has run, so the scan itself doesn't repeat every session. This is a one-time catch-up for projects tracked before this feature existed; it is separate from the always-on detection above, which keeps noticing brand-new sub-folders in any session afterwards.
