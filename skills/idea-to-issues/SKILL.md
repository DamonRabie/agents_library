---
name: idea-to-issues
description: "Idea-to-issues intelligence: design work completely before agents execute it. Three-phase workflow: Phase 1 = interrogate the idea efficiently (grill-me), Phase 2 = design doc + implementation plan (to-prd), Phase 3 = slice into self-contained issues (to-issues). Actions: interview, grill, challenge, clarify, shape, scope, design, write PRD, write implementation plan, create issues, slice, plan, break down, turn idea into issues, create ticket, wave slice, dependency map. Topics: PRD, design doc, technical design, dark corners, edge cases, decision record, assumption ledger, question budget, interface contract, file ownership, traceability, self-contained issue, user stories, acceptance criteria, vertical slice, AFK vs HITL, issue dependency, Blocks, Blocked by, wave, agent worker prompt, issue sizing, worker confusion, missed details, coverage map, ML training issue, smoke-only worker, hypothesis per experiment, resource class, stacked MR, overnight issue runner, dependency re-check at claim. Triggers: 'I want to build', 'help me plan', 'design this', 'turn this into issues', 'write a PRD', 'write an implementation plan', 'scope this feature', 'break this down for agents'."
---
# Idea-to-Issues — Design Work Completely Before Agents Execute It

Converts a vague idea into issues that agent workers execute without confusion. Three phases: **interrogate → design & plan → issues**. The two failure modes this skill exists to prevent:

1. **Interrogation waste** — asking many questions the repo or a sensible default could answer, exhausting the user before the design is done.
2. **Worker confusion / missed details** — decisions that live only in the conversation or the plan never reach the issue the worker actually reads, or issues are split across code seams so workers collide or lose context.

The cures are structural: a **question budget with an assumption ledger** in Phase 1, a **contract-level implementation plan** in Phase 2, and **self-contained issues with a traceability check** in Phase 3.

## When to Apply

### Must Use

- Starting any new feature, module, or experiment when intent is not yet precise
- Converting a conversation, plan, or idea into issues for agent execution
- Any time the user says: "I want to build X", "help me plan", "design this", "create issues for this"
- Before dispatching agent workers — unshaped issues cause scope creep and wasted runs

### Recommended

- When a feature request has hidden assumptions or unclear acceptance criteria
- Before a large refactor, to fix scope before any code changes

### Skip

- Small one-liner fixes with clear scope — just implement them
- Issues that already have complete, self-contained specs

## The Three-Phase Workflow

```
Phase 1: INTERROGATE   →   Phase 2: DESIGN & PLAN   →   Phase 3: ISSUES
(grill-me)                 (to-prd)                     (to-issues)
Decision Record            PRD + Implementation Plan    Self-contained issues
```

Each phase produces a written artifact; the next phase consumes only that artifact. This is deliberate: **if the artifact isn't sufficient for the next phase, it isn't sufficient for a worker either.** For a clear request with enough context, Phase 1 can collapse to a short assumption ledger presented for confirmation — never skip the ledger itself.

---

## Phase 1: INTERROGATE (Grill-Me)

**Goal:** every decision that shapes the design is either made or explicitly defaulted — with the minimum number of questions.

### The Question Economy (the core discipline)

Before asking anything, do **recon**: read the repo, configs, docs, schemas, and prior art. Then sort every unknown into one of three buckets:

| Bucket | Definition | Action |
|---|---|---|
| **Discoverable** | The answer exists in code, data, docs, or can be measured | Look it up. NEVER ask. |
| **Defaultable** | A sensible default exists and being wrong is cheap to fix later | Put it in the **assumption ledger** with your chosen default. Don't ask. |
| **User-owned** | Product intent, business tradeoff, taste, access/credentials, or being wrong is expensive | Ask. |

**Budget:** at most **2 question rounds** and **~7 questions total** for a typical feature (one round of ≤3 for something small; a third round only for genuinely large projects). If you are about to exceed the budget, the excess questions were probably defaultable — default them.

**Per round:**
- Batch **related** questions together (≤3–4 per round); ask one-at-a-time only when the answer changes what you'd ask next.
- Every question states in one line *why it matters* and offers a **recommended answer** — the user should be able to reply "yes to all" to a good round.
- Order by impact: decisions that change the architecture first; polish decisions never (default them).

**Interrogation lens** — check these axes for user-owned decisions (not as questions to ask verbatim):

| Axis | Key question |
|---|---|
| Scope | What is explicitly out of scope? |
| Data contract | What schema/artifact/API does this touch or freeze? |
| Failure & rollback | What happens when it breaks? What's the undo? |
| Done gate | What measurable check proves it works? |
| Dependencies | What must already be true? |
| Execution mode | Agent-executable AFK, or human judgment needed where? |
| ML/data specific | Controlled experiment or production change? Hypothesis? |

### Output: the Decision Record

Phase 1 ends with a short written record — this, not the chat scrollback, feeds Phase 2:

