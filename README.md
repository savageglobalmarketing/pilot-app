# Pilot App

[![CI](https://github.com/savageglobalmarketing/pilot-app/actions/workflows/ci.yml/badge.svg)](https://github.com/savageglobalmarketing/pilot-app/actions/workflows/ci.yml)

A minimalist Node + TypeScript app used to validate the full path from code to a
CI pass/fail signal: **typecheck -> build -> test**.

## What's inside

A tiny utility library so the test suite exercises real logic:

- `slugify(text)` - convert text to a URL-safe slug
- `sum(numbers)` - total a list of numbers

## Usage

```ts
import { slugify } from "./src/slugify.js";
import { sum } from "./src/math.js";

slugify("Q3 Marketing Plan (Draft)"); // "q3-marketing-plan-draft"
sum([10, 20, 30]); // 60
```

## Setup

```bash
npm install
```

## Commands

| Command             | What it does                          |
| ------------------- | ------------------------------------- |
| `npm run typecheck` | Type-check with `tsc --noEmit`        |
| `npm run build`     | Compile TypeScript to `dist/`         |
| `npm test`          | Run the Vitest suite (exit code 0/1)  |

## CI

`.github/workflows/ci.yml` runs on every push and pull request:
install -> typecheck -> build -> test. Any failing step turns the run red.

### Try flipping it red

Change an expected value in a test (e.g. in `test/math.test.ts`) and run
`npm test`. The suite fails with a non-zero exit code, and CI would report a
red run. Revert to return to green.
