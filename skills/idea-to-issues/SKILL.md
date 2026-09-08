---
name: idea-to-issues
description: "Plan work before development: clarify ideas through sufficient, adaptive interviewing, expose assumptions and tradeoffs, and shape useful iterations before detailing vertical issues. Use for new projects, complex features, design discussions, implementation planning, or repairing unclear plans and backlogs. Skip renewed discovery for straightforward implementation with settled requirements."
---
# Idea to Issues

Help the user reach a shared, clear understanding of what to build, why, and how to approach it. Interview until the consequential decisions are clear, then organize development into useful iterations with evidence and review points. Write executable issues when needed for the requested handoff.

The primary output is a clear plan. Question count, document length, and ticket count are not measures of success. Make relevant angles visible without turning every angle into a question. Clarity means agreed intent and explicit uncertainty, not certainty about every future implementation detail.

A **vertical slice** delivers one narrow behavior through every layer needed to make it work. It includes its wiring, relevant failure handling, tests, and operational evidence. For backend, data, infrastructure, and ML work, the consumer may be another system or an operator; a UI is not required.

## Choose the depth

- **Idea or new project:** establish intent, interview adaptively, synthesize the design, then plan iterations. A repository may not exist yet.
- **Existing PRD or plan:** preserve settled decisions, but check for consequential gaps and contradictions. A polished document is not evidence that its assumptions were agreed. Interview only about what remains unclear.
- **Existing backlog:** evaluate the whole set against the outcome; merge, split, or reorder only where needed. Preserve existing identifiers and explain replacements.
- **Small bounded request:** one issue can be the right answer. Do not manufacture a PRD, epic, or foundation phase.

Match artifacts to the request. Default to a conversational plan and iteration map; do not create files or full issue bodies merely because the skill is named idea-to-issues. For a requested durable handoff, keep the agreed design, iterations, and relevant issues together or linked. Planning does not itself authorize implementation, worker dispatch, or tracker changes.

## 1. Understand the outcome and current system

Before drafting iterations or issue titles:

1. Read the conversation and supplied material first. When a repository is relevant, read its instructions and trace the actual route from trigger/input through processing and state to the consuming surface. Inspect relevant tests and contracts, not just directory names. If intent is too vague to guide inspection, clarify it first; do not conduct an exhaustive repository audit before engaging the user.
2. State the target in observable terms: **who or what can do what, under which conditions, and what evidence proves it?** Preserve explicit constraints and non-goals.
3. Map the workflow or lifecycle, including material failure/recovery paths. Identify actors, state transitions, external boundaries, and existing components to reuse. For refactors, identify callers and behavior that must remain compatible.
4. Capture requirements as they become clear; use stable local IDs (`R1`, `R2`, ...) when needed to track a complex plan. Record current coverage as `covered`, `partial`, `missing`, or `unverified`, with evidence. Code presence alone does not prove integration or live behavior. Verify uncertain coverage where possible; otherwise keep the gap explicit.
5. Separate facts, proposed design, assumptions, and unresolved decisions. Record only the decisions that affect scope, contracts, acceptance, or sequencing.

Discover technical facts available in code or documentation. User goals, priorities, and acceptable tradeoffs need conversational evidence; do not infer them from the current implementation.

## 2. Interview until the plan is sufficiently clear

Use the interview to develop and challenge the idea, not just collect missing fields. Start with the uncertainty that most affects the direction. Translate vague terms such as "automatic", "better", or "production-ready" into a concrete scenario, boundary, or success condition. Ask for an example or counterexample when it would reveal a different interpretation.

For each round:

- Briefly state what is understood and the consequential gap. Ask one focused question, or a small group of closely related questions the user can comfortably answer together. Avoid a large questionnaire or serializing every minor detail into a separate turn.
- Explain the consequence of the choice. Offer a recommendation and alternatives when evidence supports them; leave room for the user to frame a different answer. Do not conceal a major design choice inside a suggested default.
- Use the answer to revise the working understanding and choose the next question. Follow up on ambiguity or contradictions; skip subjects already resolved by the conversation or evidence. Do not mechanically walk a fixed question list.
- Await answers before settling dependent choices. Continue independent investigation where useful. Silence is not agreement, and a proposed answer is not a user decision.

