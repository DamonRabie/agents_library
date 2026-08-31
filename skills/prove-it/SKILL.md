---
name: prove-it
description: "Prove that code, data, pipeline, model, UI, configuration, or deployment changes satisfy their acceptance criteria. Use for verification, regression testing, browser or API checks, data assertions, and any completion claim that needs evidence at the boundary where the behavior can fail."
---
# Prove-It — Verification Intelligence

The single skill for proving that a change works — before it merges, before it deploys, before the problem is discovered in production. Most commit-log thrash (CI loops, ONNX debug chains, SQL null bugs) is verification failure. This skill defines what "verified" must mean per change type and encodes the evidence hierarchy.

## When to Apply

### Must Use

- Before marking any task, issue, or acceptance criterion as complete
- Before pushing to CI (especially after any config/YAML/Dockerfile change)
- Before declaring a SQL query, pipeline job, or migration correct
- Before calling an ML training run, export, or model registration done
- Translating "acceptance criteria" into a concrete executable check
- After any bug fix — to prove the bug is gone and no regression introduced
- Any time the words: verify, confirm, test, check, validate, prove, evidence

### Recommended

- After a refactor that "shouldn't change behavior"
- Before a PR/MR that an agent authored
- When a deploy script changes
- After a database migration runs

### Skip

- Pure documentation or comment-only changes
- Style/format-only changes with zero logic
- Adding a new environment variable that isn't wired to anything yet

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Failure-boundary evidence | CRITICAL | Prove behavior at the boundary where it failed | A green unit suite for a broken user flow |
| 2 | Minimum evidence per change | CRITICAL | See evidence-levels.csv for required floor | Skipping to manual QA when automatable |
| 3 | Acceptance criteria translation | HIGH | Every AC → one concrete executable check | Vague ACs ("it should work") left untranslated |
| 4 | Root-cause contract | HIGH | Reproduce failure; fix authoritative producer; rerun same path | Cleaning a bad artifact without fixing its writer |
| 5 | CI local-first | HIGH | Reproduce every CI step locally before push | Push → watch fail → patch → repeat |
| 6 | Data/SQL verification | HIGH | Row count delta, checksum, before/after sample | Eyeballing one row and calling it done |
| 7 | ML/model verification | HIGH | Metric bounds, numerical parity check, smoke inference | Registering without forward-pass verification |
| 8 | Regression scope | MEDIUM | Run focused and broader checks for touched boundaries | Only running the new test |
| 9 | Playwright/browser | MEDIUM | Assert state, navigation, console/network health; screenshot second | Treating a screenshot as interaction proof |

## Evidence Must Match the Failure Boundary

Evidence types answer different questions; they are not a universal ranking:

- **Unit tests** prove local logic and invariants.
- **Integration tests** prove wiring across a real persistence, file, API, or process boundary.
- **End-to-end/browser tests** prove a user-visible flow, including routing and client/server interaction.
- **API and runtime probes** prove the deployed or running interface responds with the expected status and shape.
- **SQL assertions** prove data grain, counts, uniqueness, time boundaries, and write effects.
- **Inference smokes** prove a packaged model loads and produces bounded output.
- **Screenshots** prove appearance at one moment; they do not prove interaction, persistence, or absence of console errors.
- **Compile, lint, and type checks** prove structural validity, not behavioral correctness.

**Rule:** The primary proof must cross the boundary where the reported failure lived. Add the cheapest durable lower-level regression check that would catch the same cause again.

## Acceptance Criteria Translation Protocol

For every AC:
1. Restate it as a falsifiable condition: _"Given X, when Y, then Z must be measurably true."_
2. Pick evidence at the failure boundary plus a durable regression check where practical.
3. Write or invoke the check. Record the output.
4. If it passes: mark AC done. If it fails: fix first, do not merge.

## Bug-Fix Contract

1. Reproduce the original report before editing, or record why reproduction is impossible.
2. Trace the behavior from the user-facing entry point to the authoritative producer and final side effect. For a generated file, wrong database row, or stale UI value, deleting or relabeling the symptom is not a fix.
3. Capture a failing test, assertion, or minimal probe when feasible. If a permanent automated check is disproportionate, preserve a deterministic reproduction command and state the limitation.
4. Apply the smallest fix at the authoritative layer, then rerun the original path without manual cleanup that hides the defect.
5. Run focused regression checks and one broader check across every touched boundary. A green suite is evidence only for behavior it actually exercises.

## Quick Reference — Verification by Change Type

Use `scripts/search.py "<change-type>"` to get the full checklist. Summary:

**Code change / bug fix:** reproduce at the failing boundary, add a durable regression check when practical, then run the regression suite for touched modules.

**SQL query / view / migration:** dry-parse (no syntax error), row-count delta, null-boundary spot check, sample before/after.

**Pipeline / DAG change:** local dry-run (dag parse), unit test transforms, sample-dataset integration run, verify idempotency (run twice → same output).

**API endpoint:** `make verify` passes, API probe (status + shape), auth/authz edge case covered.

**ML training run:** smoke run first (sampled data + isolated storage), metric bounds check vs baseline, no NaN in loss curve, final-train gated by eval rubric.

**Model export/registration:** exported model ≠ None, numerical parity check (source vs exported forward pass on known input, delta < 1e-4), upload artifact manifest complete.

**Docker/compose change:** `docker build` succeeds, healthcheck passes, `docker compose up` + probe, non-root user confirmed.

**Deploy script change:** run locally against staging first, `make deploy` in dry-run mode, check rollback path.

**Config / env change:** identify all code paths reading the key, test each.

**Dependency upgrade:** run the full automated suite, smoke the highest-risk runtime path, inspect behavior or compatibility changes, and preserve a rollback point. Passing unit tests alone does not prove operational compatibility.

## Data Change Verification Checklist

```sql
-- Before any pipeline/migration run, capture:
SELECT count(*) AS row_count, max(updated_at) AS max_ts FROM target_table;

-- After:
SELECT count(*) AS row_count, max(updated_at) AS max_ts FROM target_table;
-- Delta must match expected insert/update count.

-- Null boundary check:
SELECT count(*) FROM target_table WHERE date_col IS NULL;

-- Sample spot check:
SELECT * FROM target_table WHERE id IN (...known_ids...) LIMIT 10;
```

## Playwright Golden Path Pattern

```python
# Save to artifacts/<feature>_<timestamp>.png
from playwright.sync_api import sync_playwright
import datetime

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:PORT/path")
    # assert key visible elements
    page.wait_for_selector("[data-testid='main-content']")
    page.screenshot(path=f"artifacts/{feature}_{datetime.datetime.now():%Y%m%d_%H%M%S}.png")
    browser.close()
```

For navigation or stateful UI changes, also test direct entry, reload, back/forward behavior, and the inverse interaction that must remain unaffected. Inspect console errors and failed network requests before declaring success.

## Regression Loop

After any fix:
1. Confirm the original failing case now passes.
2. Run the full suite for all modules you touched.
3. If a new test was needed to catch this bug, add it permanently.
4. Check: does this fix need a note in the relevant super skill's data CSV?

## Search

```bash
python scripts/search.py "<change-type or symptom>"
# e.g.: python scripts/search.py "SQL migration"
#       python scripts/search.py "ML model export"
#       python scripts/search.py "browser test"
```
