# Decomposing complex work into vertical slices

Use this procedure after shared understanding and an iteration map exist. These examples demonstrate issue boundaries, not a reason to skip the interview or make every issue its own iteration. Several slices may be needed for one meaningful iteration outcome. Keep later issue details provisional when an iteration review could change them.

## Work from scenarios to tickets

1. Write the final demonstration: a concrete input/trigger, the real route it follows, the visible result, and the essential failure behavior. This anchors completeness.
2. Sketch a scenario map. Rows are consumer journeys or lifecycle paths; columns are variants such as input type, scale, permissions, or recovery. Mark what already works. This is an analysis aid, not a ticket for each cell.
3. Select a thin first route that traverses the real boundaries. Prefer a representative case that exposes the important integration risk early. A mocked consumer is useful for development but cannot prove that the real consumer works.
4. Add increments by narrowing one dimension at a time. Compare at least two plausible decompositions when boundaries are unclear; choose based on early usable evidence, risk, coupling, and review size. Do not generate alternatives mechanically for an obvious plan.
5. State the before/after capability and demonstration for every candidate. If an issue needs a future issue to work, bring that missing behavior into it or classify it as supporting work with a reason.
6. Audit the ordered set against the final demonstration and requirements. Add explicit owners for missing behavior rather than a vague closing ticket called "integration and polish."

Useful cuts:

| Dimension | Narrow first behavior | Further behavior |
|---|---|---|
| Input or population | One supported format or bounded cohort | More formats/cohorts |
| Workflow | Complete one valid transaction | Cancellation or amendment |
| Rule complexity | One agreed policy with explicit unsupported cases | More policy variants |
| Consumer | One actual caller uses the new capability | Migrate additional callers |
| Operation | Correct bounded execution with visible failures | Operator recovery or higher throughput |
| Migration | One compatible caller on the new path | More callers, then retire the old path |

Select only dimensions present in the user's request. A slice is not permission to add features. Distinguish a deliberately limited first release from abandoning the requested remaining scope.

## Essential correctness travels with the behavior

A first slice may have limited functionality; it must still honor the invariants of the path it enables. For example:

- A background writer needs safe behavior on duplicate delivery immediately; richer operator replay tools may follow.
- A private report download needs access control with its first usable download; do not defer it to "hardening."
- A replacement data path needs agreed time/grain semantics and compatibility when its first consumer moves.
- A cancellation feature needs late-result handling in the same issue; a flag alone does not deliver cancellation.

Use feature gating or a restricted cohort when appropriate, naming who can exercise the path and how it is verified. If actual integration proof is unavailable, record the limitation and its owner; do not label the feature complete based on mocks.

## When supporting issues are justified

Every exception names a consumer and a bounded exit condition.

| Kind | Legitimate reason | Required evidence |
|---|---|---|
| Enablement | A shared prerequisite has its own review/access/release boundary | Concrete consumable artifact; first consumer; why embedding it is impractical |
| Migration | Compatibility or production rollout requires separately staged expansion/backfill/cutover | Data/compatibility assertions, cutover conditions, recovery path |
| Discovery | An empirical unknown changes the feasible design | Time/effort limit, experiment/question, decision rule, deliverable |
| Decision | Human-owned intent or approval blocks a particular branch | Options, relevant evidence, decision owner, affected slices |
| Verification | Independent certification or whole-system evidence is itself requested | Exact boundary and evidence; ordinary slice tests still stay in their slices |

A new table or config key alone is not a reason for an exception. Do not make all work depend on a generic "foundation" ticket. Extract only the prerequisite actually shared and immediately needed.

## Example 1: asynchronous report exports

**Request:** users request reports, follow progress, download their reports, and cancel unfinished exports. Assume authentication, a queue, and object storage already exist. Retention policy is a separate unresolved decision, not guessed here.

**Weak breakdown:** database schema -> worker -> API -> UI -> tests. The user receives no working export until nearly everything is finished, and cancellation races have no clear owner.

**Better breakdown:**

| ID | Capability and included work | Depends on | Demonstration |
|---|---|---|---|
| S1 | User requests one bounded report type and downloads the completed result. Includes request UI/API, durable job state, queue/worker/storage wiring, terminal failure display, owner-only download, duplicate-delivery safety, tests. | Existing auth/queue/storage | Request through the actual surface, run worker, download correct content; another user cannot access it; redelivery does not duplicate the result. |
| S2 | User sees queued/running/terminal progress without manually refreshing. Includes worker status updates, retrieval and UI refresh, terminal-state consistency. | S1 job identity and state contract | Run an export and observe status changes through the UI; finished state never returns to running. |
| S3 | User cancels queued/running exports and cannot retrieve a result published after cancellation. Includes action UI/API, state transition, worker cooperation, late-completion race handling. | S1 job lifecycle; coordinate state edits with S2 | Cancel queued and running jobs; race cancellation with completion; verify the agreed terminal-state winner and download behavior. |

