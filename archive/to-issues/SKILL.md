---
name: to-issues
description: Meticulously analyze a PRD, plan, issue, experiment wave, or refactor and convert it into complete, dependency-aware vertical issue slices that achieve the source goal end to end; use when Codex must map requirements, find missing work, classify HITL vs AFK slices, ask for approval, and optionally publish approved issues.
origin: Local
---

# To Issues

Do not merely split text into small tickets. First understand the intended end state, compare it with work already done, identify missing requirements, and design vertical slices that collectively deliver the goal. A good output lets the user see whether the plan actually reaches the PRD outcome before anything is published.

## Required Mindset

- Treat the source document as a contract. Extract requirements, acceptance gates, artifacts, operational decisions, and blockers before drafting issues.
- Map already-developed work separately from missing work. Do not create duplicate issues for work already completed unless the source goal remains unmet.
- Make completeness explicit. Produce a coverage map that shows which requirement is covered by which issue and where gaps remain.
- Prefer tracer-bullet vertical slices. Each issue should deliver a narrow but complete path through all relevant layers needed for that slice: data/schema, pipeline logic, artifact contract, validation/tests, docs/ledger, and operational evidence.
- Mark slices as `AFK` or `HITL`.
  - `AFK`: an agent can implement, validate, and merge without additional human judgment.
  - `HITL`: human review, data labeling, product/taxonomy judgment, architecture decision, or approval is inherently required.
- Ask for user approval before publishing or editing tracker issues unless the user explicitly says to publish without review.
- Treat user corrections as constraints, not suggestions. When the user merges, splits, reorders, removes validation gates, or changes blocking relationships, update the full issue set and dependency chain before publishing.
- Keep tracker state deliberate. Labels, milestones, assignees, workflow states, and readiness markers must be explicitly approved or verified from existing tracker conventions before use.

## Process

1. **Gather Context**
   - Use the conversation context first.
   - If the user passes a PRD path, issue number, URL, branch, or artifact path, read it fully.
   - If the user passes an issue reference, fetch the issue body and comments from the configured tracker when access is available.
   - Read the relevant domain ledger/progress doc when the PRD references one.

2. **Explore The Codebase When Needed**
   - Inspect current code, docs, artifacts, and open/closed issues enough to understand what already exists.
   - Use the project's domain glossary in issue titles and descriptions.
   - Respect ADRs and domain docs in the area being touched.
   - For data-heavy work, check whether artifacts are local working copies or tracked evidence.

3. **Build A Requirement Coverage Map**
   - List the source requirements and final outcome.
   - For each requirement, mark:
     - `covered`: existing completed/developed work already satisfies it.
     - `partial`: existing work helps but does not reach the requirement.
     - `missing`: new or updated work is required.
   - Call out contradictions, missing artifacts, undocumented assumptions, and silent failure modes.
   - Do not proceed to issue drafting until the coverage map makes the remaining work clear.

4. **Draft Vertical Slices**
   - Break only the missing or partial work into tracer-bullet issues.
   - Each slice must be independently demoable or verifiable.
   - Prefer many thin complete slices over one thick issue, but do not make horizontal layer-only tickets such as "write tests", "update docs", or "add API" unless that is the full deliverable.
   - Include all needed validation and evidence inside the slice, not as a later afterthought.
   - Preserve dependencies from existing issues and from the actual workflow.

5. **Quiz The User**
   Present the proposed breakdown as a numbered list before publishing. For each slice show:
   - Title
   - Type: `HITL` or `AFK`
   - Blocked by
   - User stories or PRD requirements covered
   - Why this slice is necessary for the final goal

   Ask:
   - Does the granularity feel right: too coarse, too fine, or correct?
   - Are the dependency relationships correct?
   - Should any slices be merged or split further?
   - Are the correct slices marked `HITL` and `AFK`?

   Iterate until the user approves the breakdown. If the user gives edits, restate the resulting final issue set before publishing when the edits materially change granularity, order, issue type, validation scope, or dependency relationships.

