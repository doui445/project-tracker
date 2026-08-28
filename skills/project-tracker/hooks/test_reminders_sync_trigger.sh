#!/usr/bin/env bash
# Test manuel de reminders_sync_trigger.sh — aucune dépendance à un
# framework de test. Lancer avec: bash test_reminders_sync_trigger.sh
set -uo pipefail

HOOK="$(dirname "$0")/reminders_sync_trigger.sh"
FAIL=0

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if [[ "$haystack" == *"$needle"* ]]; then
    echo "PASS: $label"
  else
    echo "FAIL: $label — attendu de trouver: $needle"
    FAIL=1
  fi
}

assert_empty() {
  local value="$1" label="$2"
  if [ -z "$value" ]; then
    echo "PASS: $label"
  else
    echo "FAIL: $label — attendu vide, obtenu: $value"
    FAIL=1
  fi
}

run_hook() {
  local tool_name="$1" file_path="$2" session_id="$3"
  printf '{"session_id": "%s", "cwd": "%s", "hook_event_name": "PostToolUse", "tool_name": "%s", "tool_input": {"file_path": "%s"}, "tool_response": {"success": true}}' \
    "$session_id" "$(dirname "$file_path")" "$tool_name" "$file_path" \
    | HOME="$TMP_HOME" TMPDIR="$TMP_MARKERS" bash "$HOOK"
}

TMP_HOME="$(mktemp -d)"
TMP_MARKERS="$(mktemp -d)"
trap 'rm -rf "$TMP_HOME" "$TMP_MARKERS"' EXIT

mkdir -p "$TMP_HOME/.claude/project-tracker"
SCOPE_ROOT="$TMP_HOME/scope"
mkdir -p "$SCOPE_ROOT"
echo "$SCOPE_ROOT" > "$TMP_HOME/.claude/project-tracker/scopes.txt"

TRACKED="$SCOPE_ROOT/tracked-project"
mkdir -p "$TRACKED/docs/project-tracker"
cat > "$TRACKED/docs/project-tracker/STATUS.md" <<'EOF'
---
project: Tracked
status: active
last_updated: 2026-01-01
reminders_list: "Tracked List"
---
Contenu.
EOF

# Cas 1: Edit sur docs/project-tracker/STATUS.md, projet suivi + lié -> additionalContext injecté
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-1")"
assert_contains "$OUT" "additionalContext" "STATUS.md edit, lie -> additionalContext"
assert_contains "$OUT" "tracked-project" "additionalContext contient le nom du projet"

# Cas 2: Write sur docs/project-tracker/ROADMAP.md, même projet, nouvelle session -> pareil
OUT="$(run_hook "Write" "$TRACKED/docs/project-tracker/ROADMAP.md" "session-2")"
assert_contains "$OUT" "additionalContext" "ROADMAP.md write, lie -> additionalContext"

# Cas 3: outil autre que Edit/Write -> silence
OUT="$(run_hook "Bash" "$TRACKED/docs/project-tracker/STATUS.md" "session-3")"
assert_empty "$OUT" "tool_name=Bash -> silence"

# Cas 4: fichier autre que STATUS.md/ROADMAP.md (README.md a la racine) -> silence
OUT="$(run_hook "Edit" "$TRACKED/README.md" "session-4")"
assert_empty "$OUT" "README.md -> silence"

# Cas 5: hors périmètre (pas dans scopes.txt) -> silence
OUTSIDE="$TMP_HOME/outside/docs/project-tracker/STATUS.md"
mkdir -p "$(dirname "$OUTSIDE")"
cat > "$OUTSIDE" <<'EOF'
---
project: Outside
status: active
last_updated: 2026-01-01
reminders_list: "Whatever"
---
EOF
OUT="$(run_hook "Edit" "$OUTSIDE" "session-5")"
assert_empty "$OUT" "hors perimetre -> silence"

# Cas 6: dans .trackignore -> silence
IGNORED="$SCOPE_ROOT/ignored-project"
mkdir -p "$IGNORED/docs/project-tracker"
cat > "$IGNORED/docs/project-tracker/STATUS.md" <<'EOF'
---
project: Ignored
status: active
last_updated: 2026-01-01
reminders_list: "Whatever"
---
EOF
IGNORE_FILE="$TMP_HOME/.claude/project-tracker/trackignore.txt"
echo "$IGNORED" > "$IGNORE_FILE"
OUT="$(run_hook "Edit" "$IGNORED/docs/project-tracker/STATUS.md" "session-6")"
assert_empty "$OUT" "trackignore.txt -> silence"

