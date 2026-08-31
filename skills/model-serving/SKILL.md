---
name: model-serving
description: "Package, register, deploy, verify, and roll back inference models. Use for export parity, artifact manifests, model-registry aliases, automated promotion/deployment, runtime model identity, serving containers, smoke inference, latency, and failures where registry state differs from the running service."
---
# Model-Serving — Model Packaging, Registry & Inference

Complete guide for the export → verify → register → promote pipeline. Encodes the checklist that prevents the 12-commit ONNX debug chain: verify the exported model numerically against the source BEFORE uploading, handle multi-file artifacts, and always test rollback before promoting to production.

## When to Apply

### Must Use

- Exporting any model to ONNX, TorchScript, or SavedModel format
- Registering a model in MLflow or any model registry
- Promoting a model alias (@staging → @production)
- Debugging a serving failure (wrong output, model not found, Triton error)
- Building or updating a Docker serving image
- Rolling back a model version

### Recommended

- Reviewing a serving pipeline before deploying
- Capacity planning for inference (latency budget, batch size, GPU memory)
- Adding a new model backend (Triton, ONNX Runtime, TorchServe)

### Skip

- Training/experiment management (use ml-experiments)
- CI/CD pipeline setup (use ci-deploy)
- ClickHouse or data pipeline work

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Numerical parity BEFORE upload | CRITICAL | Source vs exported delta < 1e-4 | Upload first, verify later (12-commit ONNX day) |
| 2 | Artifact manifest completeness | CRITICAL | All companion files (.onnx.data) present | Copying only top-level .onnx file |
| 3 | Smoke inference after registration | HIGH | Forward pass on known input after registry load | Assuming upload = working |
| 4 | Alias discipline | HIGH | @staging before @production; rollback = re-alias | Overwriting @production without staging |
| 5 | Rollback tested before promote | HIGH | Verify alias rollback in staging | No rollback plan before prod promote |
| 6 | MLflow connectivity | MEDIUM | MLFLOW_TRACKING_URI set; host reachable from export context | Header error discovered mid-export |
| 7 | GPU docker hygiene | MEDIUM | Non-root; NVIDIA runtime; healthcheck; correct CUDA version | Root user; mismatched CUDA |
| 8 | Latency budget | MEDIUM | Measure p50/p99 before and after change | Serving latency regression undetected until prod |
| 9 | Runtime identity | CRITICAL | Running service proves exact model version/digest | Treating registry metadata as deployment proof |
| 10 | Promotion automation | HIGH | Idempotent trigger; stale-event guard; observable rollout | Alias changes that never refresh the service |

## The Export → Verify → Register → Promote Pipeline

**NEVER skip or reorder these steps:**

```
1. EXPORT  →  2. VERIFY (numerical parity)  →  3. REGISTER  →  4. SMOKE  →  5. PROMOTE
```

### Step 1: Export

```python
import torch

model.eval()
dummy_input = torch.randn(1, input_dim)  # use realistic input shape

torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=17,                    # pin opset explicitly
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
)
```

### Step 2: Verify (BEFORE any upload)

```python
import onnxruntime as ort
import numpy as np

# Source model output
with torch.no_grad():
    source_out = model(dummy_input).numpy()

# Exported model output
sess = ort.InferenceSession("model.onnx")
ort_out = sess.run(None, {"input": dummy_input.numpy()})[0]

# Parity check — must pass before upload
max_delta = np.abs(source_out - ort_out).max()
assert max_delta < 1e-4, f"Numerical parity FAILED: max_delta={max_delta}"
print(f"Parity check passed: max_delta={max_delta:.2e}")
```

### Step 3: Register (with full artifact manifest)

```python
import mlflow
from pathlib import Path

# Collect ALL companion files (including .onnx.data for large models)
artifact_dir = Path("model_artifacts")
artifact_dir.mkdir(exist_ok=True)

# Use rglob to capture nested companion files
for f in Path(".").rglob("model*"):
    shutil.copy(f, artifact_dir / f.name)

with mlflow.start_run():
    mlflow.log_artifacts(str(artifact_dir), artifact_path="model")
    model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"

registered = mlflow.register_model(model_uri, "my_model")
# Set @staging first; NEVER @production directly
client = mlflow.tracking.MlflowClient()
client.set_registered_model_alias("my_model", "staging", registered.version)
```

