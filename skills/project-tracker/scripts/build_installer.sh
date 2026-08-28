#!/usr/bin/env bash
# Regenere install-project-tracker.sh a partir des fichiers actuels du
# skill (SKILL.md, references/, hooks/, scripts/), encodes en base64
# (aucun risque de collision de delimiteur heredoc ni de caractere
# special mal echappe). A relancer apres toute modification du skill,
# puis committer le resultat pour garder l'installeur a jour.
#
# Usage : bash build_installer.sh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$(cd "$SKILL_DIR/../.." && pwd)/install-project-tracker.sh"

encode() { base64 < "$1" | tr -d '\n'; }

cat > "$OUT" <<'HEADER'
#!/usr/bin/env bash
# Installeur autonome du skill project-tracker.
# Genere automatiquement -- ne pas editer a la main, regenerer depuis la
# machine source si le skill a change.
#
# Usage : bash install-project-tracker.sh
set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/project-tracker"
SCOPES_DIR="$HOME/.claude/project-tracker"
SETTINGS_FILE="$HOME/.claude/settings.json"
SKILLS_ROOT="$HOME/.claude/skills"
SKILLS_EXISTED_BEFORE=0
[ -d "$SKILLS_ROOT" ] && SKILLS_EXISTED_BEFORE=1

echo "Installation de project-tracker dans $SKILL_DIR ..."
mkdir -p "$SKILL_DIR/hooks" "$SKILL_DIR/scripts" "$SKILL_DIR/references" "$SCOPES_DIR"

write_b64() {
  # write_b64 <chemin_de_sortie>  (lit le base64 sur stdin)
  base64 -d > "$1"
}
HEADER

for f in SKILL.md references/reminders-sync.md references/backlog-phases.md hooks/session_start.sh hooks/test_session_start.sh hooks/reminders_sync_trigger.sh hooks/test_reminders_sync_trigger.sh scripts/generate_portfolio.py scripts/test_generate_portfolio.py; do
  varname=$(echo "$f" | tr '/.' '__')
  {
    echo "cat <<'B64_$varname' | write_b64 \"\$SKILL_DIR/$f\""
    encode "$SKILL_DIR/$f"
    echo ""
    echo "B64_$varname"
  } >> "$OUT"
done

cat >> "$OUT" <<'FOOTER'
chmod +x "$SKILL_DIR/hooks/session_start.sh" "$SKILL_DIR/hooks/test_session_start.sh" "$SKILL_DIR/hooks/reminders_sync_trigger.sh" "$SKILL_DIR/hooks/test_reminders_sync_trigger.sh" "$SKILL_DIR/scripts/generate_portfolio.py"

if [ -f "$SCOPES_DIR/scopes.txt" ]; then
  echo "scopes.txt existe deja -> non modifie ($SCOPES_DIR/scopes.txt)"
elif [ -t 0 ]; then
  echo
  read -rp "Chemin absolu du dossier a surveiller automatiquement (ex: /Users/toi/Documents/Code) : " scope_path
  {
    echo "# project-tracker scopes — un chemin absolu par ligne, commentaires avec #"
    echo "# Tout ce qui est sous ces racines beneficie de la detection automatique."
    [ -n "$scope_path" ] && echo "$scope_path"
  } > "$SCOPES_DIR/scopes.txt"
  echo "scopes.txt cree : $SCOPES_DIR/scopes.txt"
else
  {
    echo "# project-tracker scopes — un chemin absolu par ligne, commentaires avec #"
    echo "# Ajoute une racine a surveiller, ex: /Users/toi/Documents/Code"
  } > "$SCOPES_DIR/scopes.txt"
  echo ">> Aucun terminal interactif : edite $SCOPES_DIR/scopes.txt pour ajouter tes dossiers."
fi

if [ ! -f "$SCOPES_DIR/trackignore.txt" ]; then
  {
    echo "# project-tracker — chemins absolus a exclure de la detection, un par ligne."
    echo "# Une entree egale a une racine de scopes.txt n'ignore que ce dossier exact."
  } > "$SCOPES_DIR/trackignore.txt"
  echo "trackignore.txt cree : $SCOPES_DIR/trackignore.txt"
fi

python3 - "$SETTINGS_FILE" "$SKILL_DIR/hooks/session_start.sh" "$SKILL_DIR/hooks/reminders_sync_trigger.sh" <<'PYEOF'
import json, sys, os

settings_path, session_start_cmd, post_tool_use_cmd = sys.argv[1], sys.argv[2], sys.argv[3]
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
        print(f"hook {event} enregistre dans {settings_path}")
        return True
    print(f"hook {event} deja present dans {settings_path} -> non modifie")
    return False

changed = register("SessionStart", "", session_start_cmd)
changed = register("PostToolUse", "Edit|Write", post_tool_use_cmd) or changed

if changed:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
PYEOF

echo
echo "Verification (tests) :"
bash "$SKILL_DIR/hooks/test_session_start.sh"
bash "$SKILL_DIR/hooks/test_reminders_sync_trigger.sh"
( cd "$SKILL_DIR/scripts" && python3 -m unittest test_generate_portfolio -v )

echo
echo "=========================================="
echo "Installation terminee : $SKILL_DIR"
if [ "$SKILLS_EXISTED_BEFORE" -eq 0 ]; then
  echo "IMPORTANT : ~/.claude/skills/ n'existait pas avant -- redemarre Claude Code"
  echo "une fois pour qu'il detecte le nouveau dossier de skills."
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "Note : la CLI 'gh' n'est pas installee -- necessaire seulement si tu veux"
  echo "la creation automatique de depots GitHub depuis ce skill."
fi
echo "Ouvre une session Claude Code dans un dossier de scopes.txt pour verifier le hook."
echo "=========================================="
FOOTER

chmod +x "$OUT"
echo "Installeur genere : $OUT ($(wc -l < "$OUT") lignes, $(du -h "$OUT" | cut -f1))"
