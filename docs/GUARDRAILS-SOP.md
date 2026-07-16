# Guardrails SOP — SGM Agent Dev Team (Phase 1)

**Status: SIGNED OFF by Santiago (santiago@savageglobalent.com), 2026-07-16.**
This is the safety system. It is enforced in config + n8n, not by trust. One page
on purpose. Source: plan §6.

## Autonomy tiers — what agents may do without a human

| Tier | Scope | Gate to merge |
|---|---|---|
| **0** | Internal refactors, test additions, docs, dependency **patch** bumps | Auto-merge **only if** CI green **and** Reviewer verdict = APPROVE |
| **1** | New features, UI changes, API changes | Human approval required (Mission Control) |
| **2** | Auth, payments, data deletion, production deploys, client-facing releases | Human approval **+ rollback plan attached** |

**Phase 1 reality:** Branch protection on `main` is now **live** (ruleset
requires the `build-and-test` check, blocks force-push/deletion). Tier 0
auto-merge still stays **OFF** until the CI coverage floor has proven itself
over several real merges. Until then **everything runs Tier 1** (human approves
every merge).

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
  pushes to `main` directly. *(LIVE — ruleset `main-protection`.)*
- **Kill switch:** `pods.status = 'paused'`. n8n checks it before every
  dispatch; Mission Control has the button.

## Approvals
- Every approval has a **24h expiry**. None are valid indefinitely.
- Rejections require a feedback line; it routes back to the agent (W5) for a
  revision. All decisions are logged to `events` with actor + timestamp.

## Resolved items
- **DEV-1 (branch protection):** Resolved by making `pilot-app` **public** (free
  plans can protect public repos). Ruleset `main-protection` now enforces the
  `build-and-test` check on `main`. Repo contains no secrets or client data.

---
Sign-off: Santiago (santiago@savageglobalent.com)  Date: 2026-07-16
(Recorded from explicit in-session approval to run the pod under these caps/tiers.)
