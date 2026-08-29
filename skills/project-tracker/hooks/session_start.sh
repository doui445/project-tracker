#!/usr/bin/env bash
# project-tracker SessionStart hook.
# Purely deterministic: reads scopes.txt, decides whether cwd is within
# a scope, finds the nearest tracked project (STATUS.md) or flags a new
# folder, and prints raw text that Claude Code injects into the context.
# All the business logic lives in the project-tracker skill, not here.
# Bash 3.2 compatible (macOS default).
set -euo pipefail

INPUT="$(cat)"
CWD="$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("cwd",""))' 2>/dev/null)" || exit 0
CWD="${CWD%/}"

SCOPES_FILE="$HOME/.claude/project-tracker/scopes.txt"
[ -n "$CWD" ] || exit 0
[ -f "$SCOPES_FILE" ] || exit 0

SCOPE_ROOT=""
while IFS= read -r line || [ -n "$line" ]; do
  line="${line%/}"
  case "$line" in
    ""|"#"*) continue ;;
  esac
  case "$CWD" in
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
      [ "$CWD" = "$entry" ] && exit 0
    else
      case "$CWD" in
        "$entry"|"$entry"/*) exit 0 ;;
      esac
    fi
  done < "$IGNORE_FILE"
fi

ROOT="$CWD"
STATUS_FILE=""
while :; do
  if [ -f "$ROOT/docs/project-tracker/STATUS.md" ]; then
    STATUS_FILE="$ROOT/docs/project-tracker/STATUS.md"
    break
  fi
  [ "$ROOT" = "$SCOPE_ROOT" ] && break
  ROOT="$(dirname "$ROOT")"
done

if [ -n "$STATUS_FILE" ]; then
  echo "[project-tracker] Session opened in a tracked project ($ROOT)."
  echo "Invoke the project-tracker skill: compare last_updated (frontmatter below) with the last real activity (latest git commit if uses_git=true, otherwise file modification dates) and propose an update if needed. Do not write anything without checking the current state of the files first."
  echo "--- STATUS.md frontmatter ---"
  awk '/^---$/{count++} {print} count==2{exit}' "$STATUS_FILE" 2>/dev/null | head -c 4000 || true
  echo
  exit 0
fi

echo "[project-tracker] No tracking detected in this folder ($CWD), scope $SCOPE_ROOT."
echo "Invoke the project-tracker skill and start the bootstrap: first ask whether this folder should be tracked (otherwise add its absolute path to $IGNORE_FILE), then ask the bootstrap questions before creating the standard files."
exit 0
