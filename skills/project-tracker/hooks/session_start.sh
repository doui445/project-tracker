#!/usr/bin/env bash
# project-tracker SessionStart hook.
# Purement déterministe : lit scopes.txt, décide si cwd est dans le
# périmètre, retrouve le projet suivi le plus proche (STATUS.md) ou
# signale un nouveau dossier, et imprime du texte brut que Claude Code
# injecte dans le contexte. Toute la logique métier vit dans le skill
# project-tracker, pas ici. Compatible bash 3.2 (macOS par défaut).
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
  echo "[project-tracker] Session ouverte dans un projet suivi ($ROOT)."
  echo "Invoque le skill project-tracker : compare last_updated (frontmatter ci-dessous) a la derniere activite reelle (dernier commit git si uses_git=true, sinon date de modification des fichiers) et propose une mise a jour si necessaire. Ne rien ecrire sans verifier l'etat actuel des fichiers d'abord."
  echo "--- frontmatter de STATUS.md ---"
  awk '/^---$/{count++} {print} count==2{exit}' "$STATUS_FILE" 2>/dev/null | head -c 4000 || true
  echo
  exit 0
fi

echo "[project-tracker] Aucun suivi detecte dans ce dossier ($CWD), perimetre $SCOPE_ROOT."
echo "Invoque le skill project-tracker et lance le bootstrap : demande d'abord si ce dossier doit etre suivi (sinon ajouter son chemin absolu a $IGNORE_FILE), puis pose les questions du bootstrap avant de creer les fichiers standard."
exit 0
