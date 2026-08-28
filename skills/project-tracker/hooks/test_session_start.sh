#!/usr/bin/env bash
# Test manuel de session_start.sh — aucune dépendance à un framework de test.
# Lancer avec: bash test_session_start.sh
set -uo pipefail

HOOK="$(dirname "$0")/session_start.sh"
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
  local cwd="$1"
  printf '{"cwd": "%s", "hook_event_name": "SessionStart", "source": "startup"}' "$cwd" | HOME="$TMP_HOME" bash "$HOOK"
}

TMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TMP_HOME"' EXIT

mkdir -p "$TMP_HOME/.claude/project-tracker"
SCOPE_ROOT="$TMP_HOME/scope"
mkdir -p "$SCOPE_ROOT"
echo "$SCOPE_ROOT" > "$TMP_HOME/.claude/project-tracker/scopes.txt"

# Cas 1: cwd hors de tout périmètre -> silence total
OUT="$(run_hook "/tmp/outside-scope-$$")"
assert_empty "$OUT" "hors perimetre -> silence"

# Cas 2: cwd dans le périmètre, projet suivi (docs/project-tracker/STATUS.md présent)
TRACKED="$SCOPE_ROOT/tracked-project"
mkdir -p "$TRACKED/docs/project-tracker"
cat > "$TRACKED/docs/project-tracker/STATUS.md" <<'EOF'
---
project: Tracked
status: active
last_updated: 2026-01-01
---
Contenu.
EOF
OUT="$(run_hook "$TRACKED")"
assert_contains "$OUT" "projet suivi" "projet suivi -> rappel de verification"
assert_contains "$OUT" "project: Tracked" "projet suivi -> contenu STATUS.md inclus"

# Cas 3: cwd dans un sous-dossier profond d'un projet déjà suivi
mkdir -p "$TRACKED/subdir/deep"
OUT="$(run_hook "$TRACKED/subdir/deep")"
assert_contains "$OUT" "projet suivi" "sous-dossier d'un projet suivi -> retrouve la racine"

# Cas 4: cwd dans le périmètre, non suivi, non ignoré -> rappel de bootstrap
NEW="$SCOPE_ROOT/new-project"
mkdir -p "$NEW"
OUT="$(run_hook "$NEW")"
assert_contains "$OUT" "Aucun suivi detecte" "nouveau dossier -> rappel de bootstrap"

# Cas 5: cwd dans le périmètre, non suivi, mais dans trackignore.txt global -> silence
IGNORED="$SCOPE_ROOT/ignored-project"
mkdir -p "$IGNORED"
IGNORE_FILE="$TMP_HOME/.claude/project-tracker/trackignore.txt"
echo "$IGNORED" > "$IGNORE_FILE"
OUT="$(run_hook "$IGNORED")"
assert_empty "$OUT" "dossier dans trackignore.txt -> silence"

# Cas 6 (regression): cwd avec trailing slash doit se comporter identiquement à sans trailing slash
TRACKED_SLASH="$TRACKED/"
OUT_WITH_SLASH="$(run_hook "$TRACKED_SLASH")"
OUT_WITHOUT_SLASH="$(run_hook "$TRACKED")"
if [ "$OUT_WITH_SLASH" = "$OUT_WITHOUT_SLASH" ]; then
  echo "PASS: trailing slash normalization"
else
  echo "FAIL: trailing slash normalization — avec slash et sans slash ne produisent pas le même résultat"
  FAIL=1
fi

# Cas 7 (regression): python3 manquant doit exit 0 avec sortie vide
run_hook_no_python() {
  local cwd="$1"
  printf '{"cwd": "%s", "hook_event_name": "SessionStart", "source": "startup"}' "$cwd" | env -i PATH=/bin HOME="$TMP_HOME" bash "$HOOK"
}
OUT_NO_PYTHON="$(run_hook_no_python "$TRACKED" 2>&1)" || true
assert_empty "$OUT_NO_PYTHON" "python3 manquant -> exit 0 et sortie vide"

# Cas 8 (regression Fix 1): dossier dans .trackignore qui contient AUSSI son
# propre docs/project-tracker/STATUS.md -> l'exclusion .trackignore doit
# gagner, silence total (et non le message "projet suivi").
IGNORED_WITH_STATUS="$SCOPE_ROOT/ignored-with-status"
mkdir -p "$IGNORED_WITH_STATUS/docs/project-tracker"
cat > "$IGNORED_WITH_STATUS/docs/project-tracker/STATUS.md" <<'EOF'
---
project: IgnoredButTracked
status: active
last_updated: 2026-01-01
---
Contenu.
EOF
echo "$IGNORED_WITH_STATUS" >> "$IGNORE_FILE"
OUT="$(run_hook "$IGNORED_WITH_STATUS")"
assert_empty "$OUT" "trackignore.txt avec STATUS.md propre -> silence (exclusion prioritaire)"

