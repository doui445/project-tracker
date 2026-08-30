#!/usr/bin/env bash
# Manual test for portfolio_regen.sh — no test-framework dependency.
# Run with: bash test_portfolio_regen.sh
set -uo pipefail

HOOK="$(dirname "$0")/portfolio_regen.sh"
FAIL=0

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if [[ "$haystack" == *"$needle"* ]]; then echo "PASS: $label"; else
    echo "FAIL: $label — expected to find: $needle"; FAIL=1; fi
}
assert_empty() {
  local value="$1" label="$2"
  if [ -z "$value" ]; then echo "PASS: $label"; else
    echo "FAIL: $label — expected empty, got: $value"; FAIL=1; fi
}
assert_file() {
  local path="$1" label="$2"
  if [ -f "$path" ]; then echo "PASS: $label"; else
    echo "FAIL: $label — expected file: $path"; FAIL=1; fi
}
assert_no_file() {
  local path="$1" label="$2"
  if [ ! -e "$path" ]; then echo "PASS: $label"; else
    echo "FAIL: $label — file should not exist: $path"; FAIL=1; fi
}

run_hook() {
  local tool_name="$1" file_path="$2" session_id="$3"
  printf '{"session_id": "%s", "cwd": "%s", "hook_event_name": "PostToolUse", "tool_name": "%s", "tool_input": {"file_path": "%s"}, "tool_response": {"success": true}}' \
    "$session_id" "$(dirname "$file_path")" "$tool_name" "$file_path" \
    | HOME="$TMP_HOME" TMPDIR="$TMP_MARKERS" bash "$HOOK"
}

TMP_HOME="$(mktemp -d)"
TMP_MARKERS="$(mktemp -d)"
OUT_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_HOME" "$TMP_MARKERS" "$OUT_DIR"' EXIT

mkdir -p "$TMP_HOME/.claude/project-tracker"
# The hook shells out to the real generate_portfolio.py via
# $HOME/.claude/skills/project-tracker/... — point that at the repo copy.
mkdir -p "$TMP_HOME/.claude/skills"
ln -s "$(cd "$(dirname "$0")/.." && pwd)" "$TMP_HOME/.claude/skills/project-tracker"

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
---
Content.
EOF

# Case 1: portfolio.txt absent -> additionalContext once, no file
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "s1")"
assert_contains "$OUT" "not configured" "portfolio.txt absent -> additionalContext"
OUT2="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "s1")"
assert_empty "$OUT2" "portfolio.txt absent -> debounced within session"

# Case 2: portfolio.txt -> a folder -> PORTFOLIO.html regenerated, silent
echo "$OUT_DIR" > "$TMP_HOME/.claude/project-tracker/portfolio.txt"
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "s2")"
assert_empty "$OUT" "configured -> silent"
assert_file "$OUT_DIR/PORTFOLIO.html" "configured -> PORTFOLIO.html written"
grep -q "Tracked" "$OUT_DIR/PORTFOLIO.html" && echo "PASS: html contains project" || { echo "FAIL: html missing project"; FAIL=1; }

# Case 3: ROADMAP.md -> nothing
rm -f "$OUT_DIR/PORTFOLIO.html"
OUT="$(run_hook "Write" "$TRACKED/docs/project-tracker/ROADMAP.md" "s3")"
assert_empty "$OUT" "ROADMAP.md -> silent"
assert_no_file "$OUT_DIR/PORTFOLIO.html" "ROADMAP.md -> no regen"

# Case 4: tool_name Bash -> nothing
OUT="$(run_hook "Bash" "$TRACKED/docs/project-tracker/STATUS.md" "s4")"
assert_empty "$OUT" "tool_name=Bash -> silent"
assert_no_file "$OUT_DIR/PORTFOLIO.html" "Bash -> no regen"

# Case 5: outside scope -> nothing
OUTSIDE="$TMP_HOME/outside/docs/project-tracker/STATUS.md"
mkdir -p "$(dirname "$OUTSIDE")"
printf -- '---\nproject: O\nstatus: active\nlast_updated: 2026-01-01\n---\n' > "$OUTSIDE"
OUT="$(run_hook "Edit" "$OUTSIDE" "s5")"
assert_empty "$OUT" "outside scope -> silent"
assert_no_file "$OUT_DIR/PORTFOLIO.html" "outside scope -> no regen"

# Case 6: in trackignore.txt -> nothing
IGNORED="$SCOPE_ROOT/ignored-project"
mkdir -p "$IGNORED/docs/project-tracker"
printf -- '---\nproject: I\nstatus: active\nlast_updated: 2026-01-01\n---\n' > "$IGNORED/docs/project-tracker/STATUS.md"
echo "$IGNORED" > "$TMP_HOME/.claude/project-tracker/trackignore.txt"
OUT="$(run_hook "Edit" "$IGNORED/docs/project-tracker/STATUS.md" "s6")"
assert_empty "$OUT" "ignored project -> silent"
assert_no_file "$OUT_DIR/PORTFOLIO.html" "ignored project -> no regen"

# Case 7: trackignore.txt entry = scope root -> project inside still regenerates
echo "$SCOPE_ROOT" > "$TMP_HOME/.claude/project-tracker/trackignore.txt"
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "s7")"
assert_empty "$OUT" "scope-root ignore entry -> silent"
assert_file "$OUT_DIR/PORTFOLIO.html" "scope-root ignore entry -> project inside still regenerated"

# Case 8: portfolio.txt comments only -> no regen, no additionalContext
rm -f "$OUT_DIR/PORTFOLIO.html"
: > "$TMP_HOME/.claude/project-tracker/trackignore.txt"
printf '# not set\n' > "$TMP_HOME/.claude/project-tracker/portfolio.txt"
OUT="$(run_hook "Edit" "$TRACKED/docs/project-tracker/STATUS.md" "s8")"
assert_empty "$OUT" "portfolio.txt comments-only -> silent"
assert_no_file "$OUT_DIR/PORTFOLIO.html" "portfolio.txt comments-only -> no regen"

# Case 9: python3 missing -> exit 0, no crash
OUT="$(printf '{"session_id": "s9", "cwd": "%s", "hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": "%s"}}' "$TRACKED/docs/project-tracker" "$TRACKED/docs/project-tracker/STATUS.md" | env -i PATH=/bin HOME="$TMP_HOME" TMPDIR="$TMP_MARKERS" bash "$HOOK" 2>&1)" || true
assert_empty "$OUT" "missing python3 -> silent"

if [ "$FAIL" -eq 1 ]; then echo "Some tests failed."; exit 1; fi
echo "All tests passed."
