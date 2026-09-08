# Execution-ready issue template

Use the repository's tracker format when established. Preserve these semantics without forcing identical headings. Omit genuinely irrelevant optional fields; do not omit an unresolved dependency by calling it irrelevant.

```markdown
# S<N>: <consumer capability or bounded decision>

- Kind: delivery | enablement | migration | discovery | decision | verification
- Execution: AFK | HITL (exact human decision/gate if applicable)
- Readiness: ready | ready after prerequisites | provisional (reason)
- Requirements: R<N>, R<M> (summarize relevant requirements below)
- Iteration: I<N> (state how this issue contributes to its outcome or review evidence)
- Parent/design: <verified reference when available>

## Outcome and context
<Current limitation, new behavior, and why it advances the larger outcome.
For supporting work: name the consumer and explain the separate boundary.>

## Scope
<One coherent behavior through the required layers, including integration,
applicable failure handling, tests, config/docs, and rollout work.>

## Out of scope
<Adjacent behaviors reserved for other slices and explicit user constraints.>

## Prerequisites and coordination
- Hard prerequisites: <ID -> exact artifact/capability/decision and release condition, or none>
- Coordination: <shared files/schema/resource/environment constraints, or none>
- External prerequisites: <access/data/service; availability verified or unresolved>

## Contract and implementation context
<Embed relevant agreed input/output examples, identifiers, state/error semantics,
compatibility obligations, and decisions. Include exact canonical names where needed.
Link broader context; distinguish observed code entrypoints from proposed changes.
Add ordered implementation notes only when sequence or method matters.>

## Acceptance criteria
- [ ] Given <state/input>, when <action>, then <observable output/state>.
- [ ] Given <relevant failure/retry/concurrency case>, then <agreed behavior>.
- [ ] <Compatibility, operational, or other required constraint, when applicable.>

## Verification
- Local: <verified command or procedure, fixture, expected result>
- Integration/operational: <actual consuming boundary, environment, expected evidence>
- Limitations/gates: <what cannot be proven locally; owner and condition for remaining proof>

## Completion evidence
<Demo/result/artifact/review decision that makes acceptance assessable.
Include rollback/cutover evidence when relevant; never equate merged with proven.>
```

## Adapt supporting work

For discovery, replace implementation detail with the question, bounded investigation, alternatives to distinguish, evidence artifact, and decision rule. State which future slices need revision when the result arrives.

For a human decision, provide enough evidence/options for the named role to decide. Acceptance is a recorded decision and updated downstream constraints, not "discuss architecture."

For migrations or independent releases, specify staged compatibility and the observable release/cutover condition. Do not declare downstream work ready just because prerequisite code has merged.

## Compact completed example

This is a hypothetical system. Paths and executable commands must be discovered in the actual repository; the procedures below are concrete behavior checks, not claims about an existing test suite.

### S3: Cancel an unfinished export without exposing a late result

**Kind:** delivery. **Execution:** AFK after the lifecycle contract below is accepted. **Requirements:** R3, owners can cancel their unfinished exports. **Readiness:** ready after S1.

**Outcome:** an owner can cancel a queued or running export through the same surface used to request it. Cancellation remains effective if a worker finishes concurrently.

**Scope:** cancellation action, authorization, durable state transition, worker cooperation, download eligibility, and regression checks. Excludes automatic retries and retention policy changes.

**Prerequisite:** S1 provides a persisted job identity, owner identity, terminal job states, and authenticated download path. Coordinate edits to shared lifecycle code with S2; live progress refresh is not required.

**Proposed contract for this example:** cancellation is owner-only. A persisted transition into a terminal state wins atomically. Queued/running jobs may transition to cancelled. Repeated cancellation of a cancelled job is successful without additional effects. Cancellation after completed/failed reports a state conflict. A cancelled job cannot subsequently become completed or expose a download. Existing completed jobs retain their download behavior.

**Acceptance:**

- Owner cancels a queued job; it remains cancelled when a worker later claims it and no report is generated.
- Owner cancels a running job; late worker output is not published or downloadable.
- Repeat cancellation has no additional effect. Completed/failed jobs return the agreed state conflict.
- A different user cannot cancel the job or retrieve its output.
- Concurrent completion/cancellation yields exactly one terminal transition, with download eligibility matching that state.

**Verification:** use the repository's integration runner (command discovery required) to drive the request/cancel/status/download route with two authenticated fixture users and a controllable worker. Pause the worker before publishing; cancel, then release it. Run the reverse ordering as well. Assert terminal state and download response in both cases. Repeat through the actual user action to verify wiring; mocks alone do not prove worker or UI behavior.

**Evidence:** focused concurrency/authorization results and an integrated cancellation demonstration. If the worker environment is unavailable, report that limitation and retain the integration gate; local tests alone do not complete this issue.
