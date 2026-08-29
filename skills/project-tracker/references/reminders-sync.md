# Reminders sync

Referenced from `SKILL.md` (`## Detecting a project's root`, `## Bootstrapping a new project` step 5, `## Continuous updates` step 5).

The `#tracker-sync` tag marks a reminder as currently tracked/absorbed by Claude in the tracking files — set both on a reminder the user writes and on a reminder Claude creates, once its scope has been discussed and reflected in `STATUS.md`/`ROADMAP.md`. A reminder without this tag is a raw capture not yet seen by Claude. This `#` is the Reminders app's native display — in the `tags`/`addTags`/`filterTags` parameters of the `reminders_tasks` tool, the tag is passed without the `#` (`"tracker-sync"`), like the thematic tags (`#ROI` → `"ROI"`, etc.).

The linking question is asked at bootstrap (step 5) or, for an already-tracked project that has never had it, as soon as the "Tracked" state is detected (see `## Detecting a project's root` in `SKILL.md`) — never here, and never while waiting for a "Continuous updates" trigger.

If `reminders_list` is absent (question never asked — should normally no longer happen once the detection above has run, but a safety net if this section is reached before) or is `"non"` (declined): skip this section entirely, behaviour unchanged.

Otherwise, on every trigger (`PostToolUse` hook, backfill at linking, or an explicit request from the user):

0. Check that `reminders_list` resolves to an existing list (`reminders_lists` action `read`). Two possible failures to tell apart, neither of which must fail the rest of the continuous update:
   - **`apple-reminders` MCP tool unavailable** (the skill is portable across machines, cf. `install-project-tracker.sh` — the MCP server isn't necessarily installed everywhere): offer to install it yourself right now (`claude mcp add apple-reminders -s user -- npx -y mcp-server-apple-events` — `user` scope mandatory, not the command's default `local` scope, otherwise the server stays invisible from sessions opened in a project other than the one where you install it). If the user accepts, run the command yourself rather than just pointing to it, then explain that they must restart their Claude Code session for the new tools to become visible. If the user declines, skip the rest of this section for this session without blocking the rest of the continuous update.
   - **List not found** (renamed or deleted on the app side): do not guess, ask the user explicitly — graft onto an existing list (offer the available ones), create a new list (updates `reminders_list`), or stop tracking reminders for this project (`reminders_list: "non"`). Until this is resolved, skip the rest of this section for this session.
