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
