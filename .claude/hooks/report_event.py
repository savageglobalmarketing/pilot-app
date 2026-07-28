#!/usr/bin/env python3
"""Report an agent lifecycle event, with token usage, to the n8n W2 webhook.

Invoked by report-event.sh (which guarantees a zero exit no matter what happens
here). Reads the hook JSON on stdin, builds the W2 payload contract, and POSTs it
to $N8N_EVENTS_URL. W2 calls Supabase sgm_ingest_event, which records the event,
inserts a cost_log row when `usage` is present, and increments tasks.spend_usd.

Everything below was measured against the live endpoint and against real
transcripts rather than assumed. The traps are documented where they bite.

Stdin, per the Claude Code hooks reference:
  session_id, transcript_path, cwd, hook_event_name, agent_type, agent_id,
  and for PostToolUse also tool_name / tool_input / tool_output.

Note that CLAUDE_AGENT_NAME and CLAUDE_SESSION_ID are NOT documented hook
environment variables. An earlier version of this hook read both from the
environment, which is why agent attribution never populated. Read stdin instead.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TIMEOUT = 5

# agents.role is CHECK-constrained to exactly these. Anything else (including the
# main session, which sends no agent_type at all) must go as null or the insert is
# rejected. Verified: a null agent is accepted cleanly and leaves agent_id null.
ROLES = {"lead", "backend", "frontend", "qa", "reviewer"}

# ---------------------------------------------------------------- pricing
#
# USD per million tokens, (base input, output), from the published Anthropic
# pricing table: https://platform.claude.com/docs/en/about-claude/pricing
# Read 2026-07-28. Cache rates are NOT listed separately here because they are
# fixed multipliers of base input, which is also how the docs define them:
#
#   cache read (hit)     0.1x base input
#   5-minute cache write 1.25x base input
#   1-hour cache write   2x base input
#
# Deriving them means there are two numbers per model to keep current instead of
# five, and the multipliers cannot drift out of agreement with the base rate.
PRICES = {
    "claude-fable-5": (10.0, 50.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-opus-4-5": (5.0, 25.0),
    "claude-opus-4-1": (15.0, 75.0),
    "claude-opus-4": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-sonnet-4": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-haiku-3-5": (0.8, 4.0),
}

# Sonnet 5 runs on introductory pricing through 2026-08-31, then rises. Pricing
# depends on when the tokens were spent, so it cannot be a constant.
SONNET_5_INTRO_UNTIL = "2026-08-31"

# Fast mode is a flat premium for these two models, not a multiplier, and cache
# multipliers apply on top of the fast base rate.
FAST_MODELS = {"claude-opus-5", "claude-opus-4-8"}
FAST_PRICE = (10.0, 50.0)


def rate_for(model: str, spent_on: str) -> tuple[float, float] | None:
    """Base (input, output) per MTok, or None when the model has no known rate.

    Never guesses. An unpriced model returns None and the caller reports tokens
    without a cost rather than inventing one — a wrong number in a spend
    dashboard with hard budget caps is worse than an absent one.
    """
    if model.startswith("claude-sonnet-5"):
        return (2.0, 10.0) if spent_on <= SONNET_5_INTRO_UNTIL else (3.0, 15.0)
    # Real model ids carry date suffixes (claude-haiku-4-5-20251001), so match on
    # the longest known prefix rather than equality.
    best = max((k for k in PRICES if model.startswith(k)), key=len, default=None)
    return PRICES[best] if best else None


def message_cost(model: str, usage: dict, spent_on: str) -> float | None:
    base = rate_for(model, spent_on)
    if base is None:
        return None
    inp, out = base
    if usage.get("speed") == "fast" and model in FAST_MODELS:
        inp, out = FAST_PRICE

    cache = usage.get("cache_creation")
    if isinstance(cache, dict) and cache:
        write_5m = cache.get("ephemeral_5m_input_tokens") or 0
        write_1h = cache.get("ephemeral_1h_input_tokens") or 0
    else:
        # No breakdown available. Attribute to 5m, the cheaper of the two, so a
        # missing field cannot silently inflate spend.
        write_5m = usage.get("cache_creation_input_tokens") or 0
        write_1h = 0

    cost = (
        (usage.get("input_tokens") or 0) * inp
        + (usage.get("output_tokens") or 0) * out
        + (usage.get("cache_read_input_tokens") or 0) * inp * 0.1
        + write_5m * inp * 1.25
        + write_1h * inp * 2.0
    ) / 1_000_000

    if usage.get("inference_geo") == "us":
        cost *= 1.1  # US-only inference carries a 1.1x multiplier on every category
    if usage.get("service_tier") == "batch":
        cost *= 0.5
    return cost


# ---------------------------------------------------------------- transcript


def read_transcript(path: str) -> dict:
    """Total usage and cost for a whole transcript.

    Two traps, both found by measuring a real transcript:

    1. Assistant messages REPEAT. One file had 2038 assistant lines but only 929
       distinct message ids. Summing every line reported $722 where the true
       figure was $306. Dedupe by message id.
    2. Cache writes were 100% 1-hour (2x base), not the 5-minute default (1.25x).
       Assuming 1.25x understates cache-write cost by 60%, so read the
       cache_creation breakdown rather than the flat total.
    """
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "cost_usd": 0.0,
    }
    seen: set[str] = set()
    unpriced: set[str] = set()

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except (ValueError, TypeError):
                continue
            if rec.get("type") != "assistant":
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            mid = msg.get("id")
            if not mid or mid in seen:
                continue
            seen.add(mid)

            model = msg.get("model") or ""
            usage = msg.get("usage") or {}
            if not isinstance(usage, dict):
                continue

            for key in (
                "input_tokens",
                "output_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            ):
                totals[key] += usage.get(key) or 0

            # Rates change over time, so price each message on its own timestamp.
            spent_on = str(rec.get("timestamp") or "")[:10] or _today()
            cost = message_cost(model, usage, spent_on)
            if cost is None:
                if model and not model.startswith("<"):
                    unpriced.add(model)
            else:
                totals["cost_usd"] += cost

    totals["messages"] = len(seen)
    totals["unpriced_models"] = sorted(unpriced)
    return totals


# ---------------------------------------------------------------- watermark


def state_file(session: str) -> Path:
    """Where the already-reported totals for a session live.

    Deliberately NOT under TMPDIR: losing this file means the next Stop re-reports
    the entire session and double counts spend. XDG state persists across reboots.
    """
    root = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(root) / "sgm" / "usage" / f"{session}.json"


def usage_delta(session: str, totals: dict) -> dict | None:
    """Only what has not been reported yet, and record the new high-water mark.

    Stop fires once per turn, not once per session, and a resumed session re-reads
    the same transcript. Sending cumulative totals every time would multiply spend
    by the number of turns. Deltas make repeat fires harmless.
    """
    path = state_file(session)
    previous = {}
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass

    keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
            "cache_read_input_tokens", "cost_usd")
    # max(0, ...) guards against a transcript that shrank, e.g. after compaction.
    delta = {k: max(0, (totals.get(k) or 0) - (previous.get(k) or 0)) for k in keys}
    if delta["cost_usd"] <= 0 and delta["output_tokens"] <= 0:
        return None  # nothing new since the last report

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({k: totals.get(k) or 0 for k in keys}), encoding="utf-8")
    except OSError as exc:
        # Better to skip reporting than to report without recording the watermark,
        # which would double count on the next fire.
        note(f"state write failed, skipping usage: {exc}")
        return None
    return delta


# ---------------------------------------------------------------- plumbing

LOG = Path(os.environ.get("TMPDIR", "/tmp")) / "sgm-hooks.log"
EVENT_TYPE = sys.argv[1] if len(sys.argv) > 1 else "unknown"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def note(message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp} w2 {EVENT_TYPE} {message}\n")
    except OSError:
        pass


def git_branch(cwd: str) -> str:
    """The branch is how a task is identified.

    Verified against the live resolver: it matches tasks.branch in full.
    "task-8-capitalize" resolved; "task-8" and "8" did not.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None, capture_output=True, text=True, timeout=TIMEOUT,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def post(url: str, token: str, body: dict) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-SGM-Token": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                note(f"-> HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        note(f"-> HTTP {exc.code}")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        note(f"-> no response: {exc}")


