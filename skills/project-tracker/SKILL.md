---
name: project-tracker
description: Bootstraps and keeps up to date a standard set of markdown tracking files (README, ROADMAP, STATUS, JOURNAL, CHANGELOG, CLAUDE, DECISIONS, ERRORS, BACKLOG) for projects under the scopes defined in ~/.claude/project-tracker/scopes.txt, manages GitHub repo creation, and regenerates PORTFOLIO.html. Use it at the start of a session in a project under those scopes, after a significant change, or explicitly on request.
---

# project-tracker

## Overarching principle: never guess

Whenever a needed piece of information (the project's goal, its stack, the rationale for a decision, the content of a JOURNAL entry...) is missing or ambiguous: **ask the user**. Never infer, never invent plausible-looking content. A section with no answer stays marked "to fill in", never filled in by assumption.

## Scope

The file `~/.claude/project-tracker/scopes.txt` lists the covered roots. The `SessionStart` hook already only fires within that scope — but if the user invokes you explicitly in a folder outside any scope:
1. Warn them: "this folder is not in your automatic tracking scopes (`<list of scopes.txt entries>`)".
2. Carry on normally anyway — never act by refusing.
3. Offer to add a path to `scopes.txt` for the future: *"I'll add it to your scopes — this exact folder, or a parent path you'd rather specify?"*. If accepted, add the exact requested line to `~/.claude/project-tracker/scopes.txt`. If declined, add nothing and carry on.

## Detecting a project's root

The candidate root is the folder where the session was opened (`cwd`). Exception: if an ancestor of `cwd`, up to the scope root, already has a `docs/project-tracker/STATUS.md`, that ancestor is the tracked project's root (this avoids a false "new project" when a session is opened in a deep subfolder of an already-tracked project).

Three possible states:
- **Tracked**: `docs/project-tracker/STATUS.md` present at the root found.
  - If its frontmatter has **no** `reminders_list` key at all (never asked — distinct from a key present with the value `"non"`, which means declined): ask the Reminders linking question right away, before anything else, regardless of whether a significant change happens in this session (see `references/reminders-sync.md`) — this question must never wait for a "Continuous updates" trigger.
  - If its frontmatter has no `backlog_model` key at all: first check whether `ROADMAP.md` explicitly mentions/references a file named `BACKLOG.md` (at its standard location `docs/project-tracker/BACKLOG.md`, or at a non-standard path elsewhere in the project — e.g. nested in a subfolder; do not require it to be at the standard location, look instead for the explicit mention) — if so, the project has already adopted the model without going through the `project-tracker` bootstrap: write `backlog_model: "adopté"` directly, without asking; to decide whether to consolidate that file into `docs/project-tracker/` or leave it where it is, see `## Retrofitting an existing project` (two cases depending on whether a `STATUS.md` of its own exists at that path). Otherwise, ask the Backlog/Roadmap model adoption question (see `references/backlog-phases.md`), once, never asked again afterwards.
  - If `backlog_model` is `"adopté"` (or was just auto-recognized above) and the frontmatter has no `phase_model` key at all: check whether files matching `PHASE_N_SPEC.md` already exist in the project — if so, auto-recognize `phase_model: "leger"` without asking (same logic as above). Otherwise, do **not** ask a question here: `phase_model` stays absent until a phase is actually proposed (see `references/backlog-phases.md`, "How phases work").
  - If its frontmatter has **no** `category` key at all: propose a category (offering the values already used by other tracked projects, for reuse), then write it to the `category` frontmatter (the label, or `"non"` if the user declines). Once the key is written, never asked again.
  - If `~/.claude/project-tracker/portfolio.txt` does not exist: ask the user where the unified portfolio should go — offer `~/Desktop`, `~/Documents`, or another folder — and write the chosen **folder** path to `portfolio.txt`. If the user genuinely wants no portfolio, write a comments-only `portfolio.txt` (the hook then stays silent). Once the file exists (path or comments), never asked again — it is machine-global config, not per-project.
  - These checks are independent of one another — ask them one after another rather than all at once in the same message.
  - Then go to "Continuous updates".
- **Excluded**: the absolute path appears in `~/.claude/project-tracker/trackignore.txt` (an entry equal to a scope root ignores only that exact folder, not the projects inside it) → do nothing, unless the user brings it up explicitly.
- **New/unknown**: neither → go to "Bootstrapping a new project".

When you are invoked via the `SessionStart` hook reminder, it already tells you which of these three states applies (with the content of `STATUS.md` where relevant) — no need to re-detect it yourself in that case.

## Bootstrapping a new project

A sequence of questions, one at a time, never an assumption:

1. *"This folder isn't tracked yet — shall I set up tracking?"*
   - If no → add the folder's absolute path to `~/.claude/project-tracker/trackignore.txt` (create the file if it doesn't exist). End of flow, no justification required.
