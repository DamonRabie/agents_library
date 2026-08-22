---
name: skill-optimizer
description: Optimize an existing repo skill portfolio or create missing skills by using recent git commits as the demand signal. Use when the user wants to improve skills, reduce skill token bloat, remove redundant skill content, evolve skills from commit history, or identify missing skills for recurring workflows.
origin: internal project
---

# Skill Optimizer

Use this skill to keep `.agent-library/skills` lean, useful, and grounded in the work the repo actually does.

Default mode is approval-first: analyze evidence, propose exact creates/updates/trims, then wait for the user before editing existing skills or adding new ones.

## Core Rules

- Target `.agent-library/skills` by default.
- Preserve symlinks and edit canonical `.agent-library` files, not copied tool-specific entrypoints.
- Keep shared guidance model-neutral unless a tool-specific contract is required.
- Prefer improving an existing skill over creating a new one when the workflow is already covered.
- Optimize for the sweet spot: enough procedural detail to improve task quality, little enough text to avoid context bloat.
- Do not store raw commit dumps in skills. Extract durable patterns and cite compact evidence.

## Evidence Pass

Start with non-mutating collection:

```bash
git log --name-only --pretty=format:'COMMIT %H %ad %s' --date=short -n 200
find .agent-library/skills -maxdepth 2 -name SKILL.md | sort
rg -n "name:|description:|## When|## Core|## Workflow|git log|commit|token|redund" .agent-library/skills
```

When useful, add focused checks:

```bash
git log --oneline -n 200
git log --name-only --pretty=format: -n 200 | sed '/^$/d' | sort | uniq -c | sort -rn | head -40
wc -l .agent-library/skills/*/SKILL.md | sort -nr | head -30
```

Read adjacent skills before deciding:

- `skill-creator` for valid skill structure and progressive disclosure.
- `skill-stocktake` for portfolio-quality verdicts.
- `agent-sort` for repo-fit classification.
- `context-budget` for token and redundancy pressure.
- `knowledge-ops` for model-neutral storage and symlink rules.

## Demand Analysis

Group recent commits into workflow clusters:

- repeated file families, such as ClickHouse SQL, Spark apps, YAML descriptions, DAGs, or agent-library assets
- repeated commit messages, such as stage-to-production syncs, format fixes, lag changes, logging additions, or new data sources
- files that change together
- fixes that indicate missing validation guidance
- new capabilities with no matching skill

Treat a cluster as skill-worthy only when it is recurring, durable, and actionable across future tasks.

## Action Decision

Assign one action per cluster:

| Action | Use When |
|---|---|
| Improve existing | A matching skill exists but lacks current workflow, validation, edge cases, or repo-specific guidance. |
| Create missing | Repeated work has no skill and would benefit from reusable procedure. |
| Trim | A skill is long, generic, duplicated elsewhere, or loaded with examples that do not affect execution. |
| Merge | Two or more skills cover the same workflow and one canonical skill would be clearer. |
| No action | The pattern is one-off, already covered, or too narrow for a skill. |

Prefer `Improve existing` over `Create missing`; prefer `Trim` over adding references unless detail is truly needed.

## Skill Quality Bar

Every proposed skill change must improve at least one of these:

- trigger accuracy in frontmatter description
- task workflow clarity
- repo-specific correctness
- validation and failure-mode coverage
- token efficiency
- removal of duplicate or stale guidance

Good skills:

- have a strong `name` and `description`
- start with a concise purpose
- give ordered actions and decision rules
- reference commands only when they materially help
- keep examples short
- avoid generic best-practice filler
- include validation appropriate to the risk

Bad skills:

- repeat `AGENTS_MEMORY.md`, rules, or another skill
- explain concepts a capable agent already knows
- preserve upstream marketing language
- hard-code model-specific behavior into shared repo guidance
- create a new surface for a workflow already covered nearby

## Approval Plan Format

Before edits, return a compact plan:

```text
SKILL OPTIMIZATION PLAN

Evidence:
- commits reviewed: <N>
- strongest workflow clusters: <cluster names>
- existing skills checked: <skill names>

Proposed actions:
1. Improve <skill>: <specific change>; evidence: <commit/file pattern>; token goal: <target>
2. Create <skill>: <missing workflow>; evidence: <commit/file pattern>; initial shape: <sections>
3. Trim <skill>: <duplicated or stale content>; token goal: <target>

Skipped:
- <cluster>: <why no skill change>

Validation:
- frontmatter parse
- stale-reference search
- targeted trigger examples
```

Only implement approved actions. Retire, merge, or delete operations always need explicit approval.

## Implementation Rules

When creating a skill:

- folder name is lowercase hyphen-case
- create only `SKILL.md` unless scripts/references/assets are necessary
- use YAML frontmatter with `name`, `description`, and `origin`
- keep `SKILL.md` under 200 lines unless the domain is complex
- include no README, changelog, or setup notes

When improving a skill:

- edit in place
- preserve useful local conventions
- remove duplicated prose rather than adding around it
- move details to references only when they are large and selectively needed
- update model-specific metadata only if that metadata exists and is stale

When trimming:

- remove generic explanation first
- remove repeated examples second
- preserve trigger wording, critical workflow steps, validation, and repo-specific gotchas
- state expected token or line-count savings in the plan

## Validation

After approved edits:

```bash
python - <<'PY'
from pathlib import Path
for p in Path('.agent-library/skills').glob('*/SKILL.md'):
    text = p.read_text()
    assert text.startswith('---\n'), p
    head = text.split('---', 2)[1]
    assert 'name:' in head and 'description:' in head, p
print('skill frontmatter present')
PY
```

Run a targeted stale-reference search for old memory paths, default global Claude skill paths, upstream attribution footers, and unfinished-work markers. Report any warnings instead of hiding them.
