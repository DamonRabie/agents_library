---
name: ml-experiments
description: "Design, run, debug, and evaluate ML experiments from dataset readiness through tracked comparison and promotion. Use for training data and split design, experiment notebooks, baselines, smoke runs, HPO, reproducibility, MLflow lifecycle, leakage checks, and promotion decisions."
---
# ML-Experiments — Experiment Lifecycle Intelligence

Complete guide for the ML experiment lifecycle from hypothesis to promoted model. Encodes the research-tree workflow, HPO discipline, the training debugging table (common foot-guns), and MLflow hygiene. Every foot-gun here was discovered the hard way — this skill is the permanent record.

## When to Apply

### Must Use

- Planning or running any ML experiment, HPO sweep, or training run
- Debugging training (NaN loss, OOM, bad epoch 1, non-reproducible)
- Logging experiments or artifacts to MLflow
- Deciding whether to promote a trained model
- Building a research tree (multi-variant controlled exploration)
- Writing a smoke test for a training pipeline

### Recommended

- Code-reviewing a training script
- Designing a new model architecture or training objective
- Comparing two approaches before committing to a full run

### Skip

- Model serving/deployment (use model-serving)
- Data warehouse or feature pipeline engineering (use data-warehouse, data-pipelines)
- Non-ML Python services (use python-backend)

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Smoke run first | CRITICAL | Always smoke on sampled data before full run | Launching full training before smoke passes |
| 2 | NaN / Inf in loss | CRITICAL | Monitor first 10 steps; stop on NaN | Ignoring NaN and hoping it recovers |
| 3 | LR warmup correctness | HIGH | Per-batch scheduler; warmup doesn't zero epoch 1 | Per-epoch scheduler causing gradient zeroing |
| 4 | MLflow logging | HIGH | Every run logged; naming convention consistent | Ad-hoc local training with no MLflow record |
| 5 | Reproducibility | HIGH | Fixed seed; document split; run twice to verify | Non-deterministic results per run |
| 6 | Promotion gate | HIGH | Must beat baseline on holdout; eval rubric passed | Promoting without comparison to last registered |
| 7 | Research tree discipline | MEDIUM | One controlled variable per node; no cherry-picking | Changing two things between runs, not knowing which helped |
| 8 | Dataset leakage | HIGH | Verify train/val/test splits are disjoint | Validation samples in training set |
| 9 | Fit-on-train-only | CRITICAL | Every fitted artifact (vocab, scaler, encoder, embedding, threshold) built from train split only | Building vocab or stats on the full dataset |
| 10 | Metric name fidelity | HIGH | Read exact metric names from the training code before querying/reporting | Guessing metric names when analyzing runs |
| 11 | Run lifecycle | HIGH | Every run reaches a terminal status; artifacts verified uploaded | Runs left RUNNING forever; missing artifacts discovered later |

## Data Readiness Gate

Do not start model selection merely because a dataset file exists. Before training:

1. Define the prediction unit, target, horizon, decision point, and point-in-time feature availability.
2. Profile duplicates, missingness, label coverage, time coverage, class balance, and suspicious target proxies. Resolve whether gaps are unknown, zero, not applicable, or data loss.
3. Version the dataset construction logic and record source lineage. Persist the exact split membership or a deterministic split key.
4. Choose a split that matches deployment: time-based for future prediction, group-based when entities repeat, and stratified only when it does not violate time or group boundaries.
5. Establish a trivial or rules-based baseline before adding model complexity. A candidate must beat the baseline on the decision metric and important slices.
6. Keep agent- or model-generated labels provenance-tagged and independently validated. They must not contaminate the locked holdout.

If these conditions are not met, the useful output is a data-quality and labeling plan with executable gates, not a training run.

## Smoke Run Protocol (ALWAYS first)

