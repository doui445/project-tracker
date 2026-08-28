#!/usr/bin/env bash
# project-tracker PostToolUse hook — reminders_sync_trigger.sh
#
# Se declenche sur Edit/Write touchant STATUS.md ou ROADMAP.md d'un projet
# suivi et lie a une liste Reminders : injecte dans le contexte de Claude
# un rappel de verifier la sync Reminders (diff complet, voir
# references/reminders-sync.md) avant la fin du tour. Purement
# deterministe -- toute la logique metier vit dans le skill, pas ici.
# Parsing JSON via python3, jamais jq (pas garanti installe) -- meme
# convention que hooks/session_start.sh. Compatible bash 3.2 (macOS
# par defaut).
#
# Contrat PostToolUse (verifie contre la doc officielle Claude Code) :
# stdout brut sur exit 0 n'est PAS vu par Claude (contrairement a
# SessionStart) -- il faut imprimer du JSON avec
# hookSpecificOutput.additionalContext pour injecter du contexte.
# Silence total (aucun stdout) = passage silencieux, rien affiche,
# rien bloque.
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
msg = ("STATUS.md/ROADMAP.md de " + name +
       " vient d'\''etre modifie - invoque le skill project-tracker "
       "(si pas deja fait dans cette session) puis verifie la sync "
       "Reminders (diff complet, voir " + ref_path + ") avant de "
       "terminer ce tour.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
'
exit 0