Consider the relevant angles: intended users and value; concrete journeys; scope and non-goals; inputs and outputs; ownership and system boundaries; state/data semantics; alternatives and tradeoffs; failure and recovery; success/evaluation; cost and operational constraints. These are thinking lenses, not mandatory questions. Explain a discovered risk or recommend a solution when a question would add no useful decision.

Before asking another question, identify what its answer could change in the goal, scope, design, acceptance, or next iteration. If it would not materially change any of these, use an explicit reversible assumption, defer it to implementation, or omit it. Revisit settled choices only when new evidence or a user correction matters. There is no minimum or maximum question count.

## 3. Synthesize the plan and check readiness

Once the material gaps appear resolved, explain the project back to the user in concrete terms: intended outcome and representative journey, scope/non-goals, proposed approach and important tradeoffs, constraints, success evidence, and remaining uncertainty. Keep this synthesis proportional to the project. Distinguish user decisions, verified facts, recommendations, and assumptions.

The plan is ready to decompose when:

- The outcome, consumer, and scope are clear enough to distinguish success from a plausible but wrong implementation.
- The main route and relevant boundaries are understandable, and consequential alternatives or contradictions have been addressed.
- Acceptance and the first useful outcome or learning objective are concrete.
- Remaining unknowns are either reversible details, explicitly deferred choices that do not invalidate the next iteration, or empirical questions with a bounded investigation and decision rule.

Resolve a material mismatch in this synthesis before treating the affected plan as settled. When the user's prior answers already establish these points, continue to iterations in the same response; do not add a ritual approval turn. When intent remains unresolved, stay in discovery for that scope. Do not turn a question the user needs to answer now into a ticket to make the plan appear complete. If the user explicitly asks to stop interviewing, provide a provisional plan with visible assumptions and affected branches, without claiming unresolved choices are agreed.

Describe the proposed end-to-end route and compare alternatives where they change cost, risk, or boundaries. Avoid specifying every internal function before implementation.

Agree the contracts that different slices or repositories must share: inputs/outputs, identifiers, state transitions, errors, compatibility, data semantics, and ownership. Use exact established names and shapes where necessary. Mark unverified paths or commands as proposed; never invent repository evidence.

Consider applicable failure modes: empty or malformed inputs, retries and duplicate writes, concurrency and stale results, time semantics, external outages, permissions, scale/cost, migration/backfill, observability, and rollback. Assign essential protections to the first slice that exposes the risk. Deferring polish must not create unsafe or incorrect intermediate behavior.

If an empirical unknown could invalidate the design, create a bounded **discovery** item: question, investigation limit, evidence to produce, decision rule, and affected follow-up work. Do not disguise research as an implementation issue with a guessed solution. Detail near-term slices; keep decision-dependent future work provisional until results are available.

## 4. Plan iterations before detailed issues

An **iteration** is a coherent increment of useful capability or learning, ending in evidence that informs the next step. It can contain one or several vertical issues. An issue is an executable unit within that increment; an iteration is not a synonym for an issue, epic, fixed calendar sprint, or technical layer.

Choose the first iteration to deliver the smallest useful real outcome or resolve an uncertainty that could change the project. A bounded experiment can precede the first delivery slice when feasibility is unknown. Account for the whole intended scope, but detail the next iteration more deeply than later ones; keep evidence-dependent work conditional.

For each iteration, state:

- **Outcome and scope:** what the user or consumer can do afterward, or what decision the evidence enables; what is deliberately deferred.
- **Rationale and prerequisites:** why this comes next, what uncertainty it addresses, and which capability, artifact, or decision it needs.
- **Evidence and review:** a demonstration, acceptance check, or experiment result; who evaluates it when human judgment is needed.
- **Next-step rule:** what would justify continuing, changing direction, repeating a bounded investigation, or stopping. Use ordinary acceptance for predictable work; do not invent an experiment for every feature.

Use a compact iteration map for complex projects. Read [references/planning-examples.md](references/planning-examples.md) when calibrating interview depth or the boundary between iterations and issues. Keep independent branches independent; milestones may group iterations but do not replace their evidence and feedback points.

## 5. Decompose ready iterations by behavior