```python
# Every training pipeline must support a --smoke flag:
# - Use a SMALL sampled dataset (100–1000 rows)
# - Use an ISOLATED storage path (not the production MLflow server)
# - Complete in < 2 minutes
# - Pass all assertions before full run

# Example smoke invocation:
python train.py \
    --smoke \
    --data-sample 0.01 \
    --mlflow-uri "sqlite:///smoke_mlflow.db" \
    --output-dir "/tmp/smoke_output"

# Only after smoke passes:
python train.py \
    --data-path /full/dataset \
    --mlflow-uri "http://production-mlflow:5000" \
    --output-dir "/mnt/artifacts"
```

## Training Debugging Table

| Symptom | Likely cause | Diagnostic | Fix |
|---|---|---|---|
| NaN loss in step 1–10 | LR too high; gradient exploding | Print param norms per step | Lower LR 10x; add gradient clipping |
| NaN loss after epoch 3–5 | Learning rate divergence | Plot LR schedule; check for sudden spike | Add warmup; use LR finder |
| Loss stuck at high value | LR too low; wrong optimizer; label error | Compare to random baseline | Raise LR; check label encoding |
| Epoch 1 loss 100x worse than epoch 2 | Per-epoch LR scheduler zeroing warmup | Print LR at step 0 | Move scheduler.step() to per-batch |
| OOM on GPU | Batch too large; gradient accumulation missing | nvidia-smi; profile memory | Halve batch size; add gradient_accumulation_steps |
| Dataloader bottleneck | num_workers too low; I/O bound | profile GPU utilization < 50% | Increase num_workers; prefetch_factor=2 |
| Non-reproducible results | Random seed not fixed globally | Run twice; compare metric | Set seed in torch, numpy, random, os.environ |
| Validation metric worse than training | Overfitting | Plot train vs val curves | Add regularization; more data augmentation; early stopping |
| Dataset leakage | Shuffle before split | Check ID overlap between splits | Split first, then shuffle each split independently |
| MLflow run not logging | Tracking URI wrong; experiment name mismatch | mlflow.get_tracking_uri() | Set MLFLOW_TRACKING_URI env var before run |

## Research Tree Method

Use a research tree when the modeling direction is uncertain and requires controlled exploration.

**Structure:**
- **Wave**: a set of simultaneous experiments exploring one decision (architecture, objective, data)
- **Node**: one training run with one controlled change from the parent
- **Frontier**: the set of nodes worth deepening (based on metric + cost + signal)
- **Leaf**: a node not worth continuing (too slow, worse metric, high variance)

**Rules:**
1. Change ONE variable per node. If you change two, you can't attribute the improvement.
2. Every node must be a logged MLflow run. The run description IS the node card.
3. Make frontier judgments explicitly — write "promote node N3 because val_ndcg +2.3% over N1; N2 pruned (no improvement)"
4. Don't deepen a weak branch because it's "almost promising" — cut it early.
5. Wave slicing for long work: each wave is a GitHub issue / Airflow DAG run. Gate on wave result before starting next wave.

## HPO Design Rules

```python
# 1. Define search space with budget awareness
search_space = {
    "lr": tune.loguniform(1e-5, 1e-2),        # log scale for LR
    "batch_size": tune.choice([32, 64, 128]),   # discrete
    "dropout": tune.uniform(0.1, 0.5),
}

# 2. Smoke test the search space first (1 trial, minimum steps)
# 3. Start with small budget (10–20 trials); expand if signal found
# 4. Warm-start bounds: if best trial from last run was lr=3e-4,
#    next run's range should include it (don't cut off the known-good region)

# 5. Isolation: each HPO trial writes to its own subdirectory
# NEVER share state between trials
```

## MLflow Hygiene (non-negotiable)

```python
import mlflow

# Naming convention: <project>/<model_type>/<objective>
mlflow.set_experiment("project_name/search_ranker/ndcg_optimization")

with mlflow.start_run(run_name="node_N3_lr3e-4_bs64"):
    # Log ALL params that affect reproducibility
    mlflow.log_params({
        "lr": 3e-4, "batch_size": 64, "seed": 42,
        "dataset_version": "2024-01-15", "model_arch": "two_tower_v2"
    })

    # Log metrics at each epoch
    mlflow.log_metric("val_ndcg", ndcg, step=epoch)

    # Log artifacts (model + anything needed to reproduce)
    mlflow.log_artifact("config.yaml")
    mlflow.pytorch.log_model(model, "model")

    # Set tags for filtering
    mlflow.set_tags({"wave": "wave_3", "status": "frontier", "promoted": "false"})
```

