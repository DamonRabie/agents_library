---
name: data-pipelines
description: "Design, debug, and verify Airflow or PySpark pipelines, including DAG scheduling, task-state semantics, idempotency, backfills, log triage, runtime sinks, timestamp/version behavior, Spark sizing, and pipeline configuration. Use for DAG files, task logs, scheduler failures, incorrect writes, or pipeline performance work."
---
# Data-Pipelines — Airflow & PySpark Engineering

Complete guide for designing, testing, and maintaining Airflow DAGs and PySpark jobs in the ClickHouse medallion warehouse context. Addresses the recurring pain patterns: schedule changes, DAG renames, sync mistakes, and idempotency failures.

## When to Apply

### Must Use

- Writing or reviewing any `dag_*.py` file or `spark_applications/*.py`
- Adding or changing a schedule, catchup setting, or retry config
- Planning or executing a backfill (including week-by-week chunked backfills)
- Writing or editing ClickHouse job YAMLs or Spark table description YAMLs
- Debugging a DAG import error, task failure, or SLA miss
- Changing any stage → prod promotion path (review repo → production repo)

### Recommended

- Reviewing pipeline performance (Spark job sizing, shuffle optimization)
- Adding a new sensor or cross-DAG dependency
- Designing a new medallion pipeline from scratch

### Skip

- SQL query logic inside the job (use data-warehouse for that)
- ML training pipelines (use ml-experiments)
- Infrastructure for the Airflow cluster itself (use ci-deploy)

## Fast Diagnostic Path

Use this path when the user pastes a task log or asks whether a pipeline symptom is serious. Diagnose first; do not change code unless the request includes a fix.

1. Identify the claimed symptom, expected outcome, run/task state, and affected side effect. A warning line is not automatically the failure.
2. Find the earliest causal exception or contract violation, then follow later errors as consequences. Preserve the full traceback and task-state evidence during analysis, but do not copy sensitive log content into repository files.
3. Trace the deployed code path and effective runtime configuration to the actual source and sink. Do not infer a database, index, table, or service endpoint from a resource name alone.
4. Separate code defects from dependency, capacity, network, permission, and scheduler/executor failures before editing.
5. Reproduce the smallest safe slice: DAG parse, one transform, one bounded input, or a read-only connectivity probe. Avoid rerunning a full production batch to answer a diagnostic question.
6. Report cause, impact, evidence, and the smallest next action. State explicitly when the evidence proves only a hypothesis.

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Idempotency | CRITICAL | Every task produces same output for same input partition | Append-only without dedup |
| 2 | Catchup/backfill | HIGH | catchup=False for prod DAGs unless intentional | catchup=True on a new DAG floods scheduler |
| 3 | Schedule change safety | HIGH | Use timetable or explicit start_date; test with backfill=False | Changing schedule_interval without checking backfill impact |
| 4 | Retry config | HIGH | retries >= 1; retry_delay reasonable | retries=0 on transient network ops |
| 5 | DAG parse | HIGH | airflow dags list-import-errors after every change | Importing without parse check |
| 6 | Stage/prod sync path | HIGH | Changes in the review repo; CI syncs to production repo | Editing synced copies directly in the production repo |
| 7 | Spark sizing | MEDIUM | Partition count = 2–4× cores; avoid shuffle skew | Single partition for large table; unbounded shuffle |
| 8 | YAML validation | HIGH | yaml.safe_load() + schema check before MR | Invalid YAML discovered only after CI |

## DAG Design Rules

```python
# REQUIRED fields on every production DAG
dag = DAG(
    dag_id="dag_unique_descriptive_name",  # snake_case; no rename without backfill plan
    schedule="0 2 * * *",                  # cron or timetable; NOT timedelta for most cases
    start_date=datetime(2024, 1, 1),       # fixed; never dynamic (datetime.now())
    catchup=False,                         # REQUIRED for new prod DAGs
    max_active_runs=1,                     # prevent overlapping runs on same partition
    retries=2,
    retry_delay=timedelta(minutes=5),
    tags=["bronze", "silver", "gold"],     # layer tag for filtering
)
```

## Idempotency Patterns

**Rule:** Running a task twice on the same logical date partition must produce identical results.

```python
# PATTERN 1: Partition overwrite (ClickHouse ALTER REPLACE PARTITION)
def load_to_clickhouse(ds, **context):
    # Always overwrite the partition for ds
    client.execute(f"ALTER TABLE target REPLACE PARTITION '{ds[:7]}' FROM staging")

# PATTERN 2: ReplacingMergeTree upsert
def upsert_records(records):
    # INSERT is safe to retry — ReplacingMergeTree deduplicates by version
    client.execute("INSERT INTO target VALUES", records)

# ANTI-PATTERN: Append without dedup (breaks idempotency)
def bad_load(ds):
    client.execute("INSERT INTO target SELECT * FROM source WHERE date=%(ds)s", {"ds": ds})
    # Running twice doubles the rows
```

## Schedule Change Safety Checklist

Before changing `schedule_interval` or `schedule` on an existing DAG:

1. **Identify the last successful run date.**
2. **Determine the new first run under the new schedule.** If it's earlier than expected, you'll trigger a backfill flood.
3. **Set `catchup=False`** during the transition period unless explicit backfill is intended.
4. **Communicate to downstream consumers** — downstream DAGs with `ExternalTaskSensor` use explicit schedule times.
5. **Rename the DAG ID only if schedule change is breaking** — renaming creates a new DAG lineage; old runs are lost.

## Spark Job Sizing Rules

