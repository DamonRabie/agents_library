---
name: data-warehouse
description: "Design, debug, and verify ClickHouse analytical warehouses and SQL: engines, grain, deduplication, incremental loads, backfills, query performance, joins, timestamp semantics, timezones, and stage-to-production promotion. Use for warehouse SQL, table/view definitions, or wrong and slow analytical results."
---
# Data-Warehouse — ClickHouse OLAP Engineering

Complete guide for designing, building, and maintaining ClickHouse-based medallion warehouses. Covers engine selection, incremental patterns, backfill playbooks, the SQL quality pre-merge checklist, and query optimization.

## When to Apply

### Must Use

- Designing or reviewing any ClickHouse table (engine selection, ORDER BY, partition key, TTL)
- Writing or reviewing SQL for ClickHouse (queries, views, materialized views, job YAMLs)
- Planning or executing a backfill or data migration
- Stage → prod promotion (review-repo → production-repo sync pattern)
- Diagnosing wrong row counts, dedup failures, slow queries
- Writing any incremental load logic (watermark columns, upserts, partition swaps)

### Recommended

- Reviewing a new Spark table description or ClickHouse job YAML before opening an MR
- Designing medallion layer boundaries (what goes in bronze/silver/gold)
- Adding a new view or materialized view
- Performance investigation on any analytical query

### Skip

- OLTP / transactional database work (use python-backend)
- Airflow DAG structure (use data-pipelines; data-warehouse handles the SQL inside the jobs)
- ML model development (use ml-experiments)

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Pre-merge SQL checklist | CRITICAL | See checklist below; null dates, timezone, typos, join fanout | Shipping SQL without dry-parse |
| 2 | Engine selection | CRITICAL | See engine matrix; FINAL semantics for Replacing | AggregatingMergeTree without -State/-Merge pair |
| 3 | Dedup correctness | HIGH | FINAL on SELECT; dedup key matches version/sign col | Missing FINAL; wrong ORDER BY for dedup |
| 4 | Incremental load safety | HIGH | Watermark columns; idempotent upsert; no full reload | Overwriting entire table on every run |
| 5 | Backfill discipline | HIGH | Week-by-week chunks; scaffold DDL; verify after each chunk | Backfilling entire history in one partition |
| 6 | Stage→prod promotion | HIGH | Promote via review repo CI sync; never edit synced copies | Editing the production repo's synced job YAMLs directly |
| 7 | Query optimization | MEDIUM | PREWHERE before WHERE; projections for heavy aggregations; dictionaries for lookups | Full table scan for low-cardinality filter |
| 8 | Medallion boundaries | MEDIUM | Bronze=raw, Silver=cleaned/joined, Gold=aggregated/serving | Joining raw data in gold layer |

## Pre-Merge SQL Checklist (run before every MR)

```sql
-- 1. DRY PARSE (no syntax error)
-- Use sqlglot or clickhouse-client --dry-run
python -c "import sqlglot; sqlglot.parse(open('query.sql').read(), dialect='clickhouse')"

-- 2. NULL DATE BOUNDARY
SELECT count(*) FROM t WHERE end_date IS NULL;
-- Expected: 0, or handled with COALESCE(end_date, today())

-- 3. TIMEZONE EDGE (ClickHouse stores UTC; Jalali calcs need explicit TZ)
-- Check all toDate()/toDateTime() calls include timezone arg

-- 4. JOIN FANOUT
SELECT count(*) vs count(DISTINCT join_key) -- must match expected multiplier

-- 5. DEDUP KEY COVERAGE
-- For ReplacingMergeTree: ORDER BY cols uniquely identify a logical row

-- 6. TYPO SCAN
-- Read query aloud; check column names against actual schema
-- Use: SELECT * FROM system.columns WHERE table='t' AND name LIKE '%colname%'

-- 7. FINAL CLAUSE (for ReplacingMergeTree SELECT)
SELECT * FROM t FINAL WHERE ...
-- Add FINAL when reading deduplicated data
```

## Engine Selection Matrix

