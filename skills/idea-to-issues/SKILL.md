---
name: idea-to-issues
description: "Analyze product or technical work and turn ideas, PRDs, or existing plans into complete, dependency-aware vertical issues. Use for complex task decomposition, feature scoping, implementation planning, or repairing a weak backlog. Do not use for straightforward implementation with already-fixed requirements."
---
# Idea to Issues

Produce a breakdown that reaches the requested outcome, with issues a worker can implement and verify without the planning conversation. Organize work around observable capabilities, not technical layers or lists of files.

A **vertical slice** delivers one narrow behavior through every layer needed to make it work. It includes its wiring, relevant failure handling, tests, and operational evidence. For backend, data, infrastructure, and ML work, the consumer may be another system or an operator; a UI is not required.

## Choose the depth

- **Idea:** investigate intent and current behavior, resolve consequential unknowns, then design and slice.
- **Existing PRD or plan:** preserve settled decisions; inspect the implementation and gaps, then slice. Do not restart discovery unnecessarily.
- **Existing backlog:** evaluate the whole set against the outcome; merge, split, or reorder only where needed. Preserve existing identifiers and explain replacements.
- **Small bounded request:** one issue can be the right answer. Do not manufacture a PRD, epic, or foundation phase.

Match artifacts to the request. A compact plan can contain decisions, coverage, and issues in one document. For complex work, keep a design document plus a slice map and issue bodies. Planning does not itself authorize implementation, worker dispatch, or tracker changes.

## 1. Understand the outcome and current system

Before drafting titles:

1. Read the supplied source and relevant repository instructions. Trace the actual route from trigger/input through processing and state to the consuming surface. Inspect existing tests and contracts, not just directory names.
2. State the target in observable terms: **who or what can do what, under which conditions, and what evidence proves it?** Preserve explicit constraints and non-goals.
3. Map the workflow or lifecycle, including material failure/recovery paths. Identify actors, state transitions, external boundaries, and existing components to reuse. For refactors, identify callers and behavior that must remain compatible.
4. Extract requirements with stable local IDs (`R1`, `R2`, ...). Record current coverage as `covered`, `partial`, `missing`, or `unverified`, with evidence. Code presence alone does not prove integration or live behavior. Verify uncertain coverage where possible; otherwise keep the gap explicit.
5. Separate facts, proposed design, assumptions, and unresolved decisions. Record only the decisions that affect scope, contracts, acceptance, or sequencing.

Discover answers available in code or documentation. State inexpensive reversible defaults and continue. Ask concise questions only when user intent or a costly tradeoff changes the plan; do not use an arbitrary question quota to guess an essential decision. Continue independent analysis while awaiting an answer. An unresolved decision blocks only affected slices.

## 2. Design enough to choose meaningful slices

Describe the proposed end-to-end route and compare alternatives where they change cost, risk, or boundaries. Avoid specifying every internal function before implementation.

Agree the contracts that different slices or repositories must share: inputs/outputs, identifiers, state transitions, errors, compatibility, data semantics, and ownership. Use exact established names and shapes where necessary. Mark unverified paths or commands as proposed; never invent repository evidence.

Consider applicable failure modes: empty or malformed inputs, retries and duplicate writes, concurrency and stale results, time semantics, external outages, permissions, scale/cost, migration/backfill, observability, and rollback. Assign essential protections to the first slice that exposes the risk. Deferring polish must not create unsafe or incorrect intermediate behavior.

If an unknown could invalidate the design, create a bounded **discovery** item: question, investigation limit, evidence to produce, decision rule, and affected follow-up work. Do not disguise research as an implementation issue with a guessed solution. Detail near-term slices; keep decision-dependent future work provisional until results are available.

## 3. Decompose by behavior

Read [references/vertical-slicing.md](references/vertical-slicing.md) when creating or repairing a multi-issue breakdown. It contains the slicing procedure, exceptions, and worked examples.

Start with a **walking skeleton**: the smallest real path from input to useful output using the intended integration boundaries. It may support one input type, one consumer, or one workflow variant. Shared setup belongs here when it is needed to demonstrate this path.

Expand by one coherent scenario, lifecycle transition, supported variant, or operating capability at a time. Each delivery issue should complete this sentence:

> After this issue and its prerequisites, <consumer> can <new behavior>; demonstrate it by <observable check>.

If the sentence only says a table, service, or component exists, reconsider the boundary. Technical deliverables qualify when they are the requested consumable outcome, such as a published API, an operator recovery command, or a compatible library migration.

For each candidate slice:

- Include all necessary layers and integration work, plus tests and relevant docs/config. Do not defer its wiring or correctness to a final integration/testing ticket.
- Keep one coherent acceptance story. Split oversized work by narrower behavior, input population, or lifecycle path; do not split database/backend/frontend/tests into separate tickets merely to shrink it.
- Merge fragments that cannot demonstrate an outcome without one another. Do not merge unrelated behaviors just because they touch the same file.
- Keep independently reviewable enablement, migration, or discovery work separate only for a concrete reason. Name its immediate consumer, deliverable, verification, and why it cannot reasonably live in that consumer's slice.
- Bound human decision items too: specify the decision, evidence, responsible role, and what it unblocks. `HITL` is not permission for an unlimited issue.

