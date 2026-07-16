# Pilot App Design

Date: 2026-07-16

## Goal

One minimal app with a real test suite and a CI pipeline that produces a clear
pass/fail signal. This validates the end-to-end path: code -> typecheck ->
build -> test -> CI red/green.

## Stack

- Node + TypeScript
- Vitest (test runner)
- GitHub Actions (CI)

## Scope

A tiny self-contained utility library so the test suite exercises real logic:

- `slugify(text: string): string` - convert text to a URL-safe slug.
- `sum(numbers: number[]): number` - total a list of numbers.

Both are exported from `src/index.ts`.

## Structure

```
pilot-app/
  src/
    index.ts        # re-exports the public API
    slugify.ts
    math.ts
  test/
    slugify.test.ts
    math.test.ts
  package.json      # scripts: build, typecheck, test
  tsconfig.json
  vitest.config.ts
  .github/workflows/ci.yml
  .gitignore
  README.md
```

## CI Flow (push + pull_request)

1. Checkout
2. `npm ci` (install)
3. `npm run typecheck` (tsc --noEmit)
4. `npm run build` (tsc)
5. `npm test` (vitest run)

Any failing step fails the job. This is the pass/fail signal.

## Testing

- Happy-path and edge-case tests for both functions.
- Tests are deterministic; no network or filesystem dependencies.

## Verification

- Run `npm test` and `npm run build` locally and confirm passing output.
- `git init` and commit the initial working state.
