---
name: prove-it
description: "Verification intelligence. Prove a change works before committing, merging, or deploying. Actions: verify, test, check, validate, confirm, prove, assert, evidence, acceptance criteria, QA, regression. Change types: code change, SQL query, pipeline, API endpoint, ML model, database migration, UI feature, config change, refactor, bug fix, hotfix, deploy, rollback. Tasks: write a test, run tests, check acceptance criteria, validate output, confirm correctness, run smoke test, browser check, click path, screenshot, data validation, row count, checksum, before/after comparison. Symptoms: 'is this correct?', 'did it work?', 'how do I verify?', 'acceptance criteria', 'unit test', 'integration test', 'manual test', 'QA', e2e test, playwright, API probe, SQL assertion, MLflow metric, training validation, deploy smoke."
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
| 1 | Evidence hierarchy | CRITICAL | Unit > integration > e2e > probe > screenshot > "compiles" | Claiming verified because it compiles |
| 2 | Minimum evidence per change | CRITICAL | See evidence-levels.csv for required floor | Skipping to manual QA when automatable |
| 3 | Acceptance criteria translation | HIGH | Every AC → one concrete executable check | Vague ACs ("it should work") left untranslated |
| 4 | CI local-first | HIGH | Reproduce every CI step locally before push | Push → watch fail → patch → repeat |
| 5 | Data/SQL verification | HIGH | Row count delta, checksum, before/after sample | Eyeballing one row and calling it done |
| 6 | ML/model verification | HIGH | Metric bounds, numerical parity check, smoke inference | Registering without forward-pass verification |
| 7 | Regression scope | MEDIUM | Run full suite for touched modules | Only running the new test |
| 8 | Playwright/browser | MEDIUM | Click golden path, assert visible state, artifact screenshot | Manual click without reproducible test |

## Evidence Hierarchy (canonical order, highest to lowest)

1. **Automated unit test** — passes on every run, catches regressions permanently.
2. **Automated integration test** — hits real DB/API/filesystem; slower but proves wiring.
3. **End-to-end / browser test** (Playwright) — proves user-visible flow.
4. **API probe** — `curl`/httpx request that asserts status code + response body shape.
5. **SQL assertion query** — `SELECT COUNT(*), checksum FROM ...` before/after.
6. **Inference smoke** — forward pass through model with known input → expected output range.
7. **Screenshot artifact** — visible proof saved to `artifacts/`, timestamped.
8. **"It compiles / lints clean"** — necessary but not sufficient alone.

**Rule:** Never claim a change is verified at level N if a level < N is achievable within the same session.

## Acceptance Criteria Translation Protocol

For every AC:
1. Restate it as a falsifiable condition: _"Given X, when Y, then Z must be measurably true."_
2. Pick the highest evidence level achievable (see hierarchy above).
3. Write or invoke the check. Record the output.
4. If it passes: mark AC done. If it fails: fix first, do not merge.

## Quick Reference — Verification by Change Type

Use `scripts/search.py "<change-type>"` to get the full checklist. Summary:

**Code change / bug fix:** unit test that would have caught the bug + regression suite for touched modules.

**SQL query / view / migration:** dry-parse (no syntax error), row-count delta, null-boundary spot check, sample before/after.

**Pipeline / DAG change:** local dry-run (dag parse), unit test transforms, sample-dataset integration run, verify idempotency (run twice → same output).

**API endpoint:** `make verify` passes, API probe (status + shape), auth/authz edge case covered.

**ML training run:** smoke run first (sampled data + isolated storage), metric bounds check vs baseline, no NaN in loss curve, final-train gated by eval rubric.

**Model export/registration:** exported model ≠ None, numerical parity check (source vs exported forward pass on known input, delta < 1e-4), upload artifact manifest complete.

**Docker/compose change:** `docker build` succeeds, healthcheck passes, `docker compose up` + probe, non-root user confirmed.

**Deploy script change:** run locally against staging first, `make deploy` in dry-run mode, check rollback path.

**Config / env change:** identify all code paths reading the key, test each.

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