```markdown
## Decision Record: <feature>
### Decisions (user-confirmed)
- <decision>: <choice> — <why>
### Assumptions (defaults taken; object to change)
- <assumption>: <default chosen> — <cost if wrong: low>
### Out of scope
- <exclusion>
### Open risks
- <risk that design must mitigate>
```

**Stop condition:** stop interrogating when remaining unknowns no longer change the design. Present the assumption ledger for a single objection pass instead of asking more questions.

---

## Phase 2: DESIGN & PLAN (To-PRD)

**Goal:** a design that has considered every angle, plus an implementation plan a competent agent could execute **with zero access to this conversation**. That sentence is the quality bar for the whole phase.

Produce ONE document with two parts (or two files if the repo convention prefers): the **PRD** (why/what) and the **Implementation Plan** (how).

### Part A — PRD (compact)

```markdown
# PRD: <Feature Name>
## Problem
<1-3 sentences: what breaks or is missing today>
## Solution
<1-3 sentences: what this builds>
## User Stories
1. As a [persona], I want [action] so that [outcome]. AC: [measurable condition].
## Decisions & Out of Scope
<carried from the Decision Record>
## Acceptance Gates
- [ ] <measurable, executable check>
```

### Part B — Implementation Plan (the worker-facing truth)

```markdown
# Implementation Plan: <Feature Name>
## Architecture
<components and data flow; a small ASCII diagram beats prose>

## Interface Contracts (FROZEN)
<every boundary written EXACTLY: function signatures, API request/response
 shapes, table DDLs, file formats, config keys, metric names, CLI invocations.
 These are copy-paste sources for issues — precision here is what prevents
 two workers building incompatible halves.>

## File Touch Map
| Path | Action (create/modify) | What changes |

## Execution Order
Phase/step list with gates: what must be true before the next step starts.

## Edge Cases & Failure Handling
<from the Dark Corners sweep below — each one with its decided behavior>

## Verification Strategy
<how the whole feature is proven: commands, smoke path, expected outputs —
 per change type (see prove-it skill)>

## Rollback
<how to undo if it goes wrong in production>
```

### The Dark Corners Sweep (consider every angle)

Before the plan is final, walk this list and write the decided behavior for every applicable item — "N/A" is an acceptable answer, silence is not:

- **Empty/null/malformed input** — first run with no data; missing fields; encoding (non-Latin text, mixed languages)
- **Idempotency & retries** — what happens when any step runs twice or dies midway
- **Concurrency** — two runs at once; shared-table or shared-file collisions
- **Time** — timezone, calendar (non-Gregorian dates), DST, late-arriving data, clock of record
- **Scale & cost** — 10× data volume; API/token cost at full size; rate limits
- **Migration & backfill** — existing data; schema evolution; how history gets filled
- **Observability** — what gets logged; how a stuck run is distinguished from a slow one
- **Security & secrets** — where credentials come from (env, never code); what must not be committed
- **Failure surface** — external dependency down; partial failure; what the user sees
- **Rollback** — the concrete undo, tested in thought before needed

### Plan Rules

- The plan is **frozen during execution** — workers never edit it to match what they did; deviations are reported in MRs and the human amends the plan between waves.
- No detail may live only in the conversation. If it was decided, it is in the Decision Record or the plan.
- Use the project's domain language; avoid brittle file paths except where the contract would otherwise be ambiguous.

---

## Phase 3: ISSUES (To-Issues)

**Goal:** slice the plan into issues an agent executes without confusion, with zero details lost between plan and issues.

### Rule 0 — The Issue Is the Worker's Entire World

Write every issue as if the worker has **never seen the plan, the PRD, or this conversation**. Everything needed to execute lives in the issue body:

- **Copy, don't reference:** the relevant interface contracts, decisions, edge-case behaviors, and example inputs/outputs are pasted **verbatim** into the issue. A link to the plan is context, never a substitute — "see plan section 3" is how details get missed.
- Exact file paths to create/modify, exact commands to run, exact metric/config/table names — copied from the plan's frozen contracts, never paraphrased (paraphrase is where drift starts).

### Slicing Rules — cut along seams, not layers

1. **Slice at interface boundaries fixed in the plan.** Each issue implements one side of frozen contracts; the contract text appears verbatim in every issue that touches it, so independently-built halves fit.
2. **File ownership is exclusive per wave.** Two concurrently-runnable issues must never modify the same file. Build a file-ownership table from the plan's File Touch Map; if two slices need the same file, either merge the slices, sequence them (`blocked_by`), or move the shared change into an earlier foundation issue.
3. **Prefer fewer, larger, coherent issues.** Fragmentation confuses workers more than size does: every extra issue re-pays context setup and multiplies integration points. Split only when (a) the size cap is truly exceeded, (b) a human gate is needed between parts, or (c) parallelism across *different files* is actually wanted. Never split mid-behavior ("model + its tests + its wiring" is one issue, not three).
4. **Foundation first.** Shared scaffolding (schemas, base classes, config plumbing) is one issue that everything else is `blocked_by` — not repeated fragments of it in every issue.

### Detail Traceability Check (the missed-details killer)

After drafting issues and **before dispatching anything**, build this table and fix every gap:

