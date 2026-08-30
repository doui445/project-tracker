# ERRORS — project-tracker

Bug → cause → fix, searchable. Append-only. One entry per significant resolved
bug.

## 2026-08-30 — Installer shipped an incomplete skill after adding a reference file

**Symptom.** Added `references/writing-tracking-files.md`, ran
`scripts/build_installer.sh`, and the regenerated `install-project-tracker.sh`
did not contain the new file (`grep -c writing-tracking-files
install-project-tracker.sh` → `0`). A script-path install would have gotten a
skill whose `SKILL.md` points to a reference file that isn't there.

**Root cause.** `build_installer.sh` embedded a **hardcoded list** of files to
bundle (`for f in SKILL.md references/reminders-sync.md
references/backlog-phases.md hooks/... scripts/...`). Any new `references/*.md`
was silently left out until someone remembered to edit that list.

**Fix.** Build the file list by globbing `"$SKILL_DIR"/references/*.md` instead
of naming each one; hooks and scripts stay explicit (they need per-file
`chmod`). Commit `5add2b8`.

**Recognise it again.** Any "add a file to the skill, it works from the plugin
but not from the install script" report. The plugin path bundles the whole
repo via `hooks.json` + the marketplace source; the script path only bundles
what `build_installer.sh` enumerates. Keep the two in sync — prefer globs over
lists in that script.