2. *"The project's goal in a few words?"* → will feed the README intro and the first STATUS.md.
3. *"Tech stack?"*
4. *"How do you want to handle git?"* — three options to offer:
   - **No git tracking** → skip the whole GitHub part below; record this choice in `CLAUDE.md` (`uses_git: false`) so the question is never asked again; staleness detection will rely on file modification dates rather than `git log`.
   - **Create a new GitHub repo** → ask *"What name for the repo?"* (default suggestion = folder name, to confirm or change). Then:
     ```bash
     gh auth status   # check before anything else
     ```
     If `gh` is missing or not authenticated: say so clearly, skip the GitHub part, carry on with the rest of the bootstrap without blocking.
     If OK:
     ```bash
     cd <project root>
     git init   # if not already a repo
     gh repo create <name> --private --source=. --remote=origin
     ```
     Commit the standard files once created (see below), then ask *"shall I push this first commit?"* before any `git push`.
   - **A repo already exists** → ask for the URL, then:
     ```bash
     git init   # if not already a repo
     git remote add origin <url>
     git fetch origin
     ```
     - If the remote repo is empty → nothing more, the first commit/push follows the normal flow above.
     - If the remote repo already contains files → attempt a merge (`git merge --allow-unrelated-histories origin/main` or the default branch). If there is a path conflict between local and remote content, do not decide it yourself: show the conflict to the user and ask how to reconcile (keep local, keep remote, merge by hand) before carrying on.
5. *"Do you want to link this project to a Reminders list, so I can also propose/track tasks from the Reminders app?"* — optional.
   - If the `reminders_lists` tool fails because no `apple-reminders` MCP server is available on this machine: same handling as "MCP tool unavailable" in `references/reminders-sync.md`, step 0 (offer to install it yourself, `user` scope mandatory) — do not block the rest of the bootstrap over it.
   - If yes and an existing list already matches the project (`reminders_lists` action `read`): offer to reuse it rather than create a new one.
   - If yes and no existing list fits: ask *"What name for the list?"* (default suggestion = project name, to confirm or change — never created without the name being confirmed), then create a new one flat (`reminders_lists` action `create`) — the tool cannot file it into a Reminders folder automatically, the user does that themselves if they want.
   - In every case (yes or no), write the answer to the `reminders_list` frontmatter (the list name, or `"non"` if declined — never an empty string, which is too easily confused with "not filled in yet") — never asked again. See `references/reminders-sync.md` for how it works once linked.
6. *"Category for this project?"* — read the `category` values already present in the other tracked projects' `STATUS.md` files (walk the roots in `~/.claude/project-tracker/scopes.txt`) and offer them for reuse (e.g. "already used: Work, Personal — or a new one") to avoid case/spelling duplicates. Write the answer to the `category` frontmatter (the label, or `"non"` if the user wants none). Never asked again for this project.
7. *"Is the project complex enough to deserve a separate `ARCHITECTURE.md`, or is `CLAUDE.md` enough?"* and *"any domain jargon that would justify a `GLOSSARY.md`?"* — optional, decided case by case; create them only if the answer is yes.

First run `mkdir -p docs/project-tracker/` at the project root, then create the standard files (next section) filled in with the answers obtained — never invented content for anything that wasn't answered. `README.md` and `CLAUDE.md` go at the project root; the 7 other standard files in `docs/project-tracker/` (see the next section for the per-file detail). `project:` in the frontmatter is always the folder's own name — never asked. The frontmatter of the `STATUS.md` thus created immediately includes `backlog_model: "adopté"`, written automatically along with the other fields — never asked as a question at this stage, since `BACKLOG.md` is one of the standard files created unconditionally (see next section).