**Invariant:** If you can't find the run in MLflow, the experiment didn't happen.

### Run Lifecycle & Tracker Hygiene (hard rules)

1. **Tracking URI always comes from the environment** (`MLFLOW_TRACKING_URI` / env file). Never fall back to a local `mlruns/` or `sqlite` store in real pipelines — split-brain tracking is how runs "disappear". A local store is acceptable only for smoke runs, and must be isolated (see Smoke Run Protocol).
2. **Exact metric names, always.** Before analyzing, comparing, or reporting runs, read the metric names from the training script (or a documented metric list) and use those strings verbatim. Guessed metric names produce empty queries and wrong reports. When writing analysis docs (whitepapers, progress logs), include the exact metric-name list so later sessions don't re-guess.
3. **Every run ends in a terminal state.** Wrap training in `try/finally` with `mlflow.end_run()`; if a run was killed externally, terminate it explicitly (`MlflowClient().set_terminated(run_id)`). A tracker full of stale RUNNING runs makes real state unreadable.
4. **Verify artifact upload completeness** after the run: list run artifacts and confirm expected files (model, config, metrics dump) exist. If upload failed mid-run, upload the missing artifacts to the SAME run — do not create a duplicate run.
5. **Registry is for finals only.** Register a model version only when it is a promotion candidate; experiment checkpoints stay run artifacts. No version 1 until there is a real candidate.
6. **Prune noise.** Delete smoke and aborted runs from the shared tracking server (or tag them `smoke`/`discard` and filter). Keep completed trainings and their dataset lineage.
7. **Run ids referenced by the user are canonical** — never substitute a different run id than the one given; if it looks wrong, say so instead of silently switching.

### Notebooks vs Scripts

- **Notebooks are for logic experiments**: call the core transformation, retrieval, scoring, or model function directly; expose intermediate inputs, outputs, and metrics. Do not make an endpoint, UI, or remote tool the center of the notebook unless the experiment is specifically about that integration.
- **Keep notebooks thin and reproducible**: reusable data preparation and domain logic live in importable modules; the notebook selects a bounded sample, invokes the logic, visualizes evidence, and records the resolved configuration and dataset version.
- **Scripts are for anything run repeatedly or remotely**: data prep, full trainings, HPO. A notebook that "got stuck after epoch 3" with no logs is unrecoverable; the script version with per-epoch logging is debuggable.
- Data preparation always lives in scripts, even while modeling is still notebook-phase — otherwise the dataset can't be rebuilt.

### Long / Remote Runs

For any training expected to exceed a few minutes on a remote machine, apply the remote-ops skill: named tmux session, per-epoch logging to a file, config printed at startup, GPU verified in the first minute. Additional training-specific rules:

- **Automation workers only smoke-run.** An agent working a training issue develops the code and runs the smoke; the full training is launched by the human (or launched in tmux and handed off) — the worker's timeout must never kill a real run.
- **Sanity-check early stopping before launch**: patience must be large enough to survive metric noise; log the stopping reason. After a run stops, check whether the metric was still improving — if so, rerun with corrected stopping before drawing conclusions.
- **Never fabricate inputs.** If a feature file (events, campaign calendars, labels) is missing rows, stop and ask for the data — do not invent plausible values to make the pipeline run.

## Promotion Gate (minimum evidence for `@production` alias)

- [ ] Beats current `@production` model on holdout set (never val set used during training)
- [ ] Val metric within eval rubric bounds (documented per project in CLAUDE.md)
- [ ] Smoke inference passes (forward pass on known input → expected output range)
- [ ] MLflow run has full params, metrics, artifacts, and model logged
- [ ] No data leakage confirmed (split sizes match expected; no ID overlap)
- [ ] Training run was reproducible (seed fixed; ran twice with matching metrics)

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "NaN loss"
#       python scripts/search.py "HPO warmup"
#       python scripts/search.py "MLflow promotion"
```