1. Read all open reminders in the list (`reminders_tasks` action `read`, `filterList: <reminders_list>`).
2. **Reminders without the `#tracker-sync` tag** (the user's raw captures): announce how many were found and ask whether you handle them now or defer (they stay untagged, so they are re-proposed identically on the next pass — nothing is lost). If yes, tackle them one by one, but between each, ask again whether you continue with the next ones or stop there for this pass — a green light at the start is never agreement to process the whole batch at once. For each reminder you handle, discuss to pin down the exact scope. Once clarified:
   - Optionally rewrite the reminder's title/notes (`reminders_tasks` action `update`) to make it clearer and more detailed — the discussion itself counts as confirmation, no separate approval for the rewrite.
   - Set the priority according to the mapping below.
   - Write the item into `STATUS.md` ("Next actions") or `ROADMAP.md` (content of the current phase), depending on what was decided together — never `BACKLOG.md` (see "Scope decision" below: the raw backlog is never synced, in either direction).
   - Set the `#tracker-sync` tag, plus a thematic tag chosen in discussion if relevant (e.g. `#ROI`, `#NUC` — see "List sections" below), via `addTags` (never `tags`, which would entirely replace the tags the user already set on this reminder — `addTags` merges without touching them).
3. **Reminders tagged `#tracker-sync` and still open**: compare by judgment (never an exact text match — recognize a reworded task) with the current state of `STATUS.md`/`ROADMAP.md`/the conversation/`git log`. If you think a task is finished, propose it explicitly. If confirmed: tick the reminder (`reminders_tasks` action `update`, `completed: true`) **and** update `STATUS.md`/`JOURNAL.md` in the same confirmation — a single round trip covers both writes.
4. **Full coverage**: diff between all the goals in `STATUS.md` ("Next actions") + `ROADMAP.md` (content of the current phase) and the existing open reminders, by the same judgment-based matching as step 3 (never an exact text match). Any goal with no matching reminder is proposed for creation (`reminders_tasks` action `create`, `targetList: <reminders_list>`, tags via `tags: ["tracker-sync", ...]` — here a real `create`, nothing to preserve), priority according to the source section (see mapping below). If several items are involved in one pass, show the list and ask for confirmation before creating them in a batch; for a single item added over the course of the session, the normal `STATUS.md` update confirmation is enough, no separate approval. This diff is no longer limited to items added during the current session — see "Trigger" below.

If a call to one of these tools fails partway through, at any step (e.g. the macOS Reminders/Calendar permission revoked after the first grant): flag it clearly to the user and stop the rest of this section for this session — never fail the rest of the continuous update (`STATUS.md`, `JOURNAL.md`, etc.) because of it.

## Scope decision: Reminders ↔ Backlog

`BACKLOG.md` is **never** synced to Reminders — neither by the hook (see "Trigger"), nor by step 4 above. Only `STATUS.md` (the "Next actions" section) and `ROADMAP.md` (content of the current phase) feed Reminders. Reason: `BACKLOG.md` is a raw, deliberately unsorted reservoir (see `references/backlog-phases.md`) — a grooming tool, not a list of commitments. Syncing the whole backlog would drown the real next actions in noise. A backlog item only enters the world of reminders when it is promoted into a concrete phase of `ROADMAP.md`.

## Trigger

A `PostToolUse` hook (`hooks/reminders_sync_trigger.sh`, see its documentation in the script itself) fires automatically on the first change to `STATUS.md`/`ROADMAP.md` of each session, for a tracked and linked project (one reminder per session and per project — debounced via a marker keyed on session_id+project, consistent with "a single verification reminder per session") — it is what guarantees that step 4 above runs without depending on your own judgment of what counts as a "significant change" (the old gating, which had already caused a real bug where a retrofit never fired). The hook only injects a textual reminder; all the logic (steps 0-4 above) stays your judgment, never mechanised on the hook side.

**Backfill at linking**: right after a successful list link (bootstrap step 5, or retrofit of an already-tracked project), immediately run step 4 above once — covers the goals already present in `STATUS.md`/`ROADMAP.md` at the moment of linking, not only future additions.

## Reminders priority → file section mapping

| Reminders priority | Meaning | File section |
|---|---|---|
| Low (`priority: 9`) | Normal next task | `STATUS.md` → "Next actions" |
| Medium (`priority: 5`) | Important task | `STATUS.md` → "Next actions" |
| High (`priority: 1`) | Important AND top-priority task | `STATUS.md` → "Next actions" |

The `reminders_tasks` tool's numeric encoding is counter-intuitive (inverted relative to the natural order) — verified against the MCP server's actual schema during implementation. Always use the numeric value above, never guess an order like "higher number = higher priority".

Low/Medium/High all live in "Next actions"; the level expresses the relative weight within that active set. The priority is never fixed: Claude can raise or lower it at any time if the discussion changes the assessment of a task (e.g. a Low task becomes High if it blocks something else).

## List sections (known limitation)

The Reminders app (Tahoe) lets you group a list's reminders under thematic headers (e.g. "ROI", "NUC", "Image" in a project list) — a purely UI feature, invisible and undrivable via the MCP tool (same limitation as the Projects/Domains folders). Reminders you create or modify therefore always land outside any section — the user files them into the app themselves if they want. Workaround: set a thematic tag (step 2 above) alongside `#tracker-sync` to approximate a filterable classification.

## Subtasks

Goal: keep the list readable (few top-level items) while capturing the detail of composite tasks.

- **Composite task** (several concrete steps identified in discussion) → a single top-level reminder for the overall action, with each step as a subtask — rather than several separate top-level reminders that dilute the priority and clutter the list.
  - **New reminder** (e.g. step 4, creation from a file item) and all the steps already known at creation time: a single call, `reminders_tasks` action `create` with `subtasks: ["step 1", "step 2", ...]` — creates the reminder and its subtasks in one go rather than `create` + N separate `reminders_subtasks` action `create` calls.
  - **Reminder that already exists** (e.g. a user capture reworked at step 2, or a step discovered afterwards): inline `subtasks` only works at creation, so add each step via `reminders_subtasks` action `create`.
- **Atomic task** → a simple reminder, no subtasks.
- Ticking a subtask (`reminders_subtasks` action `toggle`) follows the same rule as ticking the parent reminder: never silent, always proposed and confirmed before writing.
- When all of a reminder's subtasks are ticked, flag it and propose ticking the parent reminder — hooks into step 3 above.
- Optional, at your discretion: reflect subtask progress in `STATUS.md` (e.g. "2/3 steps done") during a normal rewrite of the file — pure state reading, does not trigger a separate confirmation.

## Safeguard: reminder ticked outside the flow

If a reminder is ticked directly in the app (rather than via step 3 above), nothing propagates it automatically into `STATUS.md`/`JOURNAL.md` — a safety net covers this case to avoid a silent inconsistency between the file and the app.

For each "Next actions" item already linked to a reminder (so normally tagged `#tracker-sync`): check with a targeted search (`reminders_tasks` action `read`, `search: <keywords from the title>`, `filterList: <reminders_list>`, `showCompleted: true`) whether the corresponding reminder is ticked. Never read the entire history of completed reminders in bulk — it would grow without end over the project's lifetime; the targeted search stays bounded by the size of "Next actions" (always small), not by the accumulated history.

The search may return zero, one or several results — use your judgment to identify which one really corresponds to the item (same logic as step 3, no exact text match). If no clear result stands out (zero matches, or several candidates with no reliable way to decide): do not invent a match, leave that item aside for this pass rather than risk a false positive.

If a corresponding reminder is identified with confidence and it is ticked: this is an inconsistency — flag it explicitly to the user and propose updating `STATUS.md`/`JOURNAL.md` accordingly, with the same confirmation as step 3.