If `~/.claude/project-tracker/portfolio.txt` does not exist yet (first tracked project on this machine), ask where the unified portfolio should go — `~/Desktop`, `~/Documents`, or another folder — and write the chosen folder path to `portfolio.txt`, so `PORTFOLIO.html` is generated from this first project. See the `portfolio.txt` bullet under `## Detecting a project's root`.

## The standard files

Nine files for each tracked project. `README.md` and `CLAUDE.md` at the project root (GitHub/Claude Code auto-discovery); the 7 others in `docs/project-tracker/`:

| File | Content | Cadence |
|---|---|---|
| `README.md` (root) | What, why, stack, install/run, links (repo, docs) | Rare |
| `docs/project-tracker/ROADMAP.md` | Prioritised synthesis derived from `BACKLOG.md`: past phases, current phase, anticipated phases — never the raw detail. See `references/backlog-phases.md` | Occasional |
| `docs/project-tracker/STATUS.md` | Snapshot of the current state (what works/breaks, 3 next actions) + machine-readable frontmatter (see below). **Fully rewritten**, does not accumulate | Every session / significant change |
| `docs/project-tracker/JOURNAL.md` | Dated chronological log of sessions: what was done, why | **Append-only**, every significant session |
| `docs/project-tracker/CHANGELOG.md` | Keep a Changelog format (Added/Changed/Fixed) per version | Every shippable change |
| `CLAUDE.md` (root) | Instructions for you: code conventions, build/test commands, known pitfalls, architecture summary, the project's git/GitHub choices | When conventions change |
| `docs/project-tracker/DECISIONS.md` | Why one technical choice over another, alternatives rejected | **Append-only**, one entry per structural decision |
| `docs/project-tracker/ERRORS.md` | Bug encountered → cause → fix, searchable | **Append-only**, every significant resolved bug |
| `docs/project-tracker/BACKLOG.md` | Raw, complete reservoir of every envisaged idea/feature (effort, perceived value). Never purged, enriched and archived. See `references/backlog-phases.md` | **Append-only** (archiving, never purging) |

Optional (created only if requested at bootstrap step 6, in `docs/project-tracker/`): `ARCHITECTURE.md`, `GLOSSARY.md`.

### `STATUS.md` frontmatter

```yaml
---
project: <folder name>   # always the folder's own name
status: active            # active | paused | blocked | archived
uses_git: true            # or false depending on the bootstrap choice
repo: https://github.com/<user>/<repo>   # empty if not applicable
stack: [Python, FastAPI, ...]
last_updated: <YYYY-MM-DD>
next_milestone: "<free text>"
reminders_list: "<Reminders list name>"   # "non" if declined, absent if never asked
category: "<free text>"   # "non" if the user declined a category, absent if never asked
backlog_model: "adopté"   # automatic at bootstrap; "non" only possible via a declined retrofit; absent only for a project tracked before this feature and not yet retrofitted
phase_model: "superpowers"   # or "leger"; absent if no phase ever proposed
---
```

This is the only strictly structured part of any of these files — the rest is free narrative. This frontmatter is what `generate_portfolio.py` consumes for the portfolio (see below): `project`, `status` and `last_updated` are mandatory, without them the project is simply omitted from the portfolio.

## Continuous updates

When you judge that you have made a significant change in a session (new feature, important fix, an architecture decision settled):
1. Re-read `STATUS.md` as it is right now (never a version seen earlier in the session), then rewrite it (state + 3 next actions, frontmatter up to date including `last_updated`).
2. Add a dated entry to `JOURNAL.md` (a real append — do not open the whole file to rewrite it, just add the new entry at the end).
3. Where relevant: add an entry to `CHANGELOG.md` (shippable change), `DECISIONS.md` (technical choice settled), or `ERRORS.md` (bug resolved) — always by appending, never by rewriting the whole file.
4. If `uses_git: true` and there are uncommitted changes lying around, point it out and offer a commit (conventional commits message) — never commit/push without explicit confirmation.
5. The Reminders sync itself is no longer triggered here (see `references/reminders-sync.md` — a `PostToolUse` hook handles it on the first change to `docs/project-tracker/STATUS.md`/`docs/project-tracker/ROADMAP.md` of each session (one reminder per session and per project)); the linking question, for a project that has never had it, is asked earlier — see `## Detecting a project's root` — not here.

