#!/usr/bin/env bash
# Manual test for reminders_sync_trigger.sh — no test-framework
# dependency. Run with: bash test_reminders_sync_trigger.sh
set -uo pipefail

HOOK="$(dirname "$0")/reminders_sync_trigger.sh"
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
Content.
EOF

# Case 1: Edit on docs/project-tracker/STATUS.md, tracked + linked project -> additionalContext injected
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-1")"
assert_contains "$OUT" "additionalContext" "STATUS.md edit, linked -> additionalContext"
assert_contains "$OUT" "tracked-project" "additionalContext contains the project name"
assert_contains "$OUT" "references/reminders-sync.md" "additionalContext points at the reference doc"

# Case 2: Write on docs/project-tracker/ROADMAP.md, same project, new session -> same
OUT="$(run_hook "Write" "$TRACKED/docs/project-tracker/ROADMAP.md" "session-2")"
assert_contains "$OUT" "additionalContext" "ROADMAP.md write, linked -> additionalContext"

# Case 3: a tool other than Edit/Write -> silence
OUT="$(run_hook "Bash" "$TRACKED/docs/project-tracker/STATUS.md" "session-3")"
assert_empty "$OUT" "tool_name=Bash -> silence"

# Case 4: a file other than STATUS.md/ROADMAP.md (README.md at the root) -> silence
OUT="$(run_hook "Edit" "$TRACKED/README.md" "session-4")"
assert_empty "$OUT" "README.md -> silence"

# Case 5: outside the scope (not in scopes.txt) -> silence
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
assert_empty "$OUT" "outside scope -> silence"

# Case 6: in trackignore.txt -> silence
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

# Case 7: reminders_list absent -> silence
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

# Case 8: reminders_list == "non" -> silence
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

# Case 9: ROADMAP.md edited but STATUS.md absent from the same folder -> silence
NOSTATUS="$SCOPE_ROOT/no-status-project"
mkdir -p "$NOSTATUS/docs/project-tracker"
OUT="$(run_hook "Edit" "$NOSTATUS/docs/project-tracker/ROADMAP.md" "session-9")"
assert_empty "$OUT" "STATUS.md absent -> silence"

# Case 10: debounce -- same session, same project, two triggers -> the second is silent
OUT1="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-10")"
OUT2="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-10")"
assert_contains "$OUT1" "additionalContext" "debounce -> first trigger produces context"
assert_empty "$OUT2" "debounce -> second trigger (same session) silent"

# Case 11: debounce re-armed on a different session
OUT3="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-11")"
assert_contains "$OUT3" "additionalContext" "debounce -> new session reproduces the context"

# Case 12 (regression): missing python3 -> exit 0, empty output, no crash
run_hook_no_python() {
  local tool_name="$1" file_path="$2" session_id="$3"
  printf '{"session_id": "%s", "cwd": "%s", "hook_event_name": "PostToolUse", "tool_name": "%s", "tool_input": {"file_path": "%s"}}' \
    "$session_id" "$(dirname "$file_path")" "$tool_name" "$file_path" \
    | env -i PATH=/bin HOME="$TMP_HOME" TMPDIR="$TMP_MARKERS" bash "$HOOK"
}
OUT="$(run_hook_no_python "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-12" 2>&1)" || true
assert_empty "$OUT" "missing python3 -> silence"

# Case 13 (new): STATUS.md directly under docs/ (not docs/project-tracker/)
# -> silence, the pattern requires the exact project-tracker/ subfolder.
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
assert_empty "$OUT" "STATUS.md directly under docs/ (not project-tracker/) -> silence"

# Case 14 (new): trackignore.txt with an entry = scope root.
# The exact root is ignored; a project inside it is not.
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
assert_empty "$OUT" "entry = scope root -> exact root ignored"
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "session-15")"
assert_contains "$OUT" "additionalContext" "entry = scope root -> project inside still handled"

if [ "$FAIL" -eq 1 ]; then
  echo "Some tests failed."
  exit 1
fi
echo "All tests passed."
