---
name: project-surface-curator
description: "Curate a project-local portfolio of skills, agents, and commands by analyzing the repo's real stack and workflows, then choosing what to keep, merge, trim, or delete. Use when a project has too many imported surfaces, off-stack tooling, duplicated guidance, or stale agent/command/skill assets and needs a leaner project-specific library without losing durable value."
---

# Project Surface Curator

Use this skill to turn a large mixed library into a lean project-specific surface.

The job is not just deletion. First identify what the project actually needs. Then preserve protected core surfaces, merge durable value into canonical survivors, and only delete what is truly off-stack, duplicated, stale, or low-value.

## Protected Core

Keep these by default unless the user explicitly asks otherwise and there is a clear local replacement:

- `skills/git-workflow`
- `skills/skill-optimizer`
- code-review surfaces such as `agents/code-reviewer.md`, `commands/code-review.md`, or the nearest local equivalent

If one of these is missing, call it out instead of silently dropping the protection rule.

## Core Rules

- Use the repository, not taste, as the source of truth.
- Analyze requirements and current stack before classifying anything.
- Inventory skills, agents, and commands separately.
- Prefer one strong canonical surface over multiple overlapping thin ones.
- Merge durable value before deleting a donor surface.
- Delete only after the user approves the exact keep, merge, and delete set.
- Edit canonical project-library paths, not tool-specific mirrors or symlink targets.
- Keep the result lean enough for daily use, but not so lean that it loses core operator workflows.

## Workflow

### 1. Read the Project First

Establish the real usage surface before reviewing the library:

- languages and runtimes in use
- frameworks and infra in use
- CI, deployment, and local test surfaces
- domain-specific workflows repeated in the repo
- current agent/skill/command wiring

Use repo evidence such as manifests, file extensions, CI config, docs, imports, and active source trees.

### 2. Build the Surface Inventory

Inventory these buckets independently:

- `skills/*`
- `agents/*`
- `commands/*`

For each item, capture:

- path
- type
- current role
- repo evidence for or against keeping it
- overlap with another surface
- proposed action: `keep`, `merge-into`, `trim`, `delete`

### 3. Identify Canonical Survivors

Choose the smallest set of survivors that still covers:

- repo-specific workflows
- active language and framework workflows
- protected core workflows
- review and maintenance workflows needed to keep the library healthy

Promote to `keep` when a surface is clearly aligned with the project and strong enough to remain the canonical home for that workflow.

Mark as `merge-into` when a surface has useful content but should not survive as its own item.

Mark as `delete` when a surface is off-stack, stale, redundant, purely imported noise, or superseded locally.

### 4. Salvage Before Delete

For every `merge-into` or high-value `delete` candidate:

1. Read the donor and the target together.
2. Extract only durable, non-duplicative guidance.
3. Merge that value into the canonical target using the target's structure and tone.
4. Drop bulky examples, marketing copy, framework-specific digressions, and content the model already knows.

Good salvage targets:

- validation checklists
- repo-fit trigger wording
- stable workflow steps
- important failure-mode warnings
- concise decision rules

Bad salvage targets:

- long tutorials
- broad conceptual background
- off-stack examples
- repeated command lists
- stale setup docs

### 5. Approval Checkpoint

Before destructive cleanup, return an explicit proposal with:

- stack summary
- protected core surfaces
- keep set
- merge map: `donor -> canonical target`
- delete set
- reference/wiring files that must be updated
- verification plan

Do not delete until the user approves.

### 6. Apply the Trim

After approval:

- update surviving skills, agents, and commands first
- fix stale references to deleted surfaces
- remove the approved delete set
- leave unrelated worktree changes untouched

When commands or agents reference removed skills, either repoint them to surviving surfaces or note that the command layer still needs a later cleanup pass.

### 7. Verify the Result

After edits and deletions, verify:

- surviving inventory matches the approved keep set
- merged targets still parse and keep required frontmatter
- no obviously broken references remain in kept surfaces
- protected core surfaces still exist
- the remaining portfolio still covers stack, review, git workflow, and maintenance needs

Use lightweight static checks first, then targeted grep for stale paths or removed names.

## Output Format

Return results in this order:

```text
STACK
- repo evidence summary

PROTECTED CORE
- surfaces kept by policy

KEEP
- surviving surfaces with evidence

MERGE
- donor -> target with salvaged value summary

DELETE
- removed surfaces with reason

VERIFICATION
- checks run
- remaining gaps
```

## Notes

- If the user wants planning only, stop after the approval proposal.
- If the user wants implementation, still preserve the approval checkpoint before deletion.
- If an existing skill already covers only one part of this workflow, reuse it as an input, not as the whole solution.