| Plan item (decision / contract / edge case / AC) | Covered by issue | Verbatim in issue body? |
|---|---|---|
| <every numbered item from the plan> | ISSUE-NNN | yes / NO → fix |

Every plan item maps to **exactly one** issue (foundation items may map to the foundation issue). Any row with no issue, or with "referenced but not copied," is a defect in the breakdown — fix it now, not after a worker misses it.

### Coverage Map (what already exists)

Before drafting, check the repo: for each plan requirement mark `covered` / `partial` / `missing`. Only create issues for `missing` and `partial`.

### Issue Anatomy

```markdown
---
title: "ISSUE-NNN: <verb + noun + outcome>"
type: AFK | HITL
resource: light | warehouse-heavy | gpu-heavy
blocks: [ISSUE-NNN, ...]
blocked_by: [ISSUE-NNN, ...]
---

## Context
<why this slice exists; what the larger goal is — 1 paragraph, self-sufficient>

## Contracts (verbatim from plan)
<signatures, schemas, names this issue must implement or consume — EXACT text>

## Files
| Path | Action | Owned by this issue |

## Steps
<ordered implementation steps when the path matters; omit for truly obvious slices>

## Acceptance Criteria
1. Given X, when Y, then Z is measurably true.
(every AC executable as a test, command, or `make verify` check)

## How to Verify
<the exact commands the worker runs, with expected output>

## Out of Scope / Do NOT Touch
<files and behaviors this issue must leave alone — as important as the scope>
```

### Issue Sizing Rules

| Slice type | Size rule | Rationale |
|---|---|---|
| AFK (agent executes alone) | ≤ 1 day of work | Larger scope → higher error rate per run |
| HITL (human judgment needed) | No size constraint | Human gates the loop |
| Data/schema change | Own issue, first | Schema must be reviewed before dependent logic |
| Test-only issue | Only if tests are the full deliverable | Never "add tests" as a follow-on |
| Infra/config change | Own issue | Needs separate CI verification |

### AFK vs HITL Classification

**AFK:** agent can implement, verify (tests + `make verify`), and open an MR without human judgment — well-defined endpoint from a schema, DAG following an established pattern, bug fix with reproduction, behavior-preserving refactor.

**HITL:** human judgment inherently required — product/taxonomy decisions, architecture choices, data labeling/quality judgment, security audit, legal/compliance, full training runs and results analysis.

### Dependency Conventions

```
Blocks: [ISSUE-002]      # must complete before 002 starts
Blocked by: [ISSUE-001]  # cannot start until 001 done
```

No circular dependencies — draw the DAG before finalizing. Issues runnable in parallel must have disjoint file ownership (see Slicing Rule 2).

### Wave Slicing (ML experiments / multi-phase builds)

```
Wave 1: foundation (data contract, schema, smoke infrastructure)
  └── Gate: Wave 1 ACs pass; human reviews
Wave 2: core logic (training pipeline, feature logic, main API)
  └── Gate: Wave 2 metrics meet threshold; human reviews
Wave 3: optimization and productionization
  └── Gate: promotion criteria met
```

Agents do not proceed to Wave N+1 until the human gates Wave N.

### ML-Training Issue Rules (for plans that include model training)

1. **All training-code development for a wave goes in ONE issue** — don't split model variants of the same wave unless one variant's code depends on another's *results*.
2. **The worker's deliverable is code + passing smoke runs only.** Full trainings outlive worker timeouts and occupy the GPU — the human launches them (or the worker starts them in a named tmux session on the remote machine and hands off; see remote-ops).
3. **Results analysis is a separate HITL gate**, not part of the training issue.
4. **State the hypothesis on every experiment issue** — one line: what this wave tests and what result would change the plan.
5. **Resource classes:** label issues light / warehouse-heavy / gpu-heavy. At most one heavy issue runs at a time; light issues may run in parallel in worktrees. Skip, don't reshuffle agreed priorities.

### Dispatch-Time Rules (when workers execute)

- **Re-check dependencies at claim time:** before claiming, verify every `blocked_by` issue is actually merged/closed — plan-time state goes stale.
- **Stacked branches:** if issue B is blocked by A and A's MR is unmerged, B branches from A's branch (MR targets A's branch), never from master. See the commit skill's stacked-branch recipe.
- **Workers never merge to master without review** unless the issue is explicitly auto-mergeable; the default gate is an open, reviewable MR per issue.
- **The plan document is frozen during execution** — deviations go in the MR description, not into the plan.

### Pre-Dispatch Checklist

- [ ] Traceability table complete — every plan item verbatim in exactly one issue
- [ ] File-ownership table has no overlap between parallel issues
- [ ] Every AC is falsifiable and executable; "How to Verify" commands present
- [ ] Contracts pasted verbatim (not paraphrased, not referenced-only)
- [ ] Out of Scope / Do NOT Touch present on every AFK issue
- [ ] Dependency DAG drawn; no cycles; heavy issues serialized
- [ ] Worker prompt names the repo memory file and relevant skills; no secrets inline

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "self contained issue"
#       python scripts/search.py "question budget"
#       python scripts/search.py "traceability"
```