# Cas 9 (regression Fix 2): un STATUS.md avec un corps volumineux (bien
# au-dela de 4000 octets) ne doit produire qu'une sortie bornee -- seul le
# frontmatter (cape a 4000 octets) est inclus, pas le corps entier.
BIGBODY="$SCOPE_ROOT/big-body-project"
mkdir -p "$BIGBODY/docs/project-tracker"
{
  echo "---"
  echo "project: BigBody"
  echo "status: active"
  echo "last_updated: 2026-01-01"
  echo "---"
  # Corps tres volumineux : > 4000 octets a lui seul.
  for i in $(seq 1 500); do
    echo "Ligne de corps numero $i qui sert uniquement a gonfler le fichier."
  done
} > "$BIGBODY/docs/project-tracker/STATUS.md"
OUT="$(run_hook "$BIGBODY")"
OUT_LEN="${#OUT}"
assert_contains "$OUT" "project: BigBody" "corps volumineux -> frontmatter toujours present"
if [ "$OUT_LEN" -lt 6000 ]; then
  echo "PASS: corps volumineux -> sortie totale bornee (obtenu $OUT_LEN octets)"
else
  echo "FAIL: corps volumineux -> sortie totale bornee — obtenu $OUT_LEN octets, attendu < 6000"
  FAIL=1
fi
if ! [[ "$OUT" == *"Ligne de corps numero 400"* ]]; then
  echo "PASS: corps volumineux -> le corps loin dans le fichier n'apparait pas"
else
  echo "FAIL: corps volumineux -> le corps ne devrait pas etre inclus en entier"
  FAIL=1
fi

# Cas 10 (regression): STATUS.md avec divider --- dans le corps ne doit pas
# laisser fuir le contenu post-divider dans la sortie frontmatter. Le sed original
# avait un bug : la plage /---/,/---/ repartait apres chaque fermeture de plage.
# Le fix awk arrete l extraction a la deuxieme ligne ---, donc rien du corps ne fuit.
BODY_WITH_DIVIDER="$SCOPE_ROOT/body-with-divider"
mkdir -p "$BODY_WITH_DIVIDER/docs/project-tracker"
cat > "$BODY_WITH_DIVIDER/docs/project-tracker/STATUS.md" <<'EOF'
---
project: BodyWithDivider
status: active
last_updated: 2026-01-01
---
Contenu narratif normal.

---

Ceci ne doit PAS apparaitre car c est apres un divider dans le corps.
EOF
OUT="$(run_hook "$BODY_WITH_DIVIDER")"
assert_contains "$OUT" "project: BodyWithDivider" "body-with-divider -> frontmatter present"
if [[ "$OUT" == *"Ceci ne doit PAS apparaitre"* ]]; then
  echo "FAIL: body-with-divider -> contenu post-divider a fui (bug non corrige)"
  FAIL=1
else
  echo "PASS: body-with-divider -> contenu post-divider ne fuit pas"
fi

# Cas 11 (nouveau): un dossier qui a un docs/ mais SANS project-tracker/
# dedans (ex. un docs/ generique d'un projet non suivi) ne doit pas etre
# pris pour un projet suivi.
DOCS_NO_PT="$SCOPE_ROOT/docs-without-project-tracker"
mkdir -p "$DOCS_NO_PT/docs"
echo "notes" > "$DOCS_NO_PT/docs/notes.md"
OUT="$(run_hook "$DOCS_NO_PT")"
assert_contains "$OUT" "Aucun suivi detecte" "docs/ sans project-tracker/ -> pas suivi, rappel de bootstrap"

# Cas 12 (nouveau): une entrée de trackignore.txt égale à une racine de
# périmètre n'ignore QUE ce dossier exact -- les projets à l'intérieur
# restent détectés.
echo "$SCOPE_ROOT" >> "$IGNORE_FILE"
OUT="$(run_hook "$SCOPE_ROOT")"
assert_empty "$OUT" "entree = racine de perimetre -> la racine exacte est ignoree"
OUT="$(run_hook "$TRACKED")"
assert_contains "$OUT" "projet suivi" "entree = racine de perimetre -> projet a l'interieur toujours detecte"

if [ "$FAIL" -eq 1 ]; then
  echo "Des tests ont echoue."
  exit 1
fi
echo "Tous les tests sont passes."
