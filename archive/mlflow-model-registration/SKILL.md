---
name: mlflow-model-registration
description: Register a trained model in MLflow with reproducible metadata, artifact verification, smoke-tested loading, and a clear handoff summary for staging or production promotion. Use when a checkpoint, exported model, or pyfunc wrapper needs to be logged and registered in an MLflow Model Registry workflow.
origin: adapted from an internal project-local skill pack
---

# MLflow Model Registration

Use this skill when a trained model is ready to move from experiment output into a reproducible MLflow registry flow.

## When to Activate

- Logging a trained model to MLflow for the first time
- Registering a new model version in the Model Registry
- Preparing a notebook or script for ML ops handoff
- Promoting a model candidate to staging after offline validation
- Replacing ad hoc run logging with a repeatable registration workflow

## Registration Contract

Every registration should capture:

- canonical artifact path
- model name and version identifier
- experiment name and run name
- source commit or code revision
- data snapshot or dataset version
- evaluation metrics used for approval
- artifact checksum
- runtime or base-model metadata needed for loading

Keep one editable configuration block at the top of the notebook or script. Everything else should derive from that block.

## Workflow

1. Choose the canonical artifact to register.
2. Verify the file exists, record size, and compute a SHA-256 checksum.
3. Smoke-test loading with the same code path production will use.
4. Define the serving artifact to register:
   - native framework flavor when enough
   - `pyfunc` wrapper when runtime loading needs custom logic
5. Start an MLflow run and log:
   - params for reproducibility
   - evaluation metrics
   - tags for model version, task, checksum, stage intent, and lineage
6. Log both the raw model artifact and the serving artifact when they differ.
7. Register the model version and assign the intended alias or stage according to the team's release policy.
8. Print a handoff summary with the run ID, model URI, checksum, metrics, and any remaining manual steps.

## Verification Pattern

Do not touch the registry until the artifact passes a local load check.

```python
from pathlib import Path
import hashlib

artifact = Path(MODEL_ARTIFACT_PATH).resolve()
assert artifact.exists(), f"Missing model artifact: {artifact}"

sha256 = hashlib.sha256(artifact.read_bytes()).hexdigest()
size_mb = artifact.stat().st_size / (1024 ** 2)

print({"artifact": str(artifact), "size_mb": round(size_mb, 1), "sha256": sha256})
```

Smoke-test the exact production loading path, not a simplified approximation. If production restores a checkpoint, rebuilds a tokenizer, or remaps state-dict keys, the registration code must prove that path still works before upload.

## Pyfunc Rules

Use a `pyfunc` wrapper when the registry artifact needs custom load logic or a standardized inference interface.

- Keep `predict(self, context, model_input, params=None)` compatible with MLflow expectations.
- Supply an `input_example` or explicit signature so downstream validation is meaningful.
- Keep wrapper attributes lazy-loaded inside `load_context`.
- If you remap checkpoint keys or normalize outputs, make that logic explicit in the wrapper rather than burying it in a notebook cell.

## Logging Rules

- Log baseline and candidate metrics together when approval depends on comparison.
- Tag the run with the artifact checksum so registry records and raw artifacts can be matched later.
- Prefer explicit version identifiers over ambiguous names like `final` or `latest`.
- Log the raw weights separately when the serving artifact is derived from them.
- Keep environment-specific values such as tracking URI, registry target, and model alias in the config block.

## Handoff Template

The registration output should end with a concise operator summary:

```text
Run ID: ...
Model URI: models:/...
Registered Model: ...
Version: ...
Artifact SHA-256: ...
Dataset Version: ...
Baseline Metrics: ...
Candidate Metrics: ...
Next Step: stage validation | approval review | production promotion
```

## Validation

- Artifact load path matches production behavior
- Checksum recorded in params or tags
- Metrics and params are sufficient to reproduce the run
- Model URI resolves to the expected registered model and version
- Stage or alias assignment matches release policy
- Manual follow-up steps are explicitly stated if full promotion is not automated