S1 is illustrative, not automatically an acceptable size. If building those boundaries is too large in the actual repo, narrow to a preconfigured small report requested and retrieved through the existing API consumer, then add the interactive user journey as the next vertical slice. Retain that UI requirement in coverage; do not silently redefine the final product as API-only. If neither narrowing is feasible, name the specific enablement prerequisite and its evidence.

S3 does not inherently depend on S2's live refresh. File overlap creates a coordination constraint, not that semantic dependency. Retention-dependent cleanup stays provisional until policy is decided; the plan must explicitly retain this gap if retention is part of the requested outcome.

## Example 2: a data pipeline feeding an existing dashboard

**Request:** replace a manual daily feed with scheduled ingestion, historical backfill, and a dashboard consuming the output. Existing dashboard and scheduler are available; the source contract is known.

| ID | Capability | Depends on | Demonstration |
|---|---|---|---|
| S1 | One bounded date is ingested into the target contract and displayed by the dashboard. Includes extraction, transformation, storage, consumer wiring, grain/time/null semantics, duplicate-safe writes, bounded reconciliation. | Source access and agreed semantics | Run one date, reconcile source/target at the agreed grain, verify dashboard values, rerun without duplication. |
| S2 | The feed refreshes automatically with visible freshness/failure state. Includes scheduling, retry policy, alerts/status, operator instructions. | S1 repeatable date ingestion | Exercise scheduled execution and a failed attempt; prove recovery and that stale data is observable. |
| S3 | Operators backfill a bounded historical range and resume interruptions without disrupting current dates. Includes range controls, checkpoints, concurrency policy, reconciliation. | S1 ingestion contract; coordinate with S2's live writes | Interrupt/resume a sample range; reconcile each partition and show current-date data remains correct. |

R1 (automated dashboard freshness) spans S1 and S2; S2 owns its final proof. Duplicate-safe writes apply in all three issues. An "exactly one issue per requirement" rule would lose this coverage. A full historical run may require a separate execution issue if its cost/access differs from code validation; identify the actual environment and release gate.

## Example 3: replacing a shared client across repositories

**Request:** migrate several services to a new client while preserving behavior, then remove the legacy path.

- **S1:** one low-risk real caller uses the replacement client, including the minimal adapter, configuration, compatibility checks, and rollback switch. Demonstrate that caller's existing behavior using the new path.
- **S2/S3:** migrate other callers by distinct behavior or compatibility needs, each with its own integration proof. Both consume S1's established contract; shared release files may require coordination.
- **S4:** remove the legacy path after all callers are verified migrated. Prove no active callers/configuration require it and normal operation continues.

If a separately versioned package must ship before any caller can use it, a bounded enablement issue can publish that package with compatibility evidence and S1 as its named consumer. Track the package release and consuming PR explicitly. "Implement client", "migrate everything", and "test everything" hide the riskiest consumer boundary.

## Example 4: ML work with a decision-dependent path

**Request:** evaluate whether a new representation improves ranking and, if it meets agreed criteria, expose it through an existing inference consumer.

- **S1:** produce one reproducible baseline comparison on the agreed dataset/split, from prepared input through tracked metrics and an inspectable prediction sample. Include leakage checks and artifact identity. Reuse verified existing training components.
- **S2:** evaluate one coherent representation change through the same comparison contract. State hypothesis, resource budget, and success rule. Include full execution only if authorized and feasible in the execution environment; code smoke proof alone does not resolve the hypothesis.
- **D1:** decide whether the evidence satisfies the agreed promotion criteria. Bound the decision to named metrics and sample checks. Make this HITL only when human judgment/approval is actually required.
- **S3 (conditional):** expose the chosen artifact through one real inference consumer with parity, runtime identity, and recovery evidence. Its readiness depends on D1 and the selected artifact; do not freeze model-dependent details before the result exists.

Account for the failed-experiment branch: retain the baseline and record the negative result; do not automatically invent a tuning backlog. Do not put every variant in one huge issue solely because it belongs to the same wave.
