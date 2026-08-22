---
name: llm-pipelines
description: "LLM batch-processing and DSPy pipeline engineering. Actions: build classifier, convert prompt to dspy, batch classify, judge outputs, register prompt model, monitor LLM pipeline, debug batch job, fix enrichment DAG, evaluate labels, correct labels. Topics: DSPy module, LLM-as-judge, batch classification, rule-based prefilter, prompt versioning, MLflow prompt/model registry, candidate alias, structured output, JSON schema output, retry/timeout for LLM APIs, rate limit, token cost, idempotent result writes, warehouse writeback, label correction, multilingual text, language-violation rules, hallucinated fields. Symptoms: batch job fails midway, results missing from table, LLM API timeout, empty/malformed JSON output, model too strict on non-native language, judge disagrees with labels, cost blowup, duplicate result rows, run not reproducible."
---
# LLM-Pipelines — Batch LLM & DSPy Pipeline Engineering

The skill for production pipelines where an LLM is a processing step: classification, enrichment, moderation, extraction, judging. Encodes the architecture that survived repeated iterations (rules-first → LLM second → idempotent writeback) and the failure modes of batch LLM jobs (mid-run crashes, malformed output, silent missing rows, cost blowups).

## When to Apply

### Must Use

- Building or reviewing any pipeline where an LLM classifies, enriches, moderates, or extracts data in batch
- Converting a raw prompt into a DSPy module (or any structured prompt-program)
- Registering / loading a prompt-based model in MLflow (aliases like `@candidate`, `@production`)
- Debugging a batch LLM job: timeouts, missing rows, malformed output, cost explosions
- Building an LLM-as-judge review flow for labels or model outputs
- Writing an Airflow DAG whose tasks call an LLM API

### Recommended

- Choosing between a rule, a small classifier, and an LLM for a processing step
- Estimating cost/latency before committing to a full-data run
- Designing human review of LLM decisions (sample audits, correction writebacks)

### Skip

- Training/fine-tuning neural models (use ml-experiments)
- Serving latency-critical online inference (use model-serving)
- Plain ETL with no LLM step (use data-pipelines)

## Reference Architecture (rules first, LLM second, idempotent writes)

```
source table ──► fetch candidates (only unprocessed rows)
                     │
                     ▼
             rule-based prefilter          ← cheap, deterministic, auditable
             (regex, lookups, thresholds)     handles the easy majority
                     │ remaining rows
                     ▼
             LLM step (DSPy module)        ← batched, retried, cost-capped
                     │
                     ▼
             validate structured output    ← schema check EVERY row
                     │
                     ▼
             idempotent writeback          ← keyed by source id + model version
             (warehouse table)                re-runs never duplicate rows
```

**Rules:**
1. **Rules before LLM.** Every row the rules can decide is money and latency saved, and the rule layer is where domain corrections land first. Keep rules in code/config, not inside the prompt.
2. **Fetch only unprocessed rows.** The candidate query must anti-join the results table (`WHERE id NOT IN (SELECT id FROM results WHERE model_version = ...)`) so re-running after a crash resumes instead of reprocessing.
3. **Write results keyed by (source_id, model_version, prompt_version).** New prompt = new version, old results stay for comparison.
4. **Checkpoint per batch, not per run.** A job that dies at row 90k must keep the first 90k results. Insert per batch; never accumulate everything in memory for one final insert.
5. **Every run logs: model name, prompt/module version, batch size, row counts (in / rules-decided / LLM-decided / failed), token usage, and wall time.**

## Structured Output Discipline

| Rule | Why | How |
|---|---|---|
| Force a closed label set | "Unknown/Not sure" answers poison downstream tables | Enumerate labels in the signature; validate output against the enum; on violation → retry once, then quarantine row |
| Validate JSON per row, not per batch | One malformed row silently drops the batch | Parse each row; failures go to a `failed_rows` sink with the raw response |
| Never let the model invent fields or facts | Hallucinated attributes corrupt the warehouse | Output schema fixed; extra keys dropped; missing keys → row fails |
| Keep reason codes alongside decisions | Auditing "why was this rejected" is the #1 human review question | Output `{decision, reason_code, reason}` — short code enum + free-text reason |
| Language rules must allow legitimate code-switching | Users of non-Latin-script languages legitimately mix in English brand/model names ("iphone", "hd") | Never reject on "contains foreign script" alone; require the violation to be structural, or route to LLM judgment |

## DSPy Module Pattern

```python
import dspy

class ClassifyItem(dspy.Signature):
    """Classify a record into exactly one category from the closed set."""
    text: str = dspy.InputField()
    category: str = dspy.OutputField(desc="one of: SMALL, MEDIUM, LARGE, XL")
    reason_code: str = dspy.OutputField(desc="one of: SIZE_KEYWORD, WEIGHT, DEFAULT")
    reason: str = dspy.OutputField(desc="one short sentence")

module = dspy.Predict(ClassifyItem)   # or ChainOfThought when reasoning helps accuracy

# Configuration comes from env, NEVER hardcoded:
#   model name, api base, api key, MLflow tracking URI
lm = dspy.LM(model=os.environ["LLM_MODEL"], api_base=os.environ["LLM_API_BASE"], ...)
```

**Conversions from raw prompts:** move the instruction into the Signature docstring, each output constraint into an OutputField desc, and the label list into a validated enum. The prompt text stops being a copy-pasted blob and becomes a versioned program.

**MLflow registration:** log the DSPy module (or prompt bundle) as an MLflow model with `mlflow.dspy.log_model` (or pyfunc wrapping it), register under a name, and promote via alias (`@candidate` → `@production`). Batch jobs load `models:/<name>@<alias>` — never a hardcoded run id. Any companion files the module needs at load time (label maps, category CSVs) must be bundled as model artifacts, not read from repo paths.

## Batch Job Operational Rules

| Symptom | Likely cause | Fix |
|---|---|---|
| Job "succeeded" but table has fewer rows than `--limit` | Per-row failures swallowed; or writeback conditional skipped | Log in/out row counts every batch; assert `decided + failed == fetched` at end |
| Repeated DAG failures on LLM task | No timeout/retry around API; provider transient errors kill the task | Per-request timeout + bounded retries with backoff; task-level `retries>=2`; defer transient failures to next run instead of failing the DAG |
| Cost blowup on full run | No sample-first estimate; retries multiply tokens | Run on a 100–1000 row sample first; extrapolate cost; set a hard budget guard that aborts the run |
| Duplicate rows after re-run | Append-only writeback with no key | Idempotent write keyed by (source_id, model_version); or ReplacingMergeTree/upsert |
| Results differ run-to-run | Temperature > 0; prompt version untracked | temperature=0 for classification; log prompt/module version with every row |
| Human finds systematic label errors | No audit loop | Sample-audit flow: export disagreements/low-confidence rows to CSV → human or judge-LLM review → corrections written back via keyed UPDATE/insert, never manual edits without a record |

## LLM-as-Judge Review Flow

For auditing labels or another model's outputs:

1. Sample deliberately: top-traffic items, known failure examples, random tail — not uniform random only.
2. Judge prompt outputs `{verdict: agree|disagree, suggested_label, reason}` — force it to commit to a label, not just criticize.
3. Disagreements go to a CSV/table for human spot-check before any correction is applied.
4. Corrections are applied as data (keyed writeback into the results/label table), and fed back as few-shot examples or rules — the same mistake class should not need judging twice.
5. Track judge agreement rate over time; a sudden drop means the source model, the data, or the judge prompt changed.

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "batch missing rows"
#       python scripts/search.py "dspy signature"
#       python scripts/search.py "judge labels"
```
