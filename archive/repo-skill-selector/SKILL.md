---
name: repo-skill-selector
description: "Select, trim, and retire skills for a project-specific skill portfolio. Use when auditing a large local skill library, reducing load warnings, deciding which skills to keep for this repo, removing off-stack skills, or reorganizing skills into project-fit, workflow, utility, and retire buckets. Always preserve useful guidance or scripts by migrating them into surviving skills before deleting or retiring a skill."
---

# Repo Skill Selector

Use this skill when the repo has too many skills and you need a safe, project-fit selection pass.

Target the local project skill library first:
- `.agent-library/skills`

The goal is not to keep only daily-use skills. The goal is to keep the skills that improve this repo’s engineering work without carrying unrelated stacks.

## Core Selection Rules

Keep:
- development skills that match the repo stack and architecture
- utility skills that improve agentic coding, such as creating skills, portfolio review, context management, debugging, and evaluation
- workflow skills for planning, commit flow, task management, review, and validation
- general skills that can become useful here with small modification

Retire:
- skills centered on technologies the repo does not use
- broad duplicate skills that are fully covered by sharper repo-fit skills
- skills whose useful content can be migrated cleanly into other skills

Before deleting or retiring a skill:
- check whether it contains useful workflow guidance
- check whether it contains useful scripts or references
- migrate useful material into the most appropriate surviving skill first
- only then delete or retire it

## Workflow

### 1. Read the repo before classifying skills

Establish:
- backend stack
- frontend stack
- test stack
- deployment/runtime surface
- recurring repo workflows

Use the repo, not generic preferences, as the source of truth.

### 2. Classify each skill into one action

Use one of:
- `Keep`
- `Improve`
- `Trim`
- `Retire`

Prefer:
- `Improve` over creating a replacement skill
- `Trim` over keeping a long generic version
- `Retire` only after useful content has a new home

### 3. Apply the keep rules

Keep a skill when it is:
- directly aligned with the repo stack
- useful for agentic coding quality or context control
- part of the repo’s workflow surface such as commit, plan, review, testing, or debugging
- general enough to stay useful after small repo-specific modification

### 4. Apply the retire rules

Retire a skill when it is:
- centered on off-stack languages, frameworks, platforms, or business domains
- a broad wrapper that adds ambiguity over sharper repo-fit skills
- no longer unique after useful parts are extracted elsewhere

### 5. Migrate useful content before deletion

For any skill marked to retire:
- inspect `SKILL.md`
- inspect `scripts/`
- inspect `references/`
- identify any durable guidance worth keeping

Then:
- move backend-relevant guidance into `backend-patterns`, `security-review`, `python-testing`, or similar
- move frontend-relevant guidance into `frontend-patterns`, `dashboard-builder`, `playwright-pro`, or similar
- move workflow guidance into `commit`, `git-workflow`, `code-reviewer`, `context-budget`, or similar

Do not retire a skill just because it is broad if it still contains unique, useful material that has not been migrated.

## Evaluation Checklist

- does this skill match the repo’s actual stack?
- does this skill improve agentic coding or workflow quality?
- is this skill duplicated by a sharper surviving skill?
- can this skill be made useful with a small repo-fit rewrite?
- if retiring it, did we preserve any useful guidance, scripts, or references?

## Output Format

Return decisions in four groups:

```text
KEEP
- <skill>: <why>

IMPROVE
- <skill>: <what to change>

TRIM
- <skill>: <what to remove>

RETIRE
- <skill>: <what replaces it and what was migrated first>
```

## Related Skills

- `agent-sort`
- `skill-optimizer`
- `skill-stocktake`
- `context-budget`
- `knowledge-ops`
