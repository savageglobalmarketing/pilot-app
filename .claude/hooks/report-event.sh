#!/usr/bin/env bash
#
# Entry point for the W2 agent-event hooks. Usage:  report-event.sh <type>
#
# This is deliberately thin. All logic lives in report_event.py, because the hook
# now parses the stdin JSON, reads a session transcript and prices token usage —
# none of which belongs in shell. What stays here is the one guarantee that must
# hold even if Python is missing or the script is broken: **exit 0, always.**
# A hook that exits non-zero interferes with the agent it is only meant to observe.
#
# Failures append to $TMPDIR/sgm-hooks.log rather than vanishing. An earlier
# version piped everything to /dev/null and sat silently inert for days.
#
set -u

type="${1:-unknown}"
log="${TMPDIR:-/tmp}/sgm-hooks.log"
dir="$(cd "$(dirname "$0")" 2>/dev/null && pwd)" || dir='.'

note() { printf '%s w2 %s %s\n' "$(date -u +%FT%TZ)" "$type" "$1" >>"$log" 2>/dev/null || true; }

if ! command -v python3 >/dev/null 2>&1; then
  note 'skipped: python3 not found'
  exit 0
fi

# stdin (the hook JSON) passes straight through to the child.
python3 "$dir/report_event.py" "$type" || note "report_event.py exited $?"
exit 0