# Cas 7: reminders_list absent -> silence
NOLIST="$SCOPE_ROOT/no-list-project"
mkdir -p "$NOLIST/docs/project-tracker"
cat > "$NOLIST/docs/project-tracker/STATUS.md" <<'EOF'
---
project: NoList
status: active
last_updated: 2026-01-01
---
EOF
OUT="$(run_hook "Edit" "$NOLIST/docs/project-tracker/STATUS.md" "session-7")"
assert_empty "$OUT" "reminders_list absent -> silence"

# Cas 8: reminders_list == "non" -> silence
DECLINED="$SCOPE_ROOT/declined-project"
mkdir -p "$DECLINED/docs/project-tracker"
cat > "$DECLINED/docs/project-tracker/STATUS.md" <<'EOF'
---
project: Declined
status: active
last_updated: 2026-01-01
reminders_list: "non"
---
EOF
OUT="$(run_hook "Edit" "$DECLINED/docs/project-tracker/STATUS.md" "session-8")"
assert_empty "$OUT" 'reminders_list "non" -> silence'

# Cas 9: ROADMAP.md édité mais STATUS.md absent du même dossier -> silence
NOSTATUS="$SCOPE_ROOT/no-status-project"
mkdir -p "$NOSTATUS/docs/project-tracker"
OUT="$(run_hook "Edit" "$NOSTATUS/docs/project-tracker/ROADMAP.md" "session-9")"
assert_empty "$OUT" "STATUS.md absent -> silence"

# Cas 10: debounce -- même session, même projet, deux triggers -> le second est silencieux
OUT1="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-10")"
OUT2="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-10")"
assert_contains "$OUT1" "additionalContext" "debounce -> premier trigger produit du contexte"
assert_empty "$OUT2" "debounce -> deuxieme trigger (meme session) silencieux"

# Cas 11: debounce réarmé sur une session différente
OUT3="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-11")"
assert_contains "$OUT3" "additionalContext" "debounce -> nouvelle session reproduit le contexte"

# Cas 12 (regression): python3 manquant -> exit 0, sortie vide, pas de crash
run_hook_no_python() {
  local tool_name="$1" file_path="$2" session_id="$3"
  printf '{"session_id": "%s", "cwd": "%s", "hook_event_name": "PostToolUse", "tool_name": "%s", "tool_input": {"file_path": "%s"}}' \
    "$session_id" "$(dirname "$file_path")" "$tool_name" "$file_path" \
    | env -i PATH=/bin HOME="$TMP_HOME" TMPDIR="$TMP_MARKERS" bash "$HOOK"
}
OUT="$(run_hook_no_python "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-12" 2>&1)" || true
assert_empty "$OUT" "python3 manquant -> silence"

# Cas 13 (nouveau): STATUS.md directement sous docs/ (pas docs/project-tracker/)
# -> silence, le pattern exige le sous-dossier project-tracker/ exact.
WRONG_NESTING="$SCOPE_ROOT/wrong-nesting-project"
mkdir -p "$WRONG_NESTING/docs"
cat > "$WRONG_NESTING/docs/STATUS.md" <<'EOF'
---
project: WrongNesting
status: active
last_updated: 2026-01-01
reminders_list: "Whatever"
---
EOF
OUT="$(run_hook "Edit" "$WRONG_NESTING/docs/STATUS.md" "session-13")"
assert_empty "$OUT" "STATUS.md directement sous docs/ (pas project-tracker/) -> silence"

# Cas 14 (nouveau): trackignore.txt avec une entrée = racine de périmètre.
# La racine exacte est ignorée ; un projet à l'intérieur ne l'est pas.
SCOPE_STATUS="$SCOPE_ROOT/docs/project-tracker/STATUS.md"
mkdir -p "$(dirname "$SCOPE_STATUS")"
cat > "$SCOPE_STATUS" <<'EOF'
---
project: ScopeRoot
status: active
last_updated: 2026-01-01
reminders_list: "Whatever"
---
EOF
echo "$SCOPE_ROOT" >> "$IGNORE_FILE"
OUT="$(run_hook "Edit" "$SCOPE_STATUS" "session-14")"
assert_empty "$OUT" "entree = racine de perimetre -> racine exacte ignoree"
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-15")"
assert_contains "$OUT" "additionalContext" "entree = racine de perimetre -> projet a l'interieur toujours traite"

if [ "$FAIL" -eq 1 ]; then
  echo "Des tests ont echoue."
  exit 1
fi
echo "Tous les tests sont passes."
