#!/usr/bin/env bash
# project-tracker PostToolUse hook — reminders_sync_trigger.sh
#
# Fires on Edit/Write touching STATUS.md or ROADMAP.md of a tracked
# project linked to a Reminders list: injects into Claude's context a
# reminder to check the Reminders sync (full diff, see
# references/reminders-sync.md) before the end of the turn. Purely
# deterministic -- all the business logic lives in the skill, not here.
# JSON parsing via python3, never jq (not guaranteed installed) -- same
# convention as hooks/session_start.sh. Bash 3.2 compatible (macOS
# default).
#
# PostToolUse contract (checked against the official Claude Code docs):
# raw stdout on exit 0 is NOT seen by Claude (unlike SessionStart) --
# you must print JSON with hookSpecificOutput.additionalContext to
# inject context. Total silence (no stdout) = silent pass, nothing
# shown, nothing blocked.
set -euo pipefail

INPUT="$(cat)"

PARSED="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(1)
tool_input = data.get("tool_input", {}) or {}
print(data.get("tool_name", ""))
print(tool_input.get("file_path", ""))
print(data.get("session_id", ""))
' 2>/dev/null)" || exit 0

TOOL_NAME="$(printf '%s\n' "$PARSED" | sed -n '1p')"
FILE_PATH="$(printf '%s\n' "$PARSED" | sed -n '2p')"
SESSION_ID="$(printf '%s\n' "$PARSED" | sed -n '3p')"

case "$TOOL_NAME" in
  Edit|Write) ;;
  *) exit 0 ;;
esac

[ -n "$FILE_PATH" ] || exit 0
[ -n "$SESSION_ID" ] || exit 0

case "$FILE_PATH" in
  */docs/project-tracker/STATUS.md|*/docs/project-tracker/ROADMAP.md) ;;
  *) exit 0 ;;
esac

PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$FILE_PATH")")")"

SCOPES_FILE="$HOME/.claude/project-tracker/scopes.txt"
[ -f "$SCOPES_FILE" ] || exit 0

SCOPE_ROOT=""
while IFS= read -r line || [ -n "$line" ]; do
  line="${line%/}"
  case "$line" in
    ""|"#"*) continue ;;
  esac
  case "$PROJECT_ROOT" in
    "$line"|"$line"/*) SCOPE_ROOT="$line"; break ;;
  esac
done < "$SCOPES_FILE"

[ -n "$SCOPE_ROOT" ] || exit 0

IGNORE_FILE="$HOME/.claude/project-tracker/trackignore.txt"
if [ -f "$IGNORE_FILE" ]; then
  while IFS= read -r entry || [ -n "$entry" ]; do
    entry="${entry%/}"
    case "$entry" in
      ""|"#"*) continue ;;
    esac
    entry_is_scope_root=0
    while IFS= read -r scope || [ -n "$scope" ]; do
      scope="${scope%/}"
      case "$scope" in
        ""|"#"*) continue ;;
      esac
      if [ "$scope" = "$entry" ]; then
        entry_is_scope_root=1
        break
      fi
    done < "$SCOPES_FILE"
    if [ "$entry_is_scope_root" -eq 1 ]; then
      [ "$PROJECT_ROOT" = "$entry" ] && exit 0
    else
      case "$PROJECT_ROOT" in
        "$entry"|"$entry"/*) exit 0 ;;
      esac
    fi
  done < "$IGNORE_FILE"
fi

STATUS_FILE="$PROJECT_ROOT/docs/project-tracker/STATUS.md"
[ -f "$STATUS_FILE" ] || exit 0

REMINDERS_LIST_LINE="$(awk '/^---$/{c++; next} c==1 && /^reminders_list:/{print; exit} c>=2{exit}' "$STATUS_FILE" 2>/dev/null)" || true
case "$REMINDERS_LIST_LINE" in
  "") exit 0 ;;
  *'"non"'*) exit 0 ;;
esac

MARKER_DIR="${TMPDIR:-/tmp}/project-tracker-reminders-sync"
mkdir -p "$MARKER_DIR" 2>/dev/null || exit 0
SAFE_ROOT="$(printf '%s' "$PROJECT_ROOT" | tr '/' '_')"
MARKER="$MARKER_DIR/${SESSION_ID}__${SAFE_ROOT}"
[ -f "$MARKER" ] && exit 0
touch "$MARKER" 2>/dev/null || true

PROJECT_NAME="$(basename "$PROJECT_ROOT")"
CTX_PROJECT_NAME="$PROJECT_NAME" python3 -c '
import json, os
name = os.environ.get("CTX_PROJECT_NAME", "")
home = os.environ.get("HOME", "")
ref_path = home + "/.claude/skills/project-tracker/references/reminders-sync.md"
msg = ("STATUS.md/ROADMAP.md for " + name +
       " was just modified - invoke the project-tracker skill "
       "(if not already done this session) then check the Reminders "
       "sync (full diff, see " + ref_path + ") before ending this "
       "turn.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
'
exit 0
