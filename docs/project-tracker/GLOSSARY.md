# GLOSSARY — project-tracker

Domain terms used across the skill, its references and these tracking files.

| Term | Meaning |
|---|---|
| **scope / scope root** | An absolute path in `~/.claude/project-tracker/scopes.txt`. Everything under it gets `SessionStart` auto-detection. |
| **trackignore** | `~/.claude/project-tracker/trackignore.txt` — absolute paths where the skill stays silent. An entry equal to a scope root ignores only that exact folder, not the projects inside it. |
| **tracked / new / excluded** | The three detection states of a project root: has `docs/project-tracker/STATUS.md` / has neither / listed in `trackignore.txt`. |
| **bootstrap** | The first-time setup flow: a sequence of questions, then creation of the nine standard files from the answers — never guessed. |
| **retrofit** | Adopting the model for a project that already has non-standard tracking files; reuse what exists instead of asking from scratch. |
| **the nine standard files** | `README.md`, `CLAUDE.md` (root) + `ROADMAP`, `STATUS`, `JOURNAL`, `CHANGELOG`, `DECISIONS`, `ERRORS`, `BACKLOG` (in `docs/project-tracker/`). |
| **snapshot** | What `STATUS.md` is — the current state, fully rewritten each time, never accumulated. |
| **reservoir** | What `BACKLOG.md` is — every idea ever envisaged, archived on closure, never purged. |
| **frontmatter** | The YAML block at the top of `STATUS.md` — the only strictly structured part; what `generate_portfolio.py` consumes. |
| **`backlog_model`** | Frontmatter key. `"adopté"` = the backlog/roadmap/phases model is in use (automatic at bootstrap). `"non"` only via a declined retrofit. Absent = a project tracked before the feature, not yet retrofitted. |
| **`phase_model`** | Frontmatter key. `"superpowers"` (plan via the `writing-plans` skill in `docs/superpowers/plans/`) or `"leger"` (a `docs/project-tracker/phases/PHASE_N_SPEC.md` written directly). Absent until a phase is actually proposed. |
| **phase** | A coherent batch of backlog items grouped and worked as a unit. Proposed by Claude's judgment, never automatic. |
| **`#tracker-sync`** | The tag put on Reminders items the skill creates, so the sync can tell its own items apart. |
| **portfolio** | The single unified `PORTFOLIO.html` aggregating every tracked project across all scopes, written to the folder in `portfolio.txt`. |
| **chantier (C1–C4)** | The four build workstreams: C1 standalone repo, C2 English translation, C3 portfolio rework, C4 plugin wiring. |
| **the three modes** | How the skill can be installed: plugin (marketplace), skills-dir (install script), or `claude --plugin-dir` (one-shot). Hook scripts are self-relative to work in all three. |
