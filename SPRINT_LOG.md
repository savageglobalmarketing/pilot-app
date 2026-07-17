# SPRINT_LOG — SGM Agent Dev Team

Running log of what was done, decisions made, and deviations from
`~/apps/sgm-agent-sprint/agent-dev-team-plan.md`. Newest entries at the bottom of
each day.

---

## Day 1 (2026-07-16) — Foundation & Guardrails

### Assessment (pre-work)
- Pilot app = `pilot-app` (Node + TypeScript, Vitest, GitHub Actions). Confirmed
  lowest-risk, best-tested app.
- Repo health: build green, CI green (3/3 runs), 7/7 tests pass. Coverage of
  existing logic is effectively complete by inspection, but there was **no
  coverage instrumentation, no lint, and tests were not type-checked** in CI.
- **Tier 0 auto-merge verdict: NOT yet trustworthy.** Reasons: (1) no branch
  protection on `main`; (2) no enforced coverage floor; (3) tests not
  type-checked / no lint gate. Everything runs **Tier 1** until these are fixed.

### Decisions
- **D1 — Repo home:** Move `pilot-app` from personal account `sanchexm` to the
  `savageglobalmarketing` GitHub org (user directive). Rationale: correct
  long-term home; org ownership and team access.
- **D2 — Supabase:** User creates the Supabase project and supplies
  `SUPABASE_URL` + service key as env/secret (never committed). Claude cannot
  create accounts. Schema staged paste-ready from `infra/schema.sql`.
- **D3 — CI hardening in scope for Day 1:** add coverage threshold, lint, and
  test type-checking so the CI signal is strong enough to eventually justify
  Tier 0.
