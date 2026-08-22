---
name: to-prd
description: Turn the current conversation context and codebase understanding into a PRD and optionally publish it to the project issue tracker; use when the user wants Codex to synthesize a PRD from existing context without a broad interview, including problem, solution, extensive user stories, implementation decisions, testing decisions, out-of-scope items, and follow-up notes.
origin: Local
---

# To PRD

Use this skill when the user wants the current conversation, plan, investigation, or codebase context turned into a PRD. Synthesize what is already known. Do not run a broad interview or restart discovery from scratch.

## Core Rules

- Work from existing conversation context first.
- Explore the repo when needed to understand current implementation state, domain glossary, ADRs, docs, and prior art.
- Use the project's current domain language instead of generic product wording.
- Respect existing architecture, artifact contracts, label/split/metric contracts, and experiment-tracking evidence requirements.
- Do not include brittle file paths or code snippets unless a prototype produced a decision-rich contract that prose would make ambiguous.
- Before writing the final PRD, check the proposed modules and test targets with the user. This is not a broad interview; it is a focused confirmation step.

## Process

1. **Gather Context**
   - Use the current conversation and any referenced docs, issues, artifacts, or branches.
   - If the user passes an issue reference, URL, or path, fetch/read the full body and comments when available.
   - If issue tracker and triage label vocabulary are missing and publishing is requested, inspect the docs/tooling or ask the user for the missing tracker details.

2. **Explore The Repo**
   - Inspect the relevant project area when needed: repo instructions, ADRs, domain docs, nearby implementation modules, shared utilities, and tooling.
   - Identify the current state: what exists, what is partial, what is missing, and what prior tests or ledgers already cover.
   - Use the project's domain glossary throughout the PRD.

3. **Sketch Major Modules**
   - Identify major modules or workflow surfaces that need to be built or modified.
   - Actively look for deep modules: components that encapsulate meaningful behavior behind a simple, testable interface that should rarely change.
   - Prefer deep modules for validation-heavy data contracts, such as label validation, artifact manifests, import/export transforms, semantic audit checks, and metric contract formatting.
   - Present the module sketch to the user and ask:
     - Do these modules match your expectations?
     - Which modules should have tests?

4. **Write The PRD**
   - Use the template below.
   - Make user stories extensive and numbered.
   - Frame implementation decisions as durable decisions, not a file-by-file task list.
   - Name testing decisions clearly, including what external behavior should be tested and what implementation details should be ignored.

5. **Publish Only When Requested Or Approved**
   - If the user asked for a file PRD, write a markdown file in the relevant docs area and report the path.
   - If the user asked to publish to the issue tracker, publish after the focused module/test confirmation step.
   - Apply approved triage or readiness labels only when publishing is requested and label vocabulary is known.
   - Do not close, edit, or relabel unrelated parent issues unless explicitly asked.

## PRD Template

```markdown
# <Clear PRD Title>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A long, numbered list of user stories. Each story must use:

1. As an <actor>, I want a <feature>, so that <benefit>

The list should be extensive and cover all aspects of the feature, including operators, reviewers, model developers, downstream consumers, and future agents where relevant.

## Implementation Decisions

A list of durable implementation decisions, including:

- Modules that will be built or modified
- Interfaces or contracts that will change
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API or artifact contracts
- Specific workflow interactions

Do not include specific file paths or code snippets. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can, inline only the decision-rich part and note that it came from a prototype.

## Testing Decisions

A list of testing decisions, including:

- What makes a good test for this PRD
- Which modules will be tested
- Which tests should verify external behavior rather than implementation details
- Prior art for similar tests in the codebase

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.
```

## PRD Quality Bar

- The PRD states the final user-visible or operator-visible outcome.
- It names the data evidence trail: artifacts, checksums, tracked runs, ledgers, and acceptance gates.
- It captures label, split, metric, schema, and reproducibility assumptions when relevant.
- It separates HITL decisions from AFK implementation work.
- It is complete enough that `to-issues` can later produce a requirement coverage map and vertical issue slices without rediscovering the full context.