| Symptom | Cause | Fix |
|---|---|---|
| OOM on executor | Partition too large | `repartition(n)` where n = data_size_MB / 128 |
| Job slow — few tasks | Too few partitions | `spark.default.parallelism` = 2–4× cores |
| Shuffle skew — one task 100× slower | Key skew in groupBy/join | Salting key or broadcast join for small dimension |
| Executor GC thrash | Large object accumulation | Reduce partition size; use `persist(MEMORY_AND_DISK)` |
| Driver OOM | `collect()` on large result | `coalesce(1).write` instead of collect |

```python
# Recommended session config for ClickHouse warehouse loads
spark = SparkSession.builder \
    .config("spark.sql.shuffle.partitions", "400") \
    .config("spark.sql.adaptive.enabled", "true") \   # AQE: auto-coalesces partitions
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()
```

## YAML Table Description — Quality Checklist

Before opening an MR on the review/staging repo:

```bash
# 1. Parse — must not throw
python -c "import yaml; yaml.safe_load(open('table_desc.yaml'))"

# 2. Required fields present
python -c "
import yaml
d = yaml.safe_load(open('table_desc.yaml'))
required = ['table_name', 'engine', 'order_by', 'columns']
missing = [k for k in required if k not in d]
assert not missing, f'Missing fields: {missing}'
"

# 3. Engine is one of the approved set
# See data-warehouse skill for engine matrix

# 4. Column types use ClickHouse native types (not SQL Server / Postgres syntax)
```

## Debugging Airflow on Kubernetes

When Airflow runs on K8s, task logs land in object storage (S3-style) and pod logs are the ground truth. Debug in this order:

1. **Read the full task log, not the last line.** The surfaced error (often a generic pod failure) is usually downstream of the real one; search the log for the first `ERROR`/traceback, and for Spark jobs read the driver pod section (`spark-kubernetes-driver`).
2. **Classify the failure before touching code:**

| Log signature | Meaning | Fix |
|---|---|---|
| `No more replicas available for rdd_*` then executor loss | Spark executor OOM / eviction — cached partitions lost | Raise executor memory or reduce partition size; check node pressure, not the SQL |
| Task killed near a round wall-time | Pod/executor timeout or eviction | Check `execution_timeout`, cluster autoscaling events; make the task resumable |
| `Connection pool is full, discarding connection` (object storage) | Log/artifact upload chatter | Usually benign WARNING — do not "fix" it; find the real error further down |
| External API timeouts inside a task (LLM/HTTP) | Transient provider failure | Bounded retries with backoff inside the task; `retries>=2` on the task; defer leftovers to next run instead of failing the DAG (see llm-pipelines) |
| DAG stuck queued, no pod created | Scheduler/executor capacity or pod template error | Check scheduler logs and pod events (`kubectl describe pod`), not the DAG code |
| Import error only in cluster | Dependency in local env but not the Airflow image | Pin the dep in the image/requirements; never import from repo paths outside `dags/` |

3. **Quick connectivity probe from inside the cluster:** run a one-off pod or `airflow tasks test` with a minimal task that opens the DB/API connection — don't debug networking through a full DAG run.
4. **DAG self-containment rule:** a DAG file must be runnable from the `dags/` folder alone — no imports from sibling project directories (`scripts/`, `notebooks/`) that don't ship in the deployed image.

## Task State, Sink, and Timestamp Semantics

- **Success is framework state, not control flow.** Returning `False`, `None`, or an empty result can still mark a Python task successful. A failed preflight must raise the framework's failure signal or return a non-zero process status. A deliberate skip is a separate state and must be modeled explicitly.
- **Verify the DAG outcome, not only the log text.** Check the task state, downstream trigger rules, and final DAG-run state for both the failing and passing cases.
- **Name timestamp roles.** Event time, source update time, processing time, and dedup/version time are different contracts. Do not reuse one because it is convenient. Generate processing/version time at the intended write boundary, make timezone conversion explicit, and verify the stored value after the write.
- **Resolve the effective sink.** Trace configuration loading and client construction to identify the runtime destination and logical database/index. A local default, service name, or sample file is not proof of the deployed sink.
- **Count every terminal path.** For batch work, assert that written, deferred, skipped, quarantined, and failed counts reconcile to fetched input. A task can be green while silently dropping rows.

## Shared-Table Watermark & Scheduling Traps

- **Watermark race:** when several independent jobs fill one source table and a downstream incremental job uses `max(timestamp)` as its watermark, a fast source can advance the watermark past rows a slow source hasn't landed yet — those rows are silently skipped forever. Fix: per-source watermarks (min over sources), or a lag buffer (`max(ts) - INTERVAL safety`), or gate the downstream job on all upstream completions.
- **Stagger same-interval jobs:** many jobs on `*/15 * * * *` all fire at :00/:15/:30/:45 and stampede the warehouse. Derive a per-job minute offset (e.g., stable hash of dag_id modulo interval) instead of hand-editing crons.
- **One heavy job at a time:** treat warehouse-heavy or GPU-heavy jobs as a capacity pool of 1 — enforce with Airflow pools rather than hoping schedules don't collide.

## Pipeline Testing Patterns

```python
# Unit test a transform function (no Spark needed)
def test_session_metrics_transform():
    input_rows = [{"user_id": 1, "event": "view", "ts": "2024-01-01"}]
    result = apply_session_logic(input_rows)
    assert result[0]["session_id"] is not None

# Dry-run DAG parse (run in CI)
from airflow.models import DagBag
def test_dag_loads():
    db = DagBag(dag_folder="dags/", include_examples=False)
    assert len(db.import_errors) == 0, db.import_errors
```

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "catchup backfill"
#       python scripts/search.py "Spark OOM partition"
#       python scripts/search.py "YAML table description"
```
