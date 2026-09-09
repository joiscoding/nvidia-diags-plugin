#!/usr/bin/env bash
# Verify a Python symbol rename without editing files.
#
# Usage: verify_rename.sh <old_name> <new_name> [root]
#
# Exit 0 when <old_name> is gone from *.py and <new_name> appears in *.py.
# Non-Python <old_name> hits are informational.
set -uo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <old_name> <new_name> [root]" >&2
  exit 2
fi

old="$1"
new="$2"
root="${3:-.}"

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required" >&2
  exit 2
fi

common=(--word-regexp --sort path --glob '!**/__pycache__/**' --glob '!**/.git/**')

status=0

old_py="$(rg -n "${common[@]}" --glob '*.py' -- "$old" "$root" || true)"
if [[ -n "$old_py" ]]; then
  echo "FAIL: '$old' still present in Python files:"
  echo "$old_py" | sed 's/^/  /'
  status=1
else
  echo "ok: no '$old' in *.py"
fi

new_count="$(rg -c "${common[@]}" --glob '*.py' -- "$new" "$root" 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')"
new_files="$(rg -l "${common[@]}" --glob '*.py' -- "$new" "$root" 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$new_count" -eq 0 ]]; then
  echo "FAIL: '$new' not found in any *.py (rename did not land?)"
  status=1
else
  echo "ok: '$new' appears $new_count times in $new_files Python files"
fi

old_other="$(rg -n "${common[@]}" --glob '!*.py' -- "$old" "$root" || true)"
if [[ -n "$old_other" ]]; then
  echo "info: '$old' remains in non-Python files (expected; report as out of scope):"
  echo "$old_other" | sed 's/^/  /'
fi

exit $status