def baseline_all() -> int:
    """Seed watermarks for existing sessions without reporting them. Run once.

    Why this exists: the watermark starts empty, so the first Stop in a session
    that predates this hook would report its ENTIRE history as if it were spent
    now. One real transcript measured $342. SGM W6 — Budget & Health Watchdog runs
    every 15 minutes and pauses a pod over its daily cap, so back-billing history
    would halt the fleet within the quarter hour.

    Transcript filenames are session ids, which is what the watermark is keyed on.
    """
    root = Path.home() / ".claude" / "projects"
    seeded = total = 0
    for transcript in sorted(root.glob("*/*.jsonl")):
        session = transcript.stem
        path = state_file(session)
        if path.exists():
            continue
        try:
            totals = read_transcript(str(transcript))
        except OSError:
            continue
        keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                "cache_read_input_tokens", "cost_usd")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({k: totals.get(k) or 0 for k in keys}), encoding="utf-8")
        except OSError as exc:
            print(f"  could not seed {session}: {exc}", file=sys.stderr)
            continue
        seeded += 1
        total += totals["cost_usd"]
        print(f"  {session}  ${totals['cost_usd']:>10,.2f}  {totals['messages']:>5} messages")
    print(f"\n  seeded {seeded} session(s); ${total:,.2f} of history will NOT be reported.")
    print("  Usage from here on is reported as deltas.")
    return 0


