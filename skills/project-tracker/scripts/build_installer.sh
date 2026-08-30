#!/usr/bin/env bash
# Regenerates install-project-tracker.sh from the skill's current files
# (SKILL.md, references/, hooks/, scripts/), base64-encoded (no risk of a
# heredoc delimiter collision or a mis-escaped special character). Re-run
# after any change to the skill, then commit the result to keep the
# installer up to date.
#
# Usage: bash build_installer.sh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$(cd "$SKILL_DIR/../.." && pwd)/install-project-tracker.sh"

encode() { base64 < "$1" | tr -d '\n'; }

cat > "$OUT" <<'HEADER'
#!/usr/bin/env bash
# Standalone installer for the project-tracker skill.
# Auto-generated -- do not edit by hand, regenerate from the source
# machine if the skill has changed.
#
# Usage: bash install-project-tracker.sh
set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/project-tracker"
SCOPES_DIR="$HOME/.claude/project-tracker"
SETTINGS_FILE="$HOME/.claude/settings.json"
SKILLS_ROOT="$HOME/.claude/skills"
SKILLS_EXISTED_BEFORE=0
[ -d "$SKILLS_ROOT" ] && SKILLS_EXISTED_BEFORE=1

echo "Installing project-tracker into $SKILL_DIR ..."
mkdir -p "$SKILL_DIR/hooks" "$SKILL_DIR/scripts" "$SKILL_DIR/references" "$SCOPES_DIR"

write_b64() {
  # write_b64 <output_path>  (reads base64 on stdin)
  base64 -d > "$1"
}
HEADER

for f in SKILL.md references/reminders-sync.md references/backlog-phases.md hooks/session_start.sh hooks/test_session_start.sh hooks/reminders_sync_trigger.sh hooks/test_reminders_sync_trigger.sh hooks/portfolio_regen.sh hooks/test_portfolio_regen.sh scripts/generate_portfolio.py scripts/test_generate_portfolio.py; do
  varname=$(echo "$f" | tr '/.' '__')
  {
    echo "cat <<'B64_$varname' | write_b64 \"\$SKILL_DIR/$f\""
    encode "$SKILL_DIR/$f"
    echo ""
    echo "B64_$varname"
  } >> "$OUT"
done

cat >> "$OUT" <<'FOOTER'
chmod +x "$SKILL_DIR/hooks/session_start.sh" "$SKILL_DIR/hooks/test_session_start.sh" "$SKILL_DIR/hooks/reminders_sync_trigger.sh" "$SKILL_DIR/hooks/test_reminders_sync_trigger.sh" "$SKILL_DIR/hooks/portfolio_regen.sh" "$SKILL_DIR/hooks/test_portfolio_regen.sh" "$SKILL_DIR/scripts/generate_portfolio.py"

if [ -f "$SCOPES_DIR/scopes.txt" ]; then
  echo "scopes.txt already exists -> unchanged ($SCOPES_DIR/scopes.txt)"
elif [ -t 0 ]; then
  echo
  read -rp "Absolute path of the folder to watch automatically (e.g. /Users/you/Documents/Code): " scope_path
  {
    echo "# project-tracker scopes — one absolute path per line, comments with #"
    echo "# Everything under these roots gets automatic detection."
    [ -n "$scope_path" ] && echo "$scope_path"
  } > "$SCOPES_DIR/scopes.txt"
  echo "scopes.txt created: $SCOPES_DIR/scopes.txt"
else
  {
    echo "# project-tracker scopes — one absolute path per line, comments with #"
    echo "# Add a root to watch, e.g. /Users/you/Documents/Code"
  } > "$SCOPES_DIR/scopes.txt"
  echo ">> No interactive terminal: edit $SCOPES_DIR/scopes.txt to add your folders."
fi

if [ ! -f "$SCOPES_DIR/trackignore.txt" ]; then
  {
    echo "# project-tracker — absolute paths to exclude from detection, one per line."
    echo "# An entry equal to a scopes.txt root ignores only that exact folder."
  } > "$SCOPES_DIR/trackignore.txt"
  echo "trackignore.txt created: $SCOPES_DIR/trackignore.txt"
fi

python3 - "$SETTINGS_FILE" "$SKILL_DIR/hooks/session_start.sh" "$SKILL_DIR/hooks/reminders_sync_trigger.sh" "$SKILL_DIR/hooks/portfolio_regen.sh" <<'PYEOF'
import json, sys, os

settings_path, session_start_cmd, post_tool_use_cmd, portfolio_cmd = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

settings.setdefault("hooks", {})

def register(event, matcher, command):
    settings["hooks"].setdefault(event, [])
    already = any(
        h.get("command") == command
        for group in settings["hooks"][event]
        for h in group.get("hooks", [])
    )
    if not already:
        settings["hooks"][event].append(
            {"matcher": matcher, "hooks": [{"type": "command", "command": command}]}
        )
        print(f"hook {event} registered in {settings_path}")
        return True
    print(f"hook {event} already present in {settings_path} -> unchanged")
    return False

changed = register("SessionStart", "", session_start_cmd)
changed = register("PostToolUse", "Edit|Write", post_tool_use_cmd) or changed
changed = register("PostToolUse", "Edit|Write", portfolio_cmd) or changed

if changed:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
PYEOF

echo
echo "Verification (tests):"
bash "$SKILL_DIR/hooks/test_session_start.sh"
bash "$SKILL_DIR/hooks/test_reminders_sync_trigger.sh"
bash "$SKILL_DIR/hooks/test_portfolio_regen.sh"
( cd "$SKILL_DIR/scripts" && python3 -m unittest test_generate_portfolio -v )

echo
echo "=========================================="
echo "Installation complete: $SKILL_DIR"
if [ "$SKILLS_EXISTED_BEFORE" -eq 0 ]; then
  echo "IMPORTANT: ~/.claude/skills/ did not exist before -- restart Claude Code"
  echo "once so it detects the new skills folder."
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "Note: the 'gh' CLI is not installed -- only needed if you want"
  echo "automatic GitHub repo creation from this skill."
fi
echo "Open a Claude Code session in a scopes.txt folder to check the hook."
echo "=========================================="
FOOTER

chmod +x "$OUT"
echo "Installer generated: $OUT ($(wc -l < "$OUT") lines, $(du -h "$OUT" | cut -f1))"
