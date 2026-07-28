#!/usr/bin/env bash
#
# Report an agent lifecycle event to the n8n W2 webhook (POST /agent-events),
# which calls Supabase sgm_ingest_event and shows up in Mission Control's Live
# Intelligence Feed.
#
# Usage:  report-event.sh <type>
#
# This used to be a one-line curl inlined in settings.json. It moved here once it
# needed real logic — role validation, task resolution and failure logging are not
# things to maintain inside an escaped JSON string.
#
# A hook must NEVER fail the agent, so every path exits 0. Failures are appended
# to $TMPDIR/sgm-hooks.log instead of being discarded: the previous version piped
# everything to /dev/null and stayed silently inert for days.
#
# Environment (set in .claude/settings.local.json, which is untracked):
#   N8N_EVENTS_URL     the W2 webhook
#   SGM_WEBHOOK_TOKEN  W2 rejects anything else with 401
#   SGM_POD            pod NAME, e.g. "pilot-app" — see the attribution note below
#
# Attribution: sgm_ingest_event resolves pod_id, agent_id and task_id from the
# payload. Verified against the live endpoint on 2026-07-28:
#   - `pod` is what unlocks pod_id. Without it every id comes back null and the
#     event is recorded but unattributable, so Mission Control cannot pod-scope it.
#   - `agent` must be one of the five roles in the agents.role CHECK constraint.
#     The main session reports CLAUDE_AGENT_NAME=main, which is not one of them, so
#     it is sent as null rather than risking a rejected insert.
#   - `task_id` accepts a uuid or a branch name, matched against tasks.branch in
#     full: "task-8-capitalize" resolved, but "task-8" and "8" did not. So send the
#     branch verbatim. On a non-task branch like main it stays null, which is right.
#
set -u

type="${1:-unknown}"
log="${TMPDIR:-/tmp}/sgm-hooks.log"

note() { printf '%s w2 %s %s\n' "$(date -u +%FT%TZ)" "$type" "$1" >>"$log" 2>/dev/null || true; }

url="${N8N_EVENTS_URL:-}"
token="${SGM_WEBHOOK_TOKEN:-}"
pod="${SGM_POD:-}"

case "$url" in '' | SET_IN_*) note 'skipped: N8N_EVENTS_URL not set'; exit 0 ;; esac
case "$token" in '' | SET_IN_*) note 'skipped: SGM_WEBHOOK_TOKEN not set'; exit 0 ;; esac
# Not fatal: the event is still worth recording, it just cannot be pod-scoped.
case "$pod" in '' | SET_IN_*) note 'warning: SGM_POD not set — event will be unattributed' ;; esac

case "${CLAUDE_AGENT_NAME:-}" in
  lead | backend | frontend | qa | reviewer) agent="\"${CLAUDE_AGENT_NAME}\"" ;;
  *) agent='null' ;;
esac

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"

body="$(printf '{"type":"%s","pod":"%s","agent":%s,"task_id":"%s","payload":{"session":"%s"},"ts":"%s"}' \
  "$type" "$pod" "$agent" "$branch" "${CLAUDE_SESSION_ID:-unknown}" "$(date -u +%FT%TZ)")"

code="$(curl -s -o /dev/null -w '%{http_code}' -m 5 -X POST "$url" \
  -H 'Content-Type: application/json' \
  -H "X-SGM-Token: ${token}" \
  -d "$body" 2>/dev/null)" || code='000'

[ "$code" = '200' ] || note "-> HTTP ${code:-000}"
exit 0
