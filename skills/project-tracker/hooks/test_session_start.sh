#!/usr/bin/env bash
# Manual test for session_start.sh — no test-framework dependency.
# Run with: bash test_session_start.sh
set -uo pipefail

HOOK="$(dirname "$0")/session_start.sh"
FAIL=0

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if [[ "$haystack" == *"$needle"* ]]; then
    echo "PASS: $label"
  else
    echo "FAIL: $label — expected to find: $needle"
    FAIL=1
  fi
}

assert_empty() {
  local value="$1" label="$2"
  if [ -z "$value" ]; then
    echo "PASS: $label"
  else
    echo "FAIL: $label — expected empty, got: $value"
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

# Case 1: cwd outside any scope -> total silence
OUT="$(run_hook "/tmp/outside-scope-$$")"
assert_empty "$OUT" "outside scope -> silence"

# Case 2: cwd within the scope, tracked project (docs/project-tracker/STATUS.md present)
TRACKED="$SCOPE_ROOT/tracked-project"
mkdir -p "$TRACKED/docs/project-tracker"
cat > "$TRACKED/docs/project-tracker/STATUS.md" <<'EOF'
---
project: Tracked
status: active
last_updated: 2026-01-01
---
Content.
EOF
OUT="$(run_hook "$TRACKED")"
assert_contains "$OUT" "tracked project" "tracked project -> verification reminder"
assert_contains "$OUT" "project: Tracked" "tracked project -> STATUS.md content included"
assert_contains "$OUT" "Not yet configured" "tracked project missing keys -> enumerated"
assert_contains "$OUT" "reminders_list" "missing reminders_list listed"
assert_contains "$OUT" "category" "missing category listed"
assert_contains "$OUT" "portfolio.txt" "missing global portfolio.txt listed"

# Case 3: cwd in a deep subfolder of an already-tracked project
mkdir -p "$TRACKED/subdir/deep"
OUT="$(run_hook "$TRACKED/subdir/deep")"
assert_contains "$OUT" "tracked project" "subfolder of a tracked project -> finds the root"

# Case 4: cwd within the scope, not tracked, not ignored -> proactive tracking prompt
NEW="$SCOPE_ROOT/new-project"
mkdir -p "$NEW"
OUT="$(run_hook "$NEW")"
assert_contains "$OUT" "UNTRACKED project" "new folder -> untracked flag"
assert_contains "$OUT" "AskUserQuestion" "new folder -> selectable-choice question"
assert_contains "$OUT" "Yes, set it up" "new folder -> yes option"
assert_contains "$OUT" "No, don't ask again" "new folder -> no option"
assert_contains "$OUT" "Not now" "new folder -> not-now option"

# Case 5: cwd within the scope, not tracked, but in the global trackignore.txt -> silence
IGNORED="$SCOPE_ROOT/ignored-project"
mkdir -p "$IGNORED"
IGNORE_FILE="$TMP_HOME/.claude/project-tracker/trackignore.txt"
echo "$IGNORED" > "$IGNORE_FILE"
OUT="$(run_hook "$IGNORED")"
assert_empty "$OUT" "folder in trackignore.txt -> silence"

# Case 6 (regression): cwd with a trailing slash must behave identically to without one
TRACKED_SLASH="$TRACKED/"
OUT_WITH_SLASH="$(run_hook "$TRACKED_SLASH")"
OUT_WITHOUT_SLASH="$(run_hook "$TRACKED")"
if [ "$OUT_WITH_SLASH" = "$OUT_WITHOUT_SLASH" ]; then
  echo "PASS: trailing slash normalization"
else
  echo "FAIL: trailing slash normalization — with slash and without slash do not produce the same result"
  FAIL=1
fi

# Case 7 (regression): missing python3 must exit 0 with empty output
run_hook_no_python() {
  local cwd="$1"
  printf '{"cwd": "%s", "hook_event_name": "SessionStart", "source": "startup"}' "$cwd" | env -i PATH=/bin HOME="$TMP_HOME" bash "$HOOK"
}
OUT_NO_PYTHON="$(run_hook_no_python "$TRACKED" 2>&1)" || true
assert_empty "$OUT_NO_PYTHON" "missing python3 -> exit 0 and empty output"

# Case 8 (regression Fix 1): a folder in trackignore.txt that ALSO has its own
# docs/project-tracker/STATUS.md -> the trackignore exclusion must win,
# total silence (not the "tracked project" message).
IGNORED_WITH_STATUS="$SCOPE_ROOT/ignored-with-status"
mkdir -p "$IGNORED_WITH_STATUS/docs/project-tracker"
cat > "$IGNORED_WITH_STATUS/docs/project-tracker/STATUS.md" <<'EOF'
---
project: IgnoredButTracked
status: active
last_updated: 2026-01-01
---
Content.
EOF
echo "$IGNORED_WITH_STATUS" >> "$IGNORE_FILE"
OUT="$(run_hook "$IGNORED_WITH_STATUS")"
assert_empty "$OUT" "trackignore.txt with its own STATUS.md -> silence (exclusion takes precedence)"

# Case 9 (regression Fix 2): a STATUS.md with a large body (well beyond 4000
# bytes) must produce only bounded output -- only the frontmatter (capped at
# 4000 bytes) is included, not the whole body.
BIGBODY="$SCOPE_ROOT/big-body-project"
mkdir -p "$BIGBODY/docs/project-tracker"
{
  echo "---"
  echo "project: BigBody"
  echo "status: active"
  echo "last_updated: 2026-01-01"
  echo "---"
  # Very large body: > 4000 bytes on its own.
  for i in $(seq 1 500); do
    echo "Body line number $i, here only to bloat the file."
  done
} > "$BIGBODY/docs/project-tracker/STATUS.md"
OUT="$(run_hook "$BIGBODY")"
OUT_LEN="${#OUT}"
assert_contains "$OUT" "project: BigBody" "large body -> frontmatter still present"
if [ "$OUT_LEN" -lt 6000 ]; then
  echo "PASS: large body -> total output bounded (got $OUT_LEN bytes)"
else
  echo "FAIL: large body -> total output bounded — got $OUT_LEN bytes, expected < 6000"
  FAIL=1
fi
if ! [[ "$OUT" == *"Body line number 400"* ]]; then
  echo "PASS: large body -> body deep in the file does not appear"
else
  echo "FAIL: large body -> the body should not be included in full"
  FAIL=1
fi

# Case 10 (regression): a STATUS.md with a --- divider in the body must not
# leak the post-divider content into the frontmatter output. The original sed
# had a bug: the /---/,/---/ range restarted after each range close. The awk
# fix stops extraction at the second --- line, so nothing from the body leaks.
BODY_WITH_DIVIDER="$SCOPE_ROOT/body-with-divider"
mkdir -p "$BODY_WITH_DIVIDER/docs/project-tracker"
cat > "$BODY_WITH_DIVIDER/docs/project-tracker/STATUS.md" <<'EOF'
---
project: BodyWithDivider
status: active
last_updated: 2026-01-01
---
Normal narrative content.

---

This must NOT appear because it is after a divider in the body.
EOF
OUT="$(run_hook "$BODY_WITH_DIVIDER")"
assert_contains "$OUT" "project: BodyWithDivider" "body-with-divider -> frontmatter present"
if [[ "$OUT" == *"This must NOT appear"* ]]; then
  echo "FAIL: body-with-divider -> post-divider content leaked (bug not fixed)"
  FAIL=1
else
  echo "PASS: body-with-divider -> post-divider content does not leak"
fi

# Case 11 (new): a folder that has a docs/ but NO project-tracker/ inside it
# (e.g. a generic docs/ of an untracked project) must not be taken for a
# tracked project.
DOCS_NO_PT="$SCOPE_ROOT/docs-without-project-tracker"
mkdir -p "$DOCS_NO_PT/docs"
echo "notes" > "$DOCS_NO_PT/docs/notes.md"
OUT="$(run_hook "$DOCS_NO_PT")"
assert_contains "$OUT" "UNTRACKED project" "docs/ without project-tracker/ -> not tracked, prompt shown"

# Case 12 (new): an entry in trackignore.txt equal to a scope root ignores
# ONLY that exact folder -- the projects inside it are still detected.
echo "$SCOPE_ROOT" >> "$IGNORE_FILE"
OUT="$(run_hook "$SCOPE_ROOT")"
assert_empty "$OUT" "entry = scope root -> the exact root is ignored"
OUT="$(run_hook "$TRACKED")"
assert_contains "$OUT" "tracked project" "entry = scope root -> project inside is still detected"

# Case 13 (new): a tracked project with every key set AND a global
# portfolio.txt -> no "Not yet configured" line.
FULL="$SCOPE_ROOT/full-project"
mkdir -p "$FULL/docs/project-tracker"
cat > "$FULL/docs/project-tracker/STATUS.md" <<'EOF'
---
project: Full
status: active
last_updated: 2026-01-01
reminders_list: "non"
backlog_model: "adopté"
category: "non"
---
Content.
EOF
printf '/tmp/x\n' > "$TMP_HOME/.claude/project-tracker/portfolio.txt"
OUT="$(run_hook "$FULL")"
assert_contains "$OUT" "tracked project" "full project -> still detected"
if [[ "$OUT" == *"Not yet configured"* ]]; then
  echo "FAIL: full project -> should not emit 'Not yet configured'"
  FAIL=1
else
  echo "PASS: full project -> no 'Not yet configured' line"
fi

# Case 14 (new): a "~"-prefixed entry in scopes.txt resolves against $HOME.
TILDE_SCOPE="$TMP_HOME/tildescope"
mkdir -p "$TILDE_SCOPE/proj"
printf '%s\n~/tildescope\n' "$SCOPE_ROOT" > "$TMP_HOME/.claude/project-tracker/scopes.txt"
: > "$TMP_HOME/.claude/project-tracker/trackignore.txt"
OUT="$(run_hook "$TILDE_SCOPE/proj")"
assert_contains "$OUT" "UNTRACKED project" "~ scope entry -> resolved, folder seen as new"

if [ "$FAIL" -eq 1 ]; then
  echo "Some tests failed."
  exit 1
fi
echo "All tests passed."
