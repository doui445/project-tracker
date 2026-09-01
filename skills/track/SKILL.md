---
name: track
description: Bootstraps and keeps up to date a standard set of markdown tracking files (README, ROADMAP, STATUS, JOURNAL, CHANGELOG, CLAUDE, DECISIONS, ERRORS, BACKLOG) for projects under the scopes defined in ~/.claude/project-tracker/scopes.txt, manages GitHub repo creation, and regenerates PORTFOLIO.html. Use it at the start of a session in a project under those scopes, after a significant change, or explicitly on request.
---

# project-tracker

## Overarching principle: never guess

Whenever a needed piece of information (the project's goal, its stack, the rationale for a decision, the content of a JOURNAL entry...) is missing or ambiguous: **ask the user**. Never infer, never invent plausible-looking content. A section with no answer stays marked "to fill in", never filled in by assumption.

## Asking questions

Assume the person answering is not a Claude Code power user. Every question you put to them (this section's phrasings are the intent, not a script — adapt to the conversation and its language):

- **Plain language.** No unexplained jargon. If a term is unavoidable (`frontmatter`, `remote`, `scope`), gloss it in the same sentence.
- **Say what each choice changes.** When the options have real consequences, give one short clause per option describing the effect — not just the label. The person should be able to choose without knowing the tool.
- **Recommend.** Mark one option **(recommended)** and base it on what you can see (the repo has a git remote, the `README` is in French, other tracked projects use a "Work" category, …). If nothing in the context points one way, say "no strong default" instead of a fake recommendation.
- Keep it to the decision at hand. One question per message; don't stack the bootstrap questions into one wall.

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
  - If its frontmatter has **no** `category` key at all: ask for a category the same way as bootstrap step 6 (*"A category, to group this with your other projects on the portfolio page"*, offering the ones already in use + "a new one" + "no category", recommending an existing one only on a clear match). Write the label to `category` (or `"non"`). Once written, never asked again.
  - If `docs/project-tracker/GLOSSARY.md` does **not** exist and the frontmatter has no `glossary` key: glance at the code and `README.md`; if the project carries a clear domain vocabulary of its own (coined terms, business jargon, common words used with a specific local meaning — not standard industry terms), propose starting `docs/project-tracker/GLOSSARY.md` with the terms you spotted. If accepted, create it (leave `glossary` absent — the file's existence is the signal). If declined, write `glossary: "non"`. Once `GLOSSARY.md` exists **or** `glossary` is `"non"`, this proactive check never runs again — but the in-session triggers (`## Continuous updates`) still add terms, creating the file if needed.
  - If `~/.claude/project-tracker/portfolio.txt` does not exist: ask where to save the portfolio page (*"`PORTFOLIO.html` is a single page listing all your tracked projects — where should it live?"*) — offer `~/Documents` **(recommended — tidy and permanent)**, `~/Desktop` (always in view), another folder, or "don't make one". Write the chosen folder path to `portfolio.txt`; for "don't make one" write a comments-only `portfolio.txt` (the hook stays silent). Machine-global, never asked again.
  - If `~/.claude/project-tracker/language.txt` does not exist: ask which language the tracking files and portfolio should be written in — **English** / **French**, recommending whichever the project's `README` is in (or, failing that, the language the user is writing to you in). Write the code (`en` / `fr`) to `language.txt`. Machine-global, never asked again.
  - Otherwise: resolve the effective language and glance at `STATUS.md`. If it is visibly in the other language, offer the full retranslation (see `references/writing-tracking-files.md`, `## Retranslating on a language change`).
  - If `~/.claude/project-tracker/prefs.txt` does not exist: ask once about the console view — see `## Console view preference` below — and write `prefs.txt`. Machine-global, never asked again. If `prefs.txt` says `console_view: chat-local` and the current project has no `.claude/settings.local.json` setting `defaultView`, apply it now (see that section).
  - These checks are independent of one another — ask them one after another rather than all at once in the same message.
  - Then go to "Continuous updates".
- **Excluded**: the folder is ignored via `~/.claude/project-tracker/trackignore.txt` — either its own absolute path is a line there (an entry equal to a scope root ignores only that exact folder, not the projects inside it), or a non-scope-root ancestor is. → do nothing, unless the user brings it up explicitly.
  - If the user brings it up **to ask for it to be tracked** ("track this", "let's track this one"):
    - If the folder's **own path** is the `trackignore.txt` line: offer to remove that line, then go to "Bootstrapping a new project". (Symmetric with bootstrap step 1, which adds the line on a declined setup.)
    - If it is an **ancestor** that is ignored (the folder's own path is not a line): explain plainly that a parent folder is on the skip list, so there's no way to track just this one without also un-skipping everything else under that parent. Offer: **remove the parent from the skip list** (then bootstrap this folder — but every project under that parent becomes eligible for tracking too), or **leave it as is** *(recommended unless you do want the whole subtree tracked)*.
  - If the user brings it up for anything else: unchanged — do nothing about the tracking state.
- **New/unknown**: neither → go to "Bootstrapping a new project".

When you are invoked via the `SessionStart` hook reminder, it already tells you which of these three states applies (with the content of `STATUS.md` where relevant) — no need to re-detect it yourself in that case.

## Bootstrapping a new project

A sequence of questions, one at a time (see `## Asking questions`), never an assumption:

1. **On an untracked project this is the session's opening move — asked automatically, before responding to anything else. The user never has to request it.** (An *excluded* project stays silent — tracking there starts only if the user raises it, see the **Excluded** bullet under `## Detecting a project's root`.) Ask via `AskUserQuestion` (selectable choices, not prose). Intent:
   *"I can keep a small set of notes files for this project — what it does, current status, a changelog, decisions — updated as we work, so the context is always in one place. Set that up here?"*
   - **Yes, set it up** *(recommended when the folder holds a real project — source files, a git repo, a README)* → a few quick questions, then the files are created (step 2).
   - **No, don't ask again** → this folder is added to the skip list (`trackignore.txt`); never offered again.
   - **Not now** → nothing is written; you'll be asked again next time you open a session here.
2. *"What is this project for? One or two sentences."* → feeds the `README` intro and the first `STATUS.md`.
3. *"What's it built with — main languages, frameworks, key tools?"*
4. *"How is this project's code version-controlled?"* — offer:
   - **Already on GitHub (or another git remote)** *(recommended if the folder has a `.git` with a remote set)* → ask for the URL if it isn't already configured; the tracking files get committed alongside the code.
     ```bash
     git init   # if not already a repo
     git remote add origin <url>
     git fetch origin
     ```
     - Remote is empty → nothing more; the first commit/push follows the normal flow below.
     - Remote already has files → attempt a merge (`git merge --allow-unrelated-histories origin/main` or the default branch). On a path conflict, don't decide it yourself: show it and ask how to reconcile (*keep the local copy* / *keep what's on the remote* / *I'll merge them by hand*).
   - **Create a new private GitHub repo now** → ask *"Name for the new repo? (default: the folder's name)"*. Needs `gh` logged in:
     ```bash
     gh auth status   # check first
     ```
     If `gh` is missing or logged out: say so plainly, skip the GitHub part, carry on with the rest of the bootstrap.
     If OK:
     ```bash
     cd <project root>
     git init   # if not already a repo
     gh repo create <name> --private --source=. --remote=origin
     ```
     After the standard files are created, ask *"Push this first commit to GitHub now?"* *(recommended: yes)* before any `git push`.
   - **No version control** *(recommended if there's no `.git` and you don't want one)* → skip the whole GitHub part; record `uses_git: false` in `CLAUDE.md` so it's never asked again; staleness is then judged from file dates instead of `git log`.
5. *"Do you want your next actions to also show up in the macOS Reminders app, so you see them outside your editor?"* — optional.
   - **Yes** *(recommended only if this machine already has the Reminders integration and your other tracked projects use it)* → a Reminders list is created or linked, and its tasks stay in sync with the "next actions" here.
   - **No** *(the low-friction default)* → the next actions live in the tracking files only.
   - If the `reminders_lists` tool fails because the `apple-reminders` MCP server isn't installed: handle as "MCP tool unavailable" in `references/reminders-sync.md` step 0 (offer to install it, `user` scope) — don't block the bootstrap over it.
   - Yes + an existing list already fits (`reminders_lists` action `read`) → offer to reuse it rather than make a new one.
   - Yes + no list fits → ask *"Name for the Reminders list? (default: the project's name)"*, then create it flat (`reminders_lists` action `create`) — the tool can't file it into a Reminders folder, the user does that themselves.
   - Either way, write the answer to the `reminders_list` frontmatter (the list name, or `"non"` if declined — never an empty string). Never asked again. See `references/reminders-sync.md`.
6. *"A category for this project? It groups it with your other projects on the portfolio page (e.g. Work, Personal, a client name)."* — read the `category` values already used by the other tracked projects (walk the `scopes.txt` roots) and offer them for reuse, plus "a new one" and "no category". *(Recommend an existing category if the project's nature clearly matches one; otherwise no strong default.)* Write the label to the `category` frontmatter (or `"non"` for none). Never asked again for this project.
7. *"Is this project big or intricate enough to want a separate architecture document, or is a short orientation paragraph in `CLAUDE.md` enough?"*
   - **`CLAUDE.md` is enough** *(recommended for most projects)* → a one-paragraph orientation, no extra file.
   - **A separate `ARCHITECTURE.md`** *(recommended only for a genuinely large system — many modules or services)* → a full doc: components, boundaries, data flow.
   (`GLOSSARY.md` is **not** asked here — it appears later, on first need; see `## Detecting a project's root` and `## Continuous updates`.)

First run `mkdir -p docs/project-tracker/` at the project root, then create the standard files (next section) filled in with the answers obtained — never invented content for anything that wasn't answered. `README.md` and `CLAUDE.md` go at the project root; the 7 other standard files in `docs/project-tracker/` (see the next section for the per-file detail). `project:` in the frontmatter is always the folder's own name — never asked. The frontmatter of the `STATUS.md` thus created immediately includes `backlog_model: "adopté"`, written automatically along with the other fields — never asked as a question at this stage, since `BACKLOG.md` is one of the standard files created unconditionally (see next section).

If `~/.claude/project-tracker/portfolio.txt` does not exist yet (first tracked project on this machine), ask where the unified portfolio should go — `~/Desktop`, `~/Documents`, or another folder — and write the chosen folder path to `portfolio.txt`, so `PORTFOLIO.html` is generated from this first project. See the `portfolio.txt` bullet under `## Detecting a project's root`.

Likewise, if `~/.claude/project-tracker/language.txt` does not exist, ask once which language the tracking files and portfolio should use (English / French) and write the code to `language.txt`. The bootstrap then creates every file in that language (consult `references/i18n/<code>.md` when it is not `en`). No per-project `language:` key is written at bootstrap — it exists only as an explicit override set later via `/project-tracker:config`.

And if `~/.claude/project-tracker/prefs.txt` does not exist, ask the console-view question once (see `## Console view preference`) and write `prefs.txt`.

Once `README.md` (and `ARCHITECTURE.md` / `GLOSSARY.md` if you created them) are written, run the fresh-eyes readability pass on each — see `references/writing-tracking-files.md` (`## The fresh-eyes readability pass`).

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

Two optional files, both in `docs/project-tracker/`:
- `ARCHITECTURE.md` — created at bootstrap (step 7) if the project is complex enough.
- `GLOSSARY.md` — **created on first need**, not at bootstrap (see `## Detecting a project's root` for the proactive check, `## Continuous updates` for the in-session triggers).

How to write each of these well — reader, structure, what belongs and what does not, worked good/poor examples: see `references/writing-tracking-files.md`. Consult it whenever you create or substantially rewrite one of these files.

**These files are committed like any other source** — they are the project's memory, `CHANGELOG.md` / `DECISIONS.md` / `ROADMAP.md` are standard public artifacts, and the concurrent-session safeguard below relies on `git diff` seeing `STATUS.md`. Do not add them to `.gitignore`. The only exception: on a public repo whose `STATUS.md` / `JOURNAL.md` / `BACKLOG.md` would carry genuinely sensitive content (unreleased strategy, client names), those three may be ignored while `CHANGELOG.md` / `DECISIONS.md` / `ROADMAP.md` stay committed — never the default, only on request.

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
language: fr              # en | fr ; absent = inherit language.txt
glossary: "non"           # "non" = proactive glossary scan declined; absent = not yet checked; unset once GLOSSARY.md exists
---
```

This is the only strictly structured part of any of these files — the rest is free narrative. This frontmatter is what `generate_portfolio.py` consumes for the portfolio (see below): `project`, `status` and `last_updated` are mandatory, without them the project is simply omitted from the portfolio.

`language` is an optional per-project override for the tracking files' language (not the portfolio, not reminders); absent means follow `~/.claude/project-tracker/language.txt`.

## Output language

Everything the skill *writes into a project's tracking files* follows a
resolved **effective language**:

1. `language:` in that project's `STATUS.md` frontmatter, if present;
2. else `~/.claude/project-tracker/language.txt` (machine-global);
3. else `en`.

`PORTFOLIO.html` follows the `language:` line of `portfolio.txt` if present,
else `language.txt`, else `en`. Reminders items you create follow
`language.txt` (global) — never the per-project override. The **chat** (the
questions you ask, the discussion) always follows the language the user is
writing in this session — it is not driven by any of these settings.

Supported: `en`, `fr`. Machine values are never translated in any language:
frontmatter keys and enum values (`status: active|paused|…`, `"non"`,
`"adopté"`, `"leger"`, `"superpowers"`), file names, hook names,
`#tracker-sync`, the language codes.

**When the effective language is not `en`:** before creating or rewriting a
tracking file, read `references/i18n/<code>.md` and use its section headings
and template phrases verbatim; write all free prose in that language. `en.md`
holds the English originals.

**When the effective language changed** and the project already has content
in the old language (you notice it by glancing at `STATUS.md` — `en` vs `fr`
is unambiguous): propose the full retranslation — see
`references/writing-tracking-files.md` (`## Retranslating on a language change`).

## Console view preference

This skill rewrites several Markdown files per session, which fills the
transcript with edit diffs. Asked once per machine (when `prefs.txt` is
absent — see `## Detecting a project's root`), never again:

> *"project-tracker updates several tracking files each session — that fills
> the transcript with edit diffs. Fold Claude Code's view to the condensed
> 'chat' mode? It hides tool activity (reversible in `/config`, and `Ctrl+O`
> toggles it live)."*

Offer three choices, via `AskUserQuestion`:

- **Only in tracked projects** *(recommended — folds the noise exactly where
  it happens, leaves your other work untouched)* → in the current project,
  merge `{"defaultView": "chat"}` into `.claude/settings.local.json` (create
  it if missing) and make sure `.claude/settings.local.json` is in that
  project's `.gitignore`. Write `console_view: chat-local` to `prefs.txt`. On
  every later bootstrap of a new tracked project, apply the same local
  setting there (checked in `## Detecting a project's root`).
- **Everywhere** → the condensed view in *all* your Claude Code sessions.
  Merge `"defaultView": "chat"` into `~/.claude/settings.json` (read it
  first, never clobber). Write `console_view: chat-global` to `prefs.txt`.
- **No** → leave the view as it is. Write `console_view: full` to `prefs.txt`;
  mention `/config` and `Ctrl+O` once, then drop it.

`prefs.txt` is machine-global config (same family as `scopes.txt` /
`portfolio.txt` / `language.txt`): `key: value` per line, `#` comments. Its
existence is the "already asked" signal. Changed later via
`/project-tracker:config`.

## Continuous updates

When you judge that you have made a significant change in a session (new feature, important fix, an architecture decision settled):
1. Re-read `STATUS.md` as it is right now (never a version seen earlier in the session), then rewrite it (state + 3 next actions, frontmatter up to date including `last_updated`). Write it in the project's effective language (see `## Output language`); if that is not `en`, consult `references/i18n/<code>.md` for the headings.
2. Add a dated entry to `JOURNAL.md` (a real append — do not open the whole file to rewrite it, just add the new entry at the end).
3. Where relevant: add an entry to `CHANGELOG.md` (shippable change), `DECISIONS.md` (technical choice settled), or `ERRORS.md` (bug resolved) — always by appending, never by rewriting the whole file.
4. If `uses_git: true` and there are uncommitted changes lying around, point it out and offer a commit (conventional commits message) — never commit/push without explicit confirmation.
5. The Reminders sync itself is no longer triggered here (see `references/reminders-sync.md` — a `PostToolUse` hook handles it on the first change to `docs/project-tracker/STATUS.md`/`docs/project-tracker/ROADMAP.md` of each session (one reminder per session and per project)); the linking question, for a project that has never had it, is asked earlier — see `## Detecting a project's root` — not here.

This trigger (judging a change to be "significant") is your own judgment, not a mechanical rule. Safety net: the user can ask you for an update explicitly at any time — in that case, check the real state before writing anything (do not rewrite if nothing has actually changed since the last `last_updated`).

**`GLOSSARY.md` — in-session triggers.** Independent of the "significant change" judgment above. When either happens, add the term to `docs/project-tracker/GLOSSARY.md` — **create the file if it does not exist, with that first entry, and say so** (no separate question for a single term); if `glossary` was `"non"`, drop the key, the file now exists:
- the user asks what a **project-specific** term means (coined term, jargon, a common word used with a specific local meaning — not a standard industry term): answer, then add it, with the project meaning + where it shows up + a short usage example;
- a project-specific term keeps coming up undefined while you work.
Format and what to include/exclude: `references/writing-tracking-files.md` (`## GLOSSARY.md`).

**Onboarding files — fresh-eyes readability pass.** If this session substantially rewrote or restructured an onboarding file (`README.md` / `CLAUDE.md` / `ARCHITECTURE.md` / `GLOSSARY.md` — not a targeted edit), run the fresh-eyes readability pass on it before finishing: `references/writing-tracking-files.md` (`## The fresh-eyes readability pass`). Advisory, never a gate.

### Collisions between concurrent sessions

The user often works with several Claude Code sessions open in parallel on the same project. Before rewriting `STATUS.md` (or any file rewritten in full rather than accumulated):
- If `uses_git: true`: just before writing, check whether there is an uncommitted diff on this file that does not come from this session (`git diff -- docs/project-tracker/STATUS.md`). If so, do not overwrite: show the diff to the user and ask how to merge the two updates rather than deciding it yourself.
- Without git: compare the file's modification date with the one seen at your last read; if it has changed in the meantime, same handling (show, ask).

For `JOURNAL.md`, `CHANGELOG.md`, `DECISIONS.md`, `ERRORS.md`, `BACKLOG.md`: the write must always be a genuine append at the end of the file (or a targeted update of an existing item, e.g. ticking `[x]`) — never a "re-read everything / rewrite everything" cycle — so that two sessions each appending an entry in parallel do not overwrite one another.

## Reminders sync

If `reminders_list` (in the `STATUS.md` frontmatter) is linked (present, different from `"non"`): see `references/reminders-sync.md` for the trigger (hook + full diff + backfill), the `#tracker-sync` tag, the priority mapping, subtasks, and the consistency safeguard. The linking question itself is asked elsewhere — see `## Bootstrapping a new project` (step 5) and `## Detecting a project's root`. Items you create in the Reminders app are written in the machine-global `language.txt` language, not the per-project override.

## Portfolio

A `PostToolUse` hook (`hooks/portfolio_regen.sh`) regenerates `PORTFOLIO.html` automatically on every `STATUS.md` write, into the folder configured by `~/.claude/project-tracker/portfolio.txt` (a single file, all scopes aggregated). **Never run `generate_portfolio.py` yourself** — except once, with the user's approval, right after they change the portfolio folder, title or language via `/project-tracker:config` (the regeneration hook only fires on `STATUS.md` writes). If `portfolio.txt` does not exist yet, see the `portfolio.txt` bullet under `## Detecting a project's root`.

`portfolio.txt` holds the output **folder** on its first line that is neither a `title:` nor a `language:` line (a line ending in `.html` is taken as an explicit file path instead); `~`/`$VAR` are expanded. An optional `title:` line anywhere in the file sets the portfolio heading (default, locale-dependent: "My projects" / "Mes projets"); an optional `language:` line (`en`/`fr`) overrides the portfolio's output language. All three are edited via `/project-tracker:config`, never written by this skill directly.

Projects are grouped into sections by the `category` frontmatter field — uncategorized first, then categories ordered by most recent activity.

To change the portfolio location, title or language, or any config (scopes, ignored paths, output language, a project's category), the user runs `/project-tracker:config`.

## Retrofitting an existing project

When the project already has non-standard tracking files (e.g. `.pages` files, a `CLAUDE.md`/`JOURNAL.md` already present): treat it as a bootstrap, but reuse what already exists rather than asking the questions from scratch. If a source doc is not readable as plain text (Apple `.pages`, a zip): say so plainly and offer — *"I can't read `<file>` directly. Export it to text/Markdown/PDF for me, or should I just start fresh from the setup questions?"* *(recommend exporting if the file clearly holds real history worth keeping; otherwise starting fresh)*.

### Retrofitting the Backlog/Roadmap/Phases model

An already-tracked project may have its own `BACKLOG.md` (and sometimes `PHASE_N_SPEC.md` files) at a non-standard path, set up before this feature existed in `project-tracker`. Two cases to tell apart by whether or not a `STATUS.md` of its own exists in that subfolder:
- **A `STATUS.md` of its own exists in that subfolder**: it is a separately tracked project (its own root, its own `docs/project-tracker/`) — never merge its content into the enclosing project.
- **No `STATUS.md` of its own**: these are orphan detail files (not a tracking identity of their own) — consolidate them into the enclosing project's `docs/project-tracker/` rather than leaving them where they are.

The auto-recognition (see `## Detecting a project's root`) only fires if `ROADMAP.md` explicitly references that `BACKLOG.md` (whatever its path) — otherwise, ask the question normally, even if a `BACKLOG.md` exists somewhere in the project with no explicit link from `ROADMAP.md` (do not guess that it plays that role).

If the question is asked and accepted for a project that already has a `ROADMAP.md` and/or existing tracking content (e.g. a home-grown `docs/BACKLOG.md`, or a `ROADMAP.md` that already lists loose ideas): do not create an empty file alongside it — discuss with the user to summarize/reformat what already exists according to the structure in `references/backlog-phases.md`, case by case, rather than applying a generic script.