Read [references/vertical-slicing.md](references/vertical-slicing.md) when creating or repairing a multi-issue breakdown. It contains the slicing procedure, exceptions, and worked examples.

Start delivery with a **walking skeleton**: the smallest real path from input to useful output using the intended integration boundaries. It may support one input type, one consumer, or one workflow variant. Shared setup belongs here when it is needed to demonstrate this path. Research may precede delivery as described above.

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

## 6. Sequence and audit the whole set

Create the slice map before expanding issue bodies:

| ID / kind | Iteration | Newly possible behavior or decision | Requirements | Prerequisites and reasons | Demonstration | Readiness |
|---|---|---|---|---|---|---|
| S1 / delivery | I1 | Narrow real path | R1 (partial) | None | Input reaches consumer | Ready |
| S2 / delivery | I1 | Additional scenario needed for I1's outcome | R1 (complete), R2 | S1: consumes its stable contract | Scenario works through consumer | Ready after S1 |

Use stable IDs while revising. `Ready` means the issue has enough information to execute once named prerequisites hold; decision-blocked work stays provisional.

For a large initiative, retain the iteration map above the issue breakdown; capability milestones or epics can group related outcomes. An epic is an outcome container, not a giant worker assignment. Identify the critical path and first useful milestone without forcing unrelated branches into identical waves.

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
6. **Iteration check:** does each iteration end in useful evidence, and can that evidence change later work? Are conditional choices still conditional, and does the first iteration have enough clarity to begin?

## 7. Write issues when the handoff needs them

Use [references/issue-template.md](references/issue-template.md). Include enough context for a worker with repository access but no planning conversation. Embed the relevant contract and decision details; link to canonical sources for broader context. Do not copy the entire plan into every issue.

Each issue identifies its outcome, scope/non-goals, prerequisites, relevant interfaces, acceptance checks, and verification evidence. Use verified code entrypoints as navigation aids; distinguish them from proposed files. Do not prescribe internal edits that inspection has not justified.

Acceptance describes observable behavior, including applicable negative paths. Verification states the command or procedure, expected result, and required environment/data/access. Distinguish local smoke proof, integration proof, live proof, and human judgment. If a command is unknown, describe the required check and mark command discovery explicitly; do not claim a guessed `make verify` proves it.

Classify execution separately from issue kind:

- **AFK:** specified implementation/investigation and verification can proceed without an unresolved human decision, within existing permissions. This does not imply permission to merge, deploy, or run expensive jobs.
- **HITL:** a named human decision or approval is necessary. State the exact gate and which work may proceed before it.

For data/ML work, define the hypothesis or consumer outcome, source/label/split semantics, artifact contract, and evidence needed for the next decision. Separate code smoke validation, full execution, and promotion when their environments or approval needs differ. Schedule resource contention by actual capacity; do not automatically serialize unrelated heavy work or require a human to launch every training run.

## 8. Deliver and revise the plan

Present the shared understanding and consequential decisions first, then the iterations and their review points, remaining assumptions/unknowns, and the concrete next step. Include the slice map, requirement coverage, and issue bodies to the depth requested. A planning conversation can finish with a clear iteration plan without generating a backlog. Do not end with another question once the readiness conditions are met.

When authorized to publish, prepare complete reviewable bodies first, confirm the target tracker and its conventions, and reuse verified existing issues. If publication is not authorized, finish the local drafts before requesting it. Use actual returned issue IDs, update dependency references, and read back the final bodies and links. After partial failure, reconcile what exists before retrying to avoid duplicates. Do not invent labels or change unrelated workflow state.

At an iteration review, compare the observed evidence with its acceptance or learning objective, then revise the next iteration before expanding its issues. User corrections or new evidence may also require revisiting the design; update affected contracts, iterations, issues, coverage, and dependencies together. Preserve requirement and issue IDs where possible and record superseded decisions. Workers should surface contract conflicts rather than silently change shared expectations; resolve reversible implementation details within the authorized scope. Re-check actual prerequisite artifacts and integration state before execution: a closed issue alone is not proof.

## Searchable checks

From this skill directory:

```bash
python scripts/search.py "vertical slice"
python scripts/search.py "dependency"
```

The CSVs contain compact review reminders. The workflow and linked references explain how to apply them.
