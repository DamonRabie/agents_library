---
name: remote-ops
description: "Remote VM, SSH, and offline-environment operations for ML and data work. Actions: ssh to VM, run on remote, debug on remote, start long run, check training progress, transfer model, sync code to VM, check GPU, fix GPU, run in tmux, monitor remote job. Topics: jump host, ProxyJump, tmux session, nohup, long-running job survival, run-where-the-resources-are, offline/air-gapped VM, no internet on server, scp/rsync model weights, HuggingFace cache directory, HF_HOME, model download bypass, git sync local to VM, branch mismatch on VM, nvidia-smi, CUDA visibility, model not on GPU, remote logs, progress logging, tracking-server access split (job on VM / UI on laptop). Symptoms: command run on wrong machine, training killed when session dropped, cannot tell if run is stuck, VM has no internet, model download fails on server, wrong branch on VM, GPU idle while training slow, epoch takes forever, tmux session not found, ssh drops."
---
# Remote-Ops — Remote VM, SSH & Offline-Environment Discipline

The skill for working across a laptop and remote machines (GPU VMs, servers behind jump hosts, air-gapped boxes). Encodes the rules that repeated debugging sessions converged on: run code where the resources are, make every long run survive disconnection, make progress observable, and treat offline environments as first-class.

## When to Apply

### Must Use

- Any task that says "on the VM", "on the server", "ssh to", or involves a remote GPU
- Starting any run expected to take more than a few minutes on a remote machine
- Debugging a remote job (stuck, slow, killed, wrong output)
- Moving model weights or datasets to/from a machine without internet access
- Diagnosing GPU problems (job not using GPU, CUDA errors, slow epochs)

### Recommended

- Setting up a new remote environment for the first time
- Writing docs/runbooks that involve remote execution

### Skip

- Purely local development
- Production container deploys (use ci-deploy)

## Rule 1 — Run Where the Resources Are

The #1 recurring failure: editing/debugging on the laptop while the job, data, GPU, or credentials live on the VM (or vice versa).

- **Before every command, state which machine it runs on.** If a debug loop needs N iterations, do all N on the target machine over ssh — do not "try locally first" when the failure is remote.
- **Split by resource, not by habit:** compute-heavy and data-adjacent commands run on the VM; UIs and dashboards (tracking server, notebooks) are often reachable only from the laptop (port-forward). Both can be true in one task — keep the split explicit.
- **Services on the remote network should be reached through their APIs**, not by side-channels (e.g., use the tracking server's API rather than raw object-storage credentials it uses internally).
- Jump hosts: `ssh -J user@jump:port user@target`. Put frequently used hops in `~/.ssh/config` with `ProxyJump` so scripts and scp/rsync inherit them.

## Rule 2 — Long Runs Survive You

A training run must never die because an ssh session, agent process, or laptop lid did.

```bash
# Start the run in a named tmux session ON THE REMOTE MACHINE:
ssh vm "tmux new-session -d -s train_cat_v3 \
  'cd ~/project && source .venv/bin/activate && \
   python -m pipelines.train 2>&1 | tee artifacts/train_cat_v3.log'"

# Tell the user the session name. Check on it later:
ssh vm "tmux has-session -t train_cat_v3 && tail -20 ~/project/artifacts/train_cat_v3.log"
```

- **Always name the session** and report the name — "a tmux session" that can't be found later is as bad as none.
- **Verify the session actually started** (`tmux has-session`, then tail the log). A detached session that died at launch looks identical to a running one until you check.
- **Automation workers must also do this:** an agent that starts a long remote job runs it in tmux so the job continues if the agent times out or is stopped. The agent's own timeout must not become the job's timeout.

## Rule 3 — Every Run Is Observable

"I don't know if it is running or stuck" is a design failure, not a mystery.

- Log per-step/per-epoch progress with timestamps to a file (`tee` into `artifacts/<run>.log`). A silent 45-minute gap must be impossible in a healthy run.
- Log to the experiment tracker as well, but never only there — the log file is what you tail over ssh when the tracker is unreachable.
- Before a long run: print resolved config (data paths, device, batch size, tracking URI) at startup so a misconfigured run is caught in the first minute, not after hours.
- A run with early stopping must log why it stopped (patience exhausted at epoch N / max epochs). If patience is small relative to noise, flag it before the run, not after.

## Rule 4 — Offline / Air-Gapped Environments

Servers without internet are normal. Never assume a download will work on the remote side.

| Need | Pattern |
|---|---|
| HuggingFace model on offline VM | Download on laptop → `scp -r` the model directory → point code at the shared cache (`HF_HOME` / `TRANSFORMERS_CACHE` or an explicit local path) → set `HF_HUB_OFFLINE=1` so nothing tries the network |
| Cache location | Use the default HF cache layout in a shared directory, not custom per-project folders — code then works unchanged on any machine with the cache mounted |
| Registering a model without loading from the hub | Load from the local checkpoint path; never wrap a hub-download call in registration code |
| Python packages | Build a wheelhouse locally (`pip download -r requirements.txt -d wheels/`) → scp → `pip install --no-index --find-links wheels/` |
| Large files | `rsync -avP` (resumable) over scp for anything > a few hundred MB; verify with a checksum |

## Rule 5 — Code Sync Is Git, Not scp

- Sync code between laptop and VM by **commit → push → pull on the VM**. Never scp edited source files over a git checkout — the next pull silently loses or conflicts the changes.
- **Check the branch on the VM before running or editing anything there** (`git -C ~/project branch --show-current`). Work landing on the wrong branch (often the default branch) then needs untangling; if it happens: commit the changes on the wrong branch, move them with `git cherry-pick`/branch switch, and reset the wrong branch.
- If direct git access is broken on the VM, fix auth or use a bundle — do not fall back to copying files.

## GPU Sanity Checklist (slow training / GPU idle)

```bash
nvidia-smi                                   # is the process listed? memory allocated? utilization > 0?
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

| Symptom | Cause | Fix |
|---|---|---|
| nvidia-smi shows no process while "training" | Model/tensors on CPU | Verify `.to(device)` on model AND batches; print `next(model.parameters()).device` at start |
| CUDA available False | Driver/toolkit mismatch, wrong venv, or `CUDA_VISIBLE_DEVICES` empty | Check `nvidia-smi` works at all; reinstall matching torch build; check env vars |
| GPU util oscillates 0–100% | Dataloader starvation | Increase `num_workers`, `pin_memory=True`; check disk throughput |
| nvidia-smi prints errors (ERR!, lost GPU) | Driver wedged or hardware fault | Note exact error; a driver reload/reboot is a machine-owner decision — report, don't just retry |
| Works locally, OOM on VM (or reverse) | Different GPU memory; other tenants | Check free memory in nvidia-smi before sizing batch |

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "tmux long run"
#       python scripts/search.py "offline huggingface"
#       python scripts/search.py "gpu idle"
```
