# Backlog / Roadmap / Phases

Referenced from `SKILL.md` (`## The standard files`, `## Bootstrapping a new project`, `## Detecting a project's root`, `## Retrofitting an existing project`). Applies to every tracked project — `BACKLOG.md` exists for all of them, even empty at the start, created unconditionally and without a question by the bootstrap (`backlog_model: "adopté"` written automatically in that case — see `## Bootstrapping a new project` in `SKILL.md`; the declined `"non"` only exists via the retrofit path of a project that predated this feature, see `## Retrofitting an existing project`); the phase mechanism below only kicks in once enough items accumulate.

## `BACKLOG.md` — raw reservoir

Every idea/feature envisaged for the project, never purged — only enriched and archived. Organised by priority (high/medium/low, or "no defined priority"/"unprioritised ideas" for what isn't even sorted yet) rather than chronologically. For each item, as far as possible: estimated effort (S/M/L) and perceived value (⭐ to ⭐⭐⭐) — helps decide what to group into a phase. Statuses `[ ]` to do / `[~]` in progress / `[x]` done / `[-]` abandoned. End with a short "How to use this backlog" section recalling the cycle: start a phase (pick coherent items, group them) → track progress (`[~]`) → archive on closure (`[x]` then a "Completed" section at the bottom of the file).

### The adoption question (retrofit only)

For a project tracked before this model existed and with no `BACKLOG.md` yet
referenced from `ROADMAP.md`, ask once, in plain terms: *"Add a `BACKLOG.md` —
a running list of every idea for this project, sorted by priority — and have
`ROADMAP.md` summarize from it? Or keep `ROADMAP.md` as a plain hand-kept
list?"* **(recommended: add it — it's the standard setup and costs nothing
while the list is short.)** Yes → `backlog_model: "adopté"`; no → `"non"`.
Never asked again.

## `ROADMAP.md` — derived synthesis

Never lists the raw detail (effort/value, technical notes) — a pointer to `BACKLOG.md` for that. Structure:
1. **Done** — past phases, one line each, a pointer to `STATUS.md`/`CHANGELOG.md` for the detail.
2. **Phase N — 🎯 in progress** — the phase active right now (see "How phases work" below), with the detail of its content.
3. **After Phase N** — following phases already anticipated, grouped by priority.
4. **Unprioritised ideas** — a very short summary (a few words per theme, not the full list — that one lives in `BACKLOG.md`).

If a project doesn't have enough content yet to justify several phases: `ROADMAP.md` can stay a simple prioritised list without the "Phase N" structure as long as no phase has started — the full structure is put in place when the first phase begins.

## How phases work

When enough coherent backlog items accumulate (Claude's judgment — no fixed numeric threshold, consistent with "never guess": it's a proposal, never an automatic decision), propose starting a phase, in plain terms: *"You've got a batch of related backlog items — I can group them into a **phase**: a focused piece of work with its own short spec, so it's planned before we build it. Start one now?"* *(recommend yes only if the items are genuinely coherent)*. If accepted:

1. Determine `phase_model` if not yet done for this project (`STATUS.md` frontmatter, absent = never set):
   - `claude plugin list` → if `superpowers` is present and enabled: `phase_model: "superpowers"`, no question.
   - Otherwise (absent, or present but disabled): ask — *"Phase plans come out better with the `superpowers` plugin (it writes a structured spec then an implementation plan). Install it (needs a session restart after), or use a lighter built-in format?"* **(recommended: install it — I can do it for you)**. On yes: run the install yourself (`claude plugin marketplace list` → `claude plugin marketplace add anthropics/claude-plugins-official` if needed → `claude plugin install superpowers@claude-plugins-official` → `claude plugin enable superpowers`), warn a restart is required, then `phase_model: "superpowers"`. On no: `phase_model: "leger"` (a simple `PHASE_N_SPEC.md`, no extra plugin).
   - Once determined, never asked again for this project — even if `superpowers` becomes available later on the machine (consistency across all phases of a single project). Changing the format stays possible on the user's explicit request, but is never re-proposed automatically.
2. Produce the phase document according to `phase_model`:
   - `"superpowers"`: invoke the `writing-plans` skill to produce a plan in `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`, in the tracked project's repo (not `project-tracker`'s).
   - `"leger"`: write `docs/project-tracker/phases/PHASE_N_SPEC.md` yourself (goal, scope, rules to follow) — no SDD ceremony, direct implementation.
3. `ROADMAP.md` gains/updates its "Phase N — 🎯 in progress" section referencing that document.
4. The items concerned move to `[~]` in `BACKLOG.md`.

On closing a phase: finished items → `[x]` then archived in the "Completed" section of `BACKLOG.md`; the "Phase N — in progress" section of `ROADMAP.md` moves into "Done".
