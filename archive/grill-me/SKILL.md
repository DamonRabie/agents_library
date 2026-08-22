---
name: grill-me
description: Interview the user to turn a vague request, project idea, architecture proposal, ML/data workflow, or implementation plan into a clear, risk-aware, implementation-ready plan.
---

# Grill Me

Use this skill when the user wants to be interviewed, challenged, or pushed from an initial idea toward a precise implementation plan.

The primary output is clarity and an actionable plan, not documentation. Do not create or update docs by default. Mention docs, ADRs, runbooks, or tickets only when they are necessary implementation artifacts or the user explicitly asks for them.

## Core Behavior

Interview the user one decision at a time until the project is precise enough to implement.

For each question:

- ask exactly one unresolved decision at a time
- explain briefly why the question matters
- give a recommended answer when codebase evidence or engineering judgment supports one
- inspect local code, configs, docs, and existing patterns instead of asking when the answer is discoverable
- wait for the user's answer before moving to the next unresolved decision
- turn vague language into concrete terms, contracts, and acceptance criteria

Do not jump straight to implementation. The session ends when the implementation plan is clear enough that an engineer can start work without major hidden assumptions.

## Review Lens

Challenge the idea around:

- outcome: user, business, product, research, or operational result the project must improve
- scope: what is included, excluded, deferred, owned here, or delegated to another system
- users and consumers: who uses the result, who depends on it, and who owns it after launch
- inputs: source of truth, freshness, access, quality assumptions, and failure modes
- output contract: API, artifact, table, model, UI, event, report, or workflow shape downstream users depend on
- state and data semantics: keys, grain, identity, lifecycle, nulls, deduplication, ordering, retention, and backfill behavior
- design options: reasonable alternatives, trade-offs, and why the chosen approach should win
- correctness risks: edge cases, race conditions, leakage, migration hazards, security, privacy, and compliance
- evaluation: baseline, success metric, acceptance gate, failure slices, and rollback criteria
- implementation: modules, boundaries, dependencies, migration path, sequencing, and integration points
- operations: deployment path, scheduling, monitoring, alerting, cost, scaling, ownership, and cleanup
- validation: cheapest useful smoke, synthetic, unit, integration, contract, or end-to-end test

## Question Flow

Use this order as a default. Skip questions already answered by repo evidence or the user's previous answers.

1. What exact outcome should this project produce, and for whom?
2. What is out of scope for the first implementation?
3. What existing code, data, service, workflow, or manual process does this replace or extend?
4. What are the source-of-truth inputs, and what assumptions do we make about their quality and availability?
5. What output contract must be stable for consumers?
6. What are the major edge cases and failure modes?
7. What design alternatives are realistic, and what trade-off decides between them?
8. What metric, acceptance test, or business rule proves the work is useful?
9. What needs to be reproducible or configurable?
10. How will this run, deploy, monitor, and roll back in production?
11. What is the smallest validation that catches the main failure mode?
12. What is the implementation sequence, including dependencies and checkpoints?

## Implementation Plan Output

When the grilling session is complete, produce a concise implementation plan with:

- goal and non-goals
- assumptions confirmed during the interview
- proposed design and rejected alternatives
- input and output contracts
- implementation steps in order
- validation and acceptance criteria
- operational considerations
- risks and mitigations
- open questions, if any, that still block execution

If the user asks to continue into implementation, use this plan as the working checklist.

## Optional Artifacts

Only propose documentation artifacts when they materially reduce future ambiguity or are needed for project execution:

- issue or ticket body for team handoff
- contract doc for stable interfaces, data, or artifacts
- runbook for operational ownership
- ADR for hard-to-reverse decisions with real alternatives

Use `CONTEXT-FORMAT.md` and `ADR-FORMAT.md` only when one of those optional artifacts is explicitly needed.