### Step 4: Smoke Inference After Registration

```python
# Load from registry (not local file) — proves registration worked
model_uri = "models:/my_model@staging"
loaded_sess = mlflow.onnx.load_model(model_uri)
smoke_out = loaded_sess.run(None, {"input": dummy_input.numpy()})[0]

assert smoke_out.shape == expected_shape, "Shape mismatch after registry load"
assert not np.isnan(smoke_out).any(), "NaN in smoke inference output"
print("Smoke inference: PASSED")
```

### Step 5: Promote (after smoke passes)

```python
# Record rollback point BEFORE promoting
current_prod = client.get_model_version_by_alias("my_model", "production")
print(f"Rollback version: {current_prod.version}")

# Promote staging to production
client.set_registered_model_alias("my_model", "production", registered.version)
print(f"Promoted version {registered.version} to @production")
```

## Registry State Is Not Runtime State

A registry alias is control-plane metadata. Changing it does not prove that an existing serving process reloaded, redeployed, or is routing traffic to the new version.

Define one refresh contract for each service:

- load on process start and trigger an immutable rollout after promotion;
- poll the registry and atomically reload after validation;
- consume a signed promotion event and deploy the referenced immutable version; or
- resolve on each request only when the latency and consistency tradeoff is explicitly acceptable.

Promotion automation must be idempotent and keyed by immutable model version or artifact digest. Ignore stale or duplicate events, serialize competing promotions, preserve the prior serving target, and expose rollout status. The running service should report a non-sensitive model name plus immutable version/digest through a health or metadata interface.

After every promotion, query the running service identity and perform smoke inference through the real serving path. Registry lookup plus local model loading is not deployment verification.

## Rollback Procedure

```python
# Roll back by re-aliasing to previous version (recorded above)
client.set_registered_model_alias("my_model", "production", rollback_version)
print(f"Rolled back to version {rollback_version}")
# Run the service's refresh contract, then verify runtime identity and smoke inference.
```

## Multi-File Artifact Handling (.onnx.data)

Large ONNX models split weights into `.onnx.data` companion files. **Always use `rglob`:**

```python
from pathlib import Path
import shutil

def collect_onnx_artifacts(export_dir: Path, artifact_dir: Path):
    """Copy all ONNX files including companion .onnx.data files."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for f in export_dir.rglob("*"):  # rglob catches nested dirs
        if f.is_file():
            dest = artifact_dir / f.relative_to(export_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    files = list(artifact_dir.rglob("*"))
    print(f"Collected {len(files)} artifact files: {[f.name for f in files]}")
    return files
```

## Triton Model Repository Layout

```
triton_repo/
  my_model/
    config.pbtxt       # Triton model config
    1/                 # version directory
      model.onnx       # model file
      model.onnx.data  # companion file (if present)
```

```protobuf
# config.pbtxt for ONNX backend
name: "my_model"
backend: "onnxruntime"
max_batch_size: 64
input [{ name: "input" data_type: TYPE_FP32 dims: [-1, 768] }]
output [{ name: "output" data_type: TYPE_FP32 dims: [-1, 256] }]
dynamic_batching { max_queue_delay_microseconds: 5000 }
```

## Serving Docker Image

```dockerfile
FROM nvcr.io/nvidia/tritonserver:24.01-py3 AS runtime
# Non-root user for GPU containers
RUN useradd -m serving
WORKDIR /models

COPY triton_repo/ /models/
USER serving

HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/v2/health/ready || exit 1

EXPOSE 8000 8001 8002
CMD ["tritonserver", "--model-repository=/models"]
```

## MLflow Connectivity Troubleshooting

```bash
# Check tracking URI
echo $MLFLOW_TRACKING_URI

# Test reachability (common issue: export context can't reach MLflow server)
curl -f "$MLFLOW_TRACKING_URI/api/2.0/mlflow/experiments/list"

# If behind proxy, check Host header:
# MLflow client sends Host: <tracking_server_host>
# Nginx/Caddy must forward it correctly
```

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "ONNX companion file"
#       python scripts/search.py "Triton model config"
#       python scripts/search.py "rollback alias"
```
