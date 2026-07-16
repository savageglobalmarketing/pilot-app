# CLAUDE.md — pilot-app

## What this app is
A minimalist Node + TypeScript utility library that serves as the pilot app for
the SGM AI Agent Dev Team sprint. Its job is to exercise the full pipeline
(task card → agent work → review → CI → approval → merge) on real but low-risk
code. It currently exports two pure functions: `slugify(text)` (URL-safe slug)
and `sum(numbers)` (total of a list). Used by the sprint team, not end users.

## Stack
- Node.js 22 (ESM, `"type": "module"`)
- TypeScript 5.5 — `strict`, module/resolution `NodeNext`
- Vitest 2 for tests, with V8 coverage
- ESLint 9 (flat config) + typescript-eslint
- GitHub Actions for CI

## Commands
- Install: `npm ci`
- Dev server: n/a (library — there is no runtime server)
- Tests: `npm test` — runs `vitest run` with coverage. MUST pass before any PR.
- Lint: `npm run lint`
- Typecheck: `npm run typecheck` (type-checks `src` **and** `test`)
- Build: `npm run build` (emits `dist/` from `src` only)

## Conventions
- ESM only. Relative imports use explicit `.js` specifiers (NodeNext), even in
  `.ts` source (e.g. `import { sum } from "./math.js"`).
- One focused pure function per file under `src/`; a matching test file under
  `test/` named `<name>.test.ts`.
- Prefer small, total functions with explicit edge-case handling over cleverness.
- Every change ships with tests. A PR without test coverage for its changes is
  incomplete, and CI enforces a coverage floor (see below).
- Small, focused diffs. One task card = one PR.
- Commit messages: conventional commits (feat:, fix:, chore:, test:, docs:).

## Off-limits — never touch these
- Secrets, `.env` / `.env.*` files, anything under `**/secrets/**`
- CI/deploy config: `.github/workflows/**` (contains the CI gate the whole
  guardrail system depends on). Changes here are Tier 2 and need human approval.
- `.claude/settings.json` hooks and the `permissions.deny` list
- `package-lock.json` integrity — do not hand-edit; change deps via npm only
- Do not disable, skip, or delete existing tests to make a suite pass
- Do not lower the coverage thresholds in `vitest.config.ts` to pass CI
- Do not add new dependencies without flagging it in the PR description
- No billing/auth/payment code exists in this repo; if a task would introduce
  any, that is Tier 2 — ESCALATE.

## Definition of done
1. Acceptance criteria on the task card are met
2. Tests written and passing locally and in CI; coverage floor still met
3. Lint, typecheck, and build all clean
4. PR description: what changed, why, how to verify, rollback note

## Pod protocol
- You are part of a 5-agent pod (lead, backend, frontend, qa, reviewer).
- Work only in your assigned worktree. Never edit files owned by another agent's
  subtask — flag the dependency to the lead instead.
- If blocked, uncertain, or the task exceeds its stated scope: stop and emit an
  ESCALATE rather than guessing.
- Budget discipline: respect the max turns and max spend on the task card.
- No agent may merge to `main` or hold deploy credentials. Merges happen only
  through the approval gate.
