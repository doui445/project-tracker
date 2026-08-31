---
description: View and change project-tracker configuration (scopes, ignored paths, portfolio location/title, a project's category).
---

Show the user the current project-tracker configuration, then help them change it in plain language.

1. Read and display:
   - `~/.claude/project-tracker/scopes.txt` — the tracked roots (one absolute path per line)
   - `~/.claude/project-tracker/trackignore.txt` — excluded paths
   - `~/.claude/project-tracker/portfolio.txt` — the portfolio output folder, and its title if a `title:` line is present
   - If the current folder is a tracked project, that project's `category` from `docs/project-tracker/STATUS.md`
   - `~/.claude/project-tracker/language.txt` — the output language for the tracking files and portfolio; note the `language:` line of `portfolio.txt` (portfolio override) and, if the current folder is a tracked project, its `language:` frontmatter (project override)
2. Ask what they want to change. Handle:
   - **Add / remove a scope** → edit `scopes.txt`
   - **Ignore / un-ignore a path** → edit `trackignore.txt` (absolute path; an entry equal to a scope root ignores only that exact folder, not the projects inside it)
   - **Move the portfolio** → set the first line that is neither a `title:` nor a `language:` line of `portfolio.txt` to the new folder
   - **Rename the portfolio title** → set or replace the `title:` line in `portfolio.txt`
   - **Change a project's category** → edit the `category` frontmatter of that project's `STATUS.md`
   - **Change the language** — three levels:
     - *tracking files + portfolio (global)* → write the code (`en` / `fr`) as the first non-comment line of `language.txt`
     - *portfolio only* → set/replace the `language:` line of `portfolio.txt`
     - *this project only* → set/replace/remove the `language:` frontmatter key of this project's `STATUS.md`
     After a change: if it alters the **effective language of a project that already has content**, run the retranslation flow (`skills/track/references/writing-tracking-files.md`, `## Retranslating on a language change`). If it alters the portfolio language, offer to regenerate the portfolio (same as a title/folder change). If the global changes, note that other tracked projects inheriting it will be retranslated the next time a session opens on them.
3. After changing `portfolio.txt` (folder or title): the regeneration hook only fires on `STATUS.md` writes, so the change will not show until the next such write. Offer to regenerate now by running `${CLAUDE_PLUGIN_ROOT}/skills/track/scripts/generate_portfolio.py` once — ask before running it.
4. Never guess a value — ask.