- **D4 — Reviewer agent tools:** Keeping the supplied `reviewer.md` as-is (it
  relies on the CI signal and QA's verdict; it does NOT run tests itself). The
  plan's §3 inline example listed `Bash(npm test)`. Flagged for user; QA owns
  test execution, so this is defensible. Revisit if the CI signal proves
  insufficient.

### Deviations / blockers
- **DEV-1 (guardrail risk): Branch protection unavailable on a free plan for a
  private repo.** Confirmed: personal free account returns 403 (needs Pro or
  public); the `savageglobalmarketing` org is on the **free** plan, which also
  cannot protect private repos (needs Team/Enterprise). Section 6 requires
  `main` protection (non-negotiable). Resolution pending user decision:
  upgrade org to Team, make repo public, or run Tier 1-only with protection
  deferred (documented weakening). Until resolved, **no Tier 0 auto-merge** and
  the pod operates with human approval on every merge.
  - **RESOLVED (2026-07-16):** User chose to make `pilot-app` **public** (repo
    has no secrets/client data — scanned before flipping). Ruleset
    `main-protection` (#19069447) now enforces the `build-and-test` check on
    `main` and blocks force-push/deletion. Direct pushes to `main` are blocked;
    changes go via PR. Tier 0 auto-merge still deferred until the coverage floor
    proves itself over several real merges.

### Work completed
- `CLAUDE.md` written for the real stack (Node 22 / TS 5.5 / Vitest / ESLint).
- Pod config placed: `.claude/agents/{lead,backend,frontend,qa,reviewer}.md`,
  `.claude/settings.json` (event hooks; `N8N_EVENTS_URL` is an env placeholder,
  no secret committed), `.github/ISSUE_TEMPLATE/agent-task.md`.
- CI hardened (earns future Tier 0 trust):
  - Added ESLint 9 flat config + typescript-eslint; `npm run lint`.
  - Type-checking now covers `test/` too (base `tsconfig.json` includes src+test;
    `tsconfig.build.json` emits from src only).
  - Added V8 coverage with a **100% line/branch/function/statement floor** in
    `vitest.config.ts`. Added `test/index.test.ts` to exercise the public API
    barrel honestly (no file exclusions). Current coverage: 100%, 9/9 tests.
  - CI workflow now runs: install → **lint** → typecheck → build → test+coverage.
- Guardrails SOP drafted at `docs/GUARDRAILS-SOP.md` (awaiting sign-off).
- Supabase setup steps staged at `docs/supabase-setup.md` (paste-ready).
- Note: `npm audit` reports vulnerabilities in dev-only transitive deps
  (vitest/eslint toolchain); not shipped, tracked not blocking.
- Repo transferred `sanchexm/pilot-app` -> `savageglobalmarketing/pilot-app`
  (D1). Git remote + README badge updated. CI green post-transfer on `main`.
- Workflow labels created on the org repo: `agent-ready`, `agent-task`,
  `agent-working`, `needs-spec`, `queued` (used by n8n W1).
- Pipeline smoke test: branch `task-day1-smoke` -> PR #1 -> full hardened CI
  (lint -> typecheck -> build -> test+coverage) **green**. Left open as the
  first Tier-1 human-approval rehearsal (merge is the human's call).

### Day 1 exit-criteria status
| Criterion | Status |
|---|---|
| SOP signed off | 🟡 Drafted (`docs/GUARDRAILS-SOP.md`), awaiting Santiago's sign-off |
| Schema live | 🟡 Staged paste-ready (`docs/supabase-setup.md`); needs Supabase project (user) |
| Trivial task on a branch, CI passing | 🟢 Done — PR #1 green |
| Branch protection on `main` | 🟢 Live — ruleset requires `build-and-test` (DEV-1 resolved via public repo) |
| CI runs tests on every PR | 🟢 Confirmed on PR #1 |

---

## Day 2 (2026-07-16) — Pod Launch

### Decisions
- **D5 — SOP sign-off:** Santiago signed off the guardrails SOP in-session
  (explicit approval to run the pod under the caps/tiers). Recorded in
  `docs/GUARDRAILS-SOP.md`.
- **D6 — Pod execution model for the pilot week:** Day 3's n8n event bus is not
  built yet, so the pod runs *inside this Claude Code session*: implementation
  agents (Sonnet-class) each in an isolated git worktree, reviewer agents
  (Opus-class) posting a `VERDICT` PR comment. This mirrors the plan's §9
  pipeline minus the automated event bus. Model routing follows the SOP:
  Sonnet for implementation, Opus for review.
- **D7 — Proportionate choreography:** For these small, independent utility
  tasks the pod ran as implementer → reviewer per task (QA folded into the
  implementer's mandatory green-gate run + the reviewer's test-meaningfulness
  check) rather than spinning all five roles per card. Rationale: the SOP's
  cost-discipline/model-routing guardrail discourages spending Opus turns on
  trivial orchestration. Full lead-decomposition choreography kicks in for
  multi-file tasks (e.g. #7, which touches shared `math.ts`).

### Deviations
- **DEV-2 (minor): Agent-tool built-in worktree isolation unavailable.** The
  harness flagged the working dir as "not a git repository" (it was created
  after `git init` mid-session), so `isolation: worktree` failed. Worked around
  by creating git worktrees manually and pinning each agent to its own worktree
  path. No guardrail impact.
- Note: the `.claude/settings.json` `rm -rf` deny rule fired once during setup
  (blocked a cleanup command) — guardrail working as intended; used a
  non-destructive path instead.

### Work completed
- Six task cards created as GitHub issues #3–#8 (2 Tier 0, 4 Tier 1), each
  following the template; titles/tiers/goals verified aligned.
- First pod pass on the two recommended independent Tier-1 cards:
  - **#5 clamp → PR #9**: `src/clamp.ts` + tests; gate green, 100% coverage,
    16 tests. Reviewer verdict **ESCALATE** (clean Tier 1 → human approval).
  - **#6 truncate → PR #10**: `src/truncate.ts` + tests; gate green, 100%
    coverage, 17 tests. Documented behavior for `maxLength < suffix.length`
    (returns the suffix sliced to `maxLength`). Reviewer verdict **ESCALATE**.
- Worktrees cleaned up; branches `task-5-clamp` / `task-6-truncate` remain on
  origin behind their PRs.

### Day 2 exit-criteria status
| Criterion | Status |
|---|---|
| ≥2 tasks reach a reviewable PR with tests passing | 🟢 Done — PRs #9 and #10, both CI-green, both reviewed ESCALATE |
| Agent configs calibrated | 🟢 No misses this pass — both agents honored scope, conventions, and the coverage floor on the first attempt |

### Awaiting human (before Day 3)
- Your approval (merge) of PRs #9 and #10 — the first real Tier-1 approvals.
- Supabase project creation (needed for Day 3 orchestration; schema staged).

---

## Day 3 (2026-07-17) — Orchestration Layer

### Work completed
- **Supabase live:** schema applied (6 tables, `pod_spend_today` view, trigger,
  RLS), Realtime enabled on agents/tasks/approvals via the `supabase_realtime`
  publication, pod row seeded. Credentials live only in the session-local
  `scratchpad/supabase.env` (never committed).
- **DB-side logic as Postgres functions** (keeps n8n workflows thin + atomic):
  `sgm_ingest_event` (W2), `sgm_dispatch_task` (W1), `sgm_pr_sync` (W3). Each
  unit-tested via psql before wiring.
- **n8n credential:** `SGM Supabase` (Supabase API) created by user — chosen over
  a Postgres credential to avoid the pooler self-signed-cert TLS error.
- **W2 — Agent Event Ingest** (`wfuXJqcU6wCe2r1x`, published): webhook
  `POST /agent-events` → validate `X-SGM-Token` → `/rpc/sgm_ingest_event`.
  Verified: bad token → 401; heartbeat → event+agent+cost_log; approval_requested
  → event+approval(24h)+task awaiting_approval.
- **W1 — Task Dispatch** (`Hdjol0xsnzBFoBB1`, published): GitHub `issues` webhook
  → IF labeled `agent-ready` → `/rpc/sgm_dispatch_task` (validates card, checks
  pause+daily cap, parses tier/budget, creates task, emits task_started).
- **W3 — CI/PR Sync** (`ZwU3xGHVkZTP7b3m`, published): GitHub `pull_request`+
  `check_suite` webhooks → `/rpc/sgm_pr_sync` (branch `task-<issue>` → task;
  agent_review on PR open, tests_passed/failed on CI, merged/failed on close).
- **GitHub webhooks installed** (user-approved): issues → W1; pull_request +
  check_suite → W3.

### End-to-end proof (exit criterion)
Labeled issue #7 `agent-ready` → W1 created the task (`in_progress`, tier 1,
budget parsed). Pod implemented #7 → PR #12 → W3 flipped the task to
`agent_review` with the PR URL; CI green → `tests_passed`. Full Supabase event
trail: task_started → pr_opened → tests_passed. Live status from dispatch to PR,
no manual DB writes.

### Bugs found & fixed during wiring
- **DEV-3:** n8n `githubTrigger` nests the GitHub payload under `$json.body`;
  initial expressions used `$json.*` → IF fell through / fields undefined. Fixed
  all field paths to `$json.body.*`.
- **DEV-4:** PostgREST maps top-level JSON body keys to function args. W1/W3 sent
  fields un-wrapped → `PGRST202 function not found`. Fixed by wrapping the RPC
  body as `{ p: {...} }` (matching the `p jsonb` signature; W2 already did this).

### Hardening items (Phase 2, logged not blocking)
- Move the W2 `X-SGM-Token` from the IF node into a Header Auth credential (out
  of workflow JSON).
- Supabase DB connection currently uses the Session pooler; DDL was run over it
  fine. If a Postgres credential is ever needed in n8n, use CA-verified SSL.
- n8n MCP can't bind predefined credential types (supabaseApi) to HTTP Request
  nodes; those were bound once in the UI. Documented for future workflows.

### Day 3 exit-criteria status
| Criterion | Status |
|---|---|
| n8n W1, W2, W3 built + wired | 🟢 Done, all three published |
| GitHub + Claude Code hooks wired to the bus | 🟢 GitHub webhooks live; W2 webhook URL saved as N8N_EVENTS_URL for hooks |
| A task dispatched via n8n shows correct live status start→PR | 🟢 Proven with issue #7 → PR #12 |

---

## Day 4 (2026-07-17) — Mission Control, part 1

### Decisions
- **D8 — Slack → Google Chat:** SGM doesn't use Slack; W4 posts to **Google Chat**
  (already used by other SGM workflows) via an Incoming Webhook. Deviation from
  the plan (which named Slack); functionally equivalent.
- **D9 — Dashboard is its own app** (`~/apps/mission-control`, standalone) so it
  doesn't disturb pilot-app's strict library CI. Vite + React + TS + Tailwind v4.
- **D10 — Netlify deferred:** ran the dashboard locally for the Day 4 demo per
  user's choice; Netlify deploy moves to a later step.
- **D11 — Auth for the demo:** RLS allows only authenticated reads, so the
  dashboard requires a Supabase Auth login. The user signed in (Claude does not
  enter passwords).

### Work completed
- **Mission Control dashboard** scaffolded (frontend agent): Supabase JS client,
  auth gate (email+password), Fleet View + Kanban, Realtime hooks on agents/
  tasks, top-bar tiles (active agents, tasks in flight, spend vs cap, pending
  approvals). Build + typecheck + lint clean. Runs at localhost:5173.
- **Live proof:** signed in, watched the board render real Supabase data; changed
  an agent status and moved a task in the DB → Fleet card + Kanban column updated
  **live via Realtime, no refresh**.
- **W4 — Approval Notifier (Google Chat)** (`tP4NVY2t7F6FKZG0`, published):
  webhook `POST /approval-notify`, token-gated, posts a Google Chat card
  (summary, tier, impact, rollback, buttons to Mission Control + the PR).
  Verified standalone (bad token → 401; valid → card posted).
- **W2 → W4 wired:** W2 now branches after ingest — if the RPC created an
  approval, it calls W4. Verified end-to-end: `approval_requested` → approval row
  + Google Chat card.
- Demo data cleaned up afterward; store left with only the real merged task.

### Hardening items (Phase 2, logged not blocking)
- W4's Google Chat webhook URL and the X-SGM-Token are embedded in workflow JSON
  (n8n secret store). Move to n8n credentials.
- In-chat Approve/Reject buttons need a Google Chat *app* with a callback
  endpoint; for now the card links to the dashboard where decisions happen.
- Dashboard not yet deployed (Netlify) or domain-restricted; local-only for now.

### Day 4 exit-criteria status
| Criterion | Status |
|---|---|
| Watch agents work live from a browser | 🟢 Fleet View + Kanban live on Realtime (local) |
| Approval requests appear in chat | 🟢 W4 → Google Chat, proven end-to-end |

---

## Day 5 (2026-07-17) — Mission Control, part 2

### Decisions
- **D12 — Decision auth by user JWT, not a shared secret.** The decisions
  webhook is public, so W5 verifies the caller's Supabase login token via
  `/auth/v1/user` (actor = the verified email). This avoids embedding a
  guardrail token in browser JS (which would let anyone approve/merge). Took the
  longer path per the non-negotiable-guardrails rule.
- **D13 — Controls via authenticated RPC.** Pause/resume goes straight from the
  dashboard through `sgm_set_pod_paused` (SECURITY DEFINER, granted to
  authenticated) — no extra workflow needed. Writes still bypass the
  service-role-only RLS only through vetted definer functions.
- **D14 — Cost & Health panel deferred** (plan §11 allows it to slip). Fleet
  View + Approval Queue were the must-haves and are done. Controls (pause/resume)
  shipped; a dedicated Cost/Health page is a fast follow.

### Work completed
- **DB decision logic** as functions: `sgm_decide` (apply approve/reject,
  idempotent, expiry-guarded), `sgm_watchdog` (budget/health enforcement),
  `sgm_set_pod_paused` (controls). Unit-tested via psql.
- **W5 — Decision Executor** (`RzqxFlG4FHkTp6ew`, published): webhook
  `/decisions` → Verify User (JWT) → `sgm_decide` → route: approve = merge PR via
  GitHub API; reject = post feedback comment via GitHub node → Google Chat update.
- **W6 — Budget & Health Watchdog** (`E2usl95EvqaqFF2u`, published): every 15 min
  runs `sgm_watchdog` (pauses pod on hard cap, soft-cap alert once/day, marks
  silent agents error, stops over-budget tasks with a budget_extension approval,
  flags stuck tasks) → posts alerts to Google Chat. Dry-run verified (0 alerts on
  a clean store).
- **Dashboard part 2:** Approval Queue page (pending approvals joined to task,
  Realtime, Approve / Reject-with-feedback, keyboard shortcuts) + Pod Controls
  (status + pause/resume) in the header. Build/typecheck/lint clean; 26 dashboard
  tests added and passing.

### End-to-end proof (exit criterion)
Using a real backlog task (#8 capitalize, PR #15), both loops driven from the
dashboard by the signed-in user (actor recorded as santiago@savageglobalent.com):
- **Reject:** feedback posted to PR #15 → task → in_progress → pod agent revised
  (hyphenated-word handling + 4 tests, CI green) → queue cleared live.
- **Approve:** PR #15 merged via W5 → W3 set task #8 → merged → Google Chat
  "approved & merged". 5th feature task shipped through the full pipeline.

### Notes / hardening (Phase 2)
- A corrupted Vite HMR state blanked the dashboard mid-build; a clean dev-server
  restart fixed it. Non-issue for a deployed (built) app.
- Merge via W5 requires the PR up-to-date + CI green (branch protection) — the
  demo PR satisfied both before approval.
- Cost & Health dashboard page still to build (deferred, §11).

### Day 5 exit-criteria status
| Criterion | Status |
|---|---|
| Approve works end-to-end from the dashboard | 🟢 PR #15 merged on Approve, task → merged |
| Reject works end-to-end incl. agent revision | 🟢 Feedback → PR → agent revised → CI green |
| Watchdog (W6) built | 🟢 Published; full chaos drills are Day 6 |

---

## Day 6 (2026-07-17) — Integration Hardening / Chaos Pass

### Work completed
- Added approval-expiry enforcement to the watchdog (`sgm_expire_approvals`,
  merged into `sgm_watchdog`): pending approvals past their 24h deadline are
  marked `expired` and alerted.
- Ran the four failure drills against the live guardrails (controlled conditions,
  pod config snapshotted + restored afterward). All passed:

| Drill | Expected | Result |
|---|---|---|
| Kill agent mid-task (silent >30m) | mark error + alert | 🟢 qa → error, "AGENT SILENT" alert |
| Task exceeds budget | stop + budget_extension approval | 🟢 task → awaiting_approval + approval + alert |
| Dispatch while over daily cap | block | 🟢 `{ok:false, reason:"daily cap reached"}` |
| Daily soft cap reached | alert, stay active | 🟢 "SOFT CAP" alert, pod active |
| Approval past 24h | mark expired + alert | 🟢 decision → expired + alert |
| Hard cap (kill switch) | pause pod + block dispatch | 🟢 pod → paused + alert; dispatch `{ok:false,"pod paused"}` |

- **Live alert delivery confirmed:** executed W6 in production (exec 11347) with a
  freshly-silent agent → it marked the agent `error` AND posted the alert to
  Google Chat (message id returned). Full detect → enforce → notify path works.
- Alert-noise control: soft-cap alerts de-dupe to once/day/pod (checked against
  today's `budget_alert` events) so a lingering soft breach doesn't spam.
- All drill artifacts cleaned; pod restored (active, $50/$100); watchdog dry-run
  quiet.

### Notes
- Drills were exercised at the enforcement layer (the `sgm_watchdog` /
  `sgm_dispatch_task` functions W6/W1 call) plus one full W6 production run for
  end-to-end alert delivery. This is faithful because the workflows are thin
  wrappers over those functions.

### Day 6 exit-criteria status
| Criterion | Status |
|---|---|
| All four failure drills produce correct alert/block behavior | 🟢 All four (+ kill switch) verified |
| Alert noise tightened | 🟢 Soft-cap de-duped once/day |