6. **Publish Only After Approval**
   - Publish approved issues in dependency order so real issue identifiers can be referenced in downstream `Blocked by` sections.
   - Do not close, edit, or relabel parent issues unless explicitly asked.
   - If the user approves publishing but not readiness labels, publish with the domain label only.
   - Use the actual issue identifiers returned by the tracker. Never assume identifiers are contiguous or predictable.
   - When textual dependencies need both upstream and downstream references, publish with placeholders only where unavoidable, then patch descriptions after all needed identifiers exist.
   - Read back each created or edited issue and verify the title, state, labels, description, and dependency text.
   - If an accidental description, label, milestone, assignee, or workflow-state change is detected during readback, correct it immediately when the intended state is unambiguous.

## Issue Quality Gate

Before presenting issues, check that the set as a whole reaches the source goal:

- Every PRD requirement is covered by at least one existing item or proposed issue.
- Every proposed issue has a concrete verification path.
- HITL work is explicit and not hidden inside AFK tickets.
- Data and model contract risks are named where relevant: leakage, label semantics, split timing, metric compatibility, artifact reproducibility, and experiment evidence.
- The final slice produces the promised end-state artifact or decision, not just an intermediate report.

## Issue Template

Use this body for approved issues:

```markdown
## Parent

<A reference to the parent issue on the issue tracker if the source was an existing issue. Omit this section if there is no parent.>

## What to build

<A concise description of this vertical slice. Describe end-to-end behavior, not layer-by-layer implementation. Avoid specific file paths or code snippets unless a prototype produced a decision-rich snippet that is more precise than prose.>

## Type

<AFK or HITL>

## Requirements covered

- <Source requirement or user story covered by this slice>

## Acceptance criteria

- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] <Criterion 3>

## Validation

- Command: `<exact command, "requires external data/service", or "requires human review">`
- Expected evidence: <row counts, schema, metric keys, tracked run, reviewed artifact, ledger update, tracker note, or doc update>

## Blocked by

<Issue references or "None - can start immediately">

## Blocks

<Issue references or "None">
```

## Data/Remote Issue Checks

- State data source, artifact contract, split/label assumptions, and experiment evidence requirements when relevant.
- Include sample/synthetic validation before full external-data or remote-compute work.
- Require docs updates when data labels, splits, metrics, artifact schemas, or operational decisions change.

## Tracker Rules

- Use the tracker CLI or documented project tooling when credentials, project id/path, and issue tooling are available.
- If tracker access is not configured in the current session, draft the issues locally and state exactly what is needed to publish them.
- Do not invent labels, milestones, assignees, readiness labels, or project paths. Read existing tracker metadata first when tooling supports it.
- Before referencing any pre-existing issue, fetch it from the project and verify it is the intended open issue. Do not infer issue identity from a number alone.
- Do not assume native blocking links are supported. Check the available CLI help; if native blocking cannot be created, record dependencies explicitly in `## Blocked by` and `## Blocks` sections.
- Publish issues first, read back each created issue, and verify state, title, labels, project path, and description before writing dependency references.
- Use the issue reference syntax required by the configured tracker. Do not use merge-request or pull-request syntax unless the user explicitly asked for it.
- Prepare issue bodies in temporary files or another reviewable local form before creation when the tracker CLI supports file-backed descriptions. Verify the CLI syntax for file-backed fields before creating issues; some CLIs treat literal values and file references differently.
- Do a final readback after dependency patches. Confirm no placeholder text remains and that upstream `Blocks` and downstream `Blocked by` sections agree.

## Labels

- Every published issue should have one project/domain label when the domain is clear.
- Prefer existing labels to new labels, and match the label vocabulary already used by the tracker.
- Treat readiness labels and automation labels as workflow state. Apply them only when the user explicitly approves them during the publishing step.
- Some trackers or templates may add default labels automatically. Read back labels after creation and remove unapproved workflow labels when the intended label set is clear.
- If the intended label is missing, do not silently create it. Ask before creating the label unless the user explicitly instructed you to create missing labels.
- If an issue spans multiple domains, choose the dominant deliverable's project label and mention the secondary area in the issue body rather than applying many project labels.