This trigger (judging a change to be "significant") is your own judgment, not a mechanical rule. Safety net: the user can ask you for an update explicitly at any time — in that case, check the real state before writing anything (do not rewrite if nothing has actually changed since the last `last_updated`).

### Collisions between concurrent sessions

The user often works with several Claude Code sessions open in parallel on the same project. Before rewriting `STATUS.md` (or any file rewritten in full rather than accumulated):
- If `uses_git: true`: just before writing, check whether there is an uncommitted diff on this file that does not come from this session (`git diff -- docs/project-tracker/STATUS.md`). If so, do not overwrite: show the diff to the user and ask how to merge the two updates rather than deciding it yourself.
- Without git: compare the file's modification date with the one seen at your last read; if it has changed in the meantime, same handling (show, ask).

For `JOURNAL.md`, `CHANGELOG.md`, `DECISIONS.md`, `ERRORS.md`, `BACKLOG.md`: the write must always be a genuine append at the end of the file (or a targeted update of an existing item, e.g. ticking `[x]`) — never a "re-read everything / rewrite everything" cycle — so that two sessions each appending an entry in parallel do not overwrite one another.

## Reminders sync

If `reminders_list` (in the `STATUS.md` frontmatter) is linked (present, different from `"non"`): see `references/reminders-sync.md` for the trigger (hook + full diff + backfill), the `#tracker-sync` tag, the priority mapping, subtasks, and the consistency safeguard. The linking question itself is asked elsewhere — see `## Bootstrapping a new project` (step 5) and `## Detecting a project's root`.

## Portfolio

A `PostToolUse` hook (`hooks/portfolio_regen.sh`) regenerates `PORTFOLIO.html` automatically on every `STATUS.md` write, into the folder configured by `~/.claude/project-tracker/portfolio.txt` (a single file, all scopes aggregated). **Never run `generate_portfolio.py` yourself** — except once, with the user's approval, right after they change the portfolio folder or title via `/project-tracker:config` (the regeneration hook only fires on `STATUS.md` writes). If `portfolio.txt` does not exist yet, see the `portfolio.txt` bullet under `## Detecting a project's root`.

Projects are grouped into sections by the `category` frontmatter field — uncategorized first, then categories ordered by most recent activity.

To change the portfolio location or title, or any config (scopes, ignored paths, a project's category), the user runs `/project-tracker:config`.

## Retrofitting an existing project

When the project already has non-standard tracking files (e.g. `.pages` files, a `CLAUDE.md`/`JOURNAL.md` already present): treat it as a bootstrap, but reuse what already exists rather than asking the questions from scratch. If a source doc is not natively readable (e.g. Apple `.pages` files, zip binaries): say so clearly to the user and offer either that they export it to text/markdown/PDF, or to start straight from the bootstrap questions.

### Retrofitting the Backlog/Roadmap/Phases model

An already-tracked project may have its own `BACKLOG.md` (and sometimes `PHASE_N_SPEC.md` files) at a non-standard path, set up before this feature existed in `project-tracker`. Two cases to tell apart by whether or not a `STATUS.md` of its own exists in that subfolder:
- **A `STATUS.md` of its own exists in that subfolder**: it is a separately tracked project (its own root, its own `docs/project-tracker/`) — never merge its content into the enclosing project.
- **No `STATUS.md` of its own**: these are orphan detail files (not a tracking identity of their own) — consolidate them into the enclosing project's `docs/project-tracker/` rather than leaving them where they are.

The auto-recognition (see `## Detecting a project's root`) only fires if `ROADMAP.md` explicitly references that `BACKLOG.md` (whatever its path) — otherwise, ask the question normally, even if a `BACKLOG.md` exists somewhere in the project with no explicit link from `ROADMAP.md` (do not guess that it plays that role).

If the question is asked and accepted for a project that already has a `ROADMAP.md` and/or existing tracking content (e.g. a home-grown `docs/BACKLOG.md`, or a `ROADMAP.md` that already lists loose ideas): do not create an empty file alongside it — discuss with the user to summarize/reformat what already exists according to the structure in `references/backlog-phases.md`, case by case, rather than applying a generic script.