Size by outcome count, uncertainty, integration boundaries, verification cost, and reviewability. Time estimates are secondary and explicitly approximate. Aim for a focused change/review per issue, not a universal day limit or a target ticket count.

## 4. Sequence and audit the whole set

Create the slice map before expanding issue bodies:

| ID / kind | Newly possible behavior or decision | Requirements | Prerequisites and reasons | Demonstration | Readiness |
|---|---|---|---|---|---|
| S1 / delivery | Narrow real path | R1 (partial) | None | Input reaches consumer | Ready |
| S2 / delivery | Additional scenario | R1 (complete), R2 | S1: consumes its stable contract | Scenario works through consumer | Ready after S1 |

Use stable IDs while revising. `Ready` means the issue has enough information to execute once named prerequisites hold; decision-blocked work stays provisional.

For a large initiative, group slices under capability milestones or epics, then decompose each into executable issues. An epic is an outcome container, not a giant worker assignment. Identify the critical path and first useful milestone without forcing unrelated branches into identical waves.

Distinguish dependencies:

- **Hard prerequisite:** a required artifact, capability, or decision. Record what it provides and the condition for release; avoid unexplained `blocked_by` lists.
- **Coordination constraint:** overlapping files, migrations, deployments, or exclusive resources. Sequence or coordinate these without pretending they are product dependencies.
- **Preference:** a desirable order that does not block execution.

Check for cycles, missing prerequisites, excessive fan-in, and a giant foundation that delays the first useful outcome. File overlap informs scheduling after slicing; it does not define the slices. Cross-repository slices need explicit contract ownership and coordinated reviews, or separately verifiable producer/consumer issues with a visible integration owner.

Build requirement coverage separately from the dependency graph:

| Requirement / final acceptance gate | Existing evidence | Delivery owner(s) | Final proof owner | Gap or deferral |
|---|---|---|---|---|

A requirement may need multiple issues. Shared invariants belong in every affected issue; name the issue responsible for proving their composition. Each required behavior needs an owner or an explicit unresolved gap. Do not silently turn requirements into non-goals. A requested full breakdown must account for later work even when its details remain provisional.

Run these challenges before accepting the set:

1. **Prefix check:** after each delivery slice and its dependencies, what new behavior actually works? Supporting work needs its explicit exception rationale.
2. **Deletion check:** remove each issue mentally. If the final outcome still holds, is that issue optional, duplicate, or outside scope?
3. **Integration check:** do outputs reach their intended consumers? Is any wiring, migration, rollout, recovery, or whole-flow proof ownerless?
4. **Sizing check:** can each issue be reviewed and verified as one coherent change? Does any ticket contain several independently useful outcomes?
5. **Coverage check:** do the issues plus existing evidence satisfy the original outcome and constraints, including failure cases? Explain any unmet requirement.

## 5. Write issues for execution

Use [references/issue-template.md](references/issue-template.md). Include enough context for a worker with repository access but no planning conversation. Embed the relevant contract and decision details; link to canonical sources for broader context. Do not copy the entire plan into every issue.

Each issue identifies its outcome, scope/non-goals, prerequisites, relevant interfaces, acceptance checks, and verification evidence. Use verified code entrypoints as navigation aids; distinguish them from proposed files. Do not prescribe internal edits that inspection has not justified.

Acceptance describes observable behavior, including applicable negative paths. Verification states the command or procedure, expected result, and required environment/data/access. Distinguish local smoke proof, integration proof, live proof, and human judgment. If a command is unknown, describe the required check and mark command discovery explicitly; do not claim a guessed `make verify` proves it.

Classify execution separately from issue kind:

- **AFK:** specified implementation/investigation and verification can proceed without an unresolved human decision, within existing permissions. This does not imply permission to merge, deploy, or run expensive jobs.
- **HITL:** a named human decision or approval is necessary. State the exact gate and which work may proceed before it.

For data/ML work, define the hypothesis or consumer outcome, source/label/split semantics, artifact contract, and evidence needed for the next decision. Separate code smoke validation, full execution, and promotion when their environments or approval needs differ. Schedule resource contention by actual capacity; do not automatically serialize unrelated heavy work or require a human to launch every training run.

## 6. Deliver and maintain the breakdown

Present the outcome, important assumptions/open decisions, slice map, requirement coverage, and requested issue bodies. Explain consequential split/merge choices and the first useful milestone. Ask only about remaining decisions that materially affect the work, rather than requiring ritual approval of every planning phase.

When authorized to publish, prepare complete reviewable bodies first, confirm the target tracker and its conventions, and reuse verified existing issues. If publication is not authorized, finish the local drafts before requesting it. Use actual returned issue IDs, update dependency references, and read back the final bodies and links. After partial failure, reconcile what exists before retrying to avoid duplicates. Do not invent labels or change unrelated workflow state.

On user corrections or new implementation evidence, update the affected contracts, issues, coverage, and dependencies together. Preserve requirement and issue IDs where possible and record superseded decisions. Workers should surface contract conflicts rather than silently change shared expectations; resolve reversible implementation details within the authorized scope. Re-check actual prerequisite artifacts and integration state before execution: a closed issue alone is not proof.

## Searchable checks

From this skill directory:

```bash
python scripts/search.py "vertical slice"
python scripts/search.py "dependency"
```

The CSVs contain compact review reminders. The workflow and linked references explain how to apply them.