def main() -> None:
    if "--baseline" in sys.argv:
        sys.exit(baseline_all())

    try:
        hook = json.loads(sys.stdin.read() or "{}")
    except (ValueError, TypeError):
        hook = {}
    if not isinstance(hook, dict):
        hook = {}

    url = os.environ.get("N8N_EVENTS_URL", "")
    token = os.environ.get("SGM_WEBHOOK_TOKEN", "")
    pod = os.environ.get("SGM_POD", "")
    for name, value in (("N8N_EVENTS_URL", url), ("SGM_WEBHOOK_TOKEN", token)):
        if not value or value.startswith("SET_IN_"):
            note(f"skipped: {name} not set")
            return
    if not pod or pod.startswith("SET_IN_"):
        # Not fatal. The event is still worth recording, it just cannot be
        # pod-scoped in Mission Control.
        note("warning: SGM_POD not set — event will be unattributed")
        pod = ""

    agent = hook.get("agent_type")
    session = hook.get("session_id") or "unknown"
    cwd = hook.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    detail: dict = {"session": session}
    # PostToolUse carries the file, which is far more useful in the feed than a
    # bare session id.
    target = (hook.get("tool_input") or {}).get("file_path") if isinstance(hook.get("tool_input"), dict) else None
    if target:
        detail["summary"] = f"{hook.get('tool_name') or 'Changed'} {os.path.basename(target)}"
        detail["path"] = target

    body = {
        "type": EVENT_TYPE,
        "pod": pod,
        "agent": agent if agent in ROLES else None,
        "task_id": git_branch(cwd),
        "payload": detail,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Usage is a whole-session figure, so it belongs on Stop. Sending it from
    # PostToolUse would report the running total once per edit.
    transcript = hook.get("transcript_path")
    if EVENT_TYPE == "session_stopped" and transcript and os.path.exists(transcript):
        try:
            totals = read_transcript(transcript)
        except OSError as exc:
            note(f"transcript unreadable: {exc}")
            totals = None
        if totals:
            if totals["unpriced_models"]:
                note("no rate for " + ", ".join(totals["unpriced_models"]) + " — cost excludes them")
            delta = usage_delta(session, totals)
            if delta:
                body["usage"] = {
                    # cost_log has no cache columns, so input_tokens carries total
                    # input across all categories. The breakdown is preserved in
                    # payload.usage_detail so nothing is lost.
                    "input_tokens": delta["input_tokens"]
                    + delta["cache_creation_input_tokens"]
                    + delta["cache_read_input_tokens"],
                    "output_tokens": delta["output_tokens"],
                    "cost_usd": round(delta["cost_usd"], 6),
                }
                detail["usage_detail"] = {
                    "base_input_tokens": delta["input_tokens"],
                    "cache_write_tokens": delta["cache_creation_input_tokens"],
                    "cache_read_tokens": delta["cache_read_input_tokens"],
                    "messages_in_transcript": totals["messages"],
                }

    post(url, token, body)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — a hook must never fail the agent
        note(f"unhandled: {type(exc).__name__}: {exc}")
