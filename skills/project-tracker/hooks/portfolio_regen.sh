#!/usr/bin/env bash
# project-tracker PostToolUse hook — portfolio_regen.sh
#
# Fires on Edit/Write touching a tracked project's STATUS.md: regenerates
# the unified PORTFOLIO.html by shelling out to generate_portfolio.py
# (config-driven, no arguments). Purely deterministic -- the only context
# it injects is a one-per-session note when the output location is not
# configured yet (a hook cannot prompt the user; the skill does).
# JSON parsing via python3, never jq. Bash 3.2 compatible (macOS default).
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
  */docs/project-tracker/STATUS.md) ;;
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

PORTFOLIO_FILE="$HOME/.claude/project-tracker/portfolio.txt"

if [ ! -f "$PORTFOLIO_FILE" ]; then
  # Never configured: a hook cannot prompt -- ask Claude to, once per session.
  MARKER_DIR="${TMPDIR:-/tmp}/project-tracker-portfolio-regen"
  mkdir -p "$MARKER_DIR" 2>/dev/null || exit 0
  MARKER="$MARKER_DIR/${SESSION_ID}"
  [ -f "$MARKER" ] && exit 0
  touch "$MARKER" 2>/dev/null || true
  python3 -c '
import json
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "project-tracker: portfolio output location not configured - invoke the project-tracker skill and propose an output folder to the user (see SKILL.md ## Portfolio)."}}))
'
  exit 0
fi

# File exists: a comment-only file means "configured to off" -> stay silent.
HAS_TARGET=0
while IFS= read -r line || [ -n "$line" ]; do
  line="${line#"${line%%[![:space:]]*}"}"
  case "$line" in
    ""|"#"*) continue ;;
  esac
  HAS_TARGET=1
  break
done < "$PORTFOLIO_FILE"
[ "$HAS_TARGET" -eq 1 ] || exit 0

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEN="$SKILL_DIR/scripts/generate_portfolio.py"
[ -f "$GEN" ] || exit 0
python3 "$GEN" >/dev/null 2>&1 || true
exit 0
