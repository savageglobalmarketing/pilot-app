# Guardrails SOP — SGM Agent Dev Team (Phase 1)

**Status: DRAFT — awaiting sign-off from Santiago.**
This is the safety system. It is enforced in config + n8n, not by trust. One page
on purpose. Source: plan §6.

## Autonomy tiers — what agents may do without a human

| Tier | Scope | Gate to merge |
|---|---|---|
| **0** | Internal refactors, test additions, docs, dependency **patch** bumps | Auto-merge **only if** CI green **and** Reviewer verdict = APPROVE |
| **1** | New features, UI changes, API changes | Human approval required (Mission Control) |
| **2** | Auth, payments, data deletion, production deploys, client-facing releases | Human approval **+ rollback plan attached** |

**Phase 1 reality:** Tier 0 auto-merge stays **OFF** until (a) branch protection
on `main` is live and (b) the CI coverage floor has proven itself over several
merges. Until then **everything runs Tier 1** (human approves every merge).

## Hard limits (non-negotiable)

- **Turn budget:** 25 planning-execution cycles per session. At the limit the
  agent stops and files an ESCALATE. It never loops indefinitely.
- **Spend caps:**
  - **$10** default per task (override only on the task card).
  - **$50/day soft cap** per pod → Slack alert to `#mission-control`.
  - **$100/day hard cap** per pod → n8n sets pod `paused`, dispatch stops.
  - Monthly ceiling requires an explicit written extension.
- **Model routing (biggest cost lever):** Haiku-class = triage/formatting;
  Sonnet-class = implementation (backend/frontend/qa); Opus-class = planning &
  review only (lead, reviewer).
- **Tool restrictions:** allowlisted tools per agent. **No agent holds deploy
  credentials.** Deploys run through GitHub Actions, triggered only by an
  approved row in the `approvals` table.
- **Branch protection:** `main` requires CI green + the approval gate. No agent
  pushes to `main` directly. *(Blocked on current free plan — see below.)*
- **Kill switch:** `pods.status = 'paused'`. n8n checks it before every
  dispatch; Mission Control has the button.

## Approvals
- Every approval has a **24h expiry**. None are valid indefinitely.
- Rejections require a feedback line; it routes back to the agent (W5) for a
  revision. All decisions are logged to `events` with actor + timestamp.

## Open item blocking full enforcement
- **Branch protection is unavailable** on the current GitHub plan for a private
  repo (free account/org → needs Team/Enterprise, or make the repo public).
  Until resolved: Tier 0 auto-merge stays off; human approves every merge; this
  is recorded as deviation DEV-1 in `SPRINT_LOG.md`.

---
Sign-off: ____________________  Date: __________