| Use case | Engine | ORDER BY guidance | Notes |
|---|---|---|---|
| Event log / immutable facts | MergeTree | (partition_date, entity_id) | No dedup needed |
| Slowly changing entity (keep latest) | ReplacingMergeTree(version) | (entity_id) | Always SELECT ... FINAL |
| Pre-aggregated metrics (sum/count) | SummingMergeTree | (dimensions...) | Safe for additive metrics; not averages |
| Complex pre-aggregations (avg, percentile) | AggregatingMergeTree | (dimensions...) | Use -State on insert, -Merge on query |
| CDC with deletes (sign +1/-1) | CollapsingMergeTree(sign) | (entity_id) | INSERT pair: +1 new, -1 old |
| CDC with version + sign | VersionedCollapsingMergeTree(sign,ver) | (entity_id) | Safer than Collapsing; version resolves races |
| Cross-shard queries | Distributed | same as underlying | Local table + Distributed view |

## Incremental Load Patterns

```sql
-- Watermark pattern (safe for late-arriving data with buffer)
SELECT *
FROM source_table
WHERE updated_at >= (
    SELECT max(updated_at) - INTERVAL 2 HOUR   -- buffer for late arrivals
    FROM target_table
)

-- Idempotent upsert (ReplacingMergeTree accepts re-inserts; version column resolves)
INSERT INTO target_table SELECT * FROM source_table WHERE ...

-- Partition swap (atomic; use for large backfill chunks)
ALTER TABLE target_table REPLACE PARTITION partition_expr
    FROM staging_table
```

## Timestamp Roles and Freshness

Treat event time, source update time, ingestion time, processing time, and dedup/version time as separate columns unless the data contract explicitly makes them identical.

- Define which clock determines partitions, incremental watermarks, user-visible reporting, and conflict resolution.
- Generate processing or version timestamps at the write boundary when they represent the current write. Do not carry forward a stale source time merely because it has the right type.
- Convert timezones explicitly at system boundaries and compare instants in a canonical zone. Preserve the original source offset only when it is part of the business meaning.
- For model or report datasets, make the as-of cutoff explicit so later facts cannot leak into earlier rows.
- Verify stored minimum/maximum values and a boundary sample after the write; inspecting only the SQL expression does not prove the persisted result.

## Backfill Playbook

**Never backfill entire history in one job.** Always chunk by week/month:

```python
# Week-by-week DAG pattern
from datetime import date, timedelta

START = date(2024, 1, 1)
END   = date.today()

d = START
while d < END:
    week_end = min(d + timedelta(days=7), END)
    run_backfill_job(partition_start=d, partition_end=week_end)
    verify_row_count(partition_start=d, partition_end=week_end)  # never skip
    d = week_end
```

Scaffold DDL for backfill:
```sql
-- Create staging table with same schema
CREATE TABLE target_backfill AS target_table;
-- Load chunk into staging
-- Verify staging row count
-- Swap partition
ALTER TABLE target_table REPLACE PARTITION 'YYYY-MM' FROM target_backfill;
-- Clean up
DROP TABLE target_backfill;
```

## Stage→Prod Promotion Rules

- All ClickHouse job YAMLs, view descriptions, and Spark table descriptions live in the designated review/staging repo (see the project's memory file for which repo that is).
- Changes are reviewed there, merged to `master`, and CI syncs into the production pipeline repo automatically.
- **Never edit the synced copies in the production repo directly** — they will be overwritten on next sync.
- If a production-side DAG needs a table description change, open the MR in the review repo, not the production repo.

## Query Optimization Quick Reference

```sql
-- PREWHERE: runs before WHERE, faster on column-store
SELECT ... FROM t PREWHERE partition_date = '2024-01' WHERE entity_id = 42

-- Aggregate projection (declare at CREATE time)
ALTER TABLE t ADD PROJECTION monthly_rollup (
    SELECT toStartOfMonth(event_date) AS month, sum(revenue), count()
    GROUP BY month
);

-- Dictionary lookup (replaces slow JOIN to dimension table)
SELECT dictGet('product_dict', 'category', product_id) FROM events

-- FINAL avoids double-counting in ReplacingMergeTree
SELECT sum(revenue) FROM transactions FINAL
```

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "ReplacingMergeTree dedup"
#       python scripts/search.py "backfill week partition"
#       python scripts/search.py "null date boundary"
```
