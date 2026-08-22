# Sources

Registry of imported, adapted, or source-inspired material in this library.

Use this file to keep a durable record of provenance even when the local asset has been renamed, restructured, or heavily edited.

## How To Use

- Add one entry for each imported skill, command, or standalone agent.
- Update the entry when the local file moves or the adaptation becomes substantial.
- Keep the file path current.
- Prefer concrete URLs over vague source names.

## Entry Template

```md
## local-item-name
- Type: skill | command | agent
- Path: skills/local-item-name/SKILL.md
- Status: copied | adapted | inspired-by
- Source: Example Project / Author
- URL: https://github.com/example/project
- License: MIT
- Notes: What changed locally and why
```

## Registered Sources

## blueprint
- Type: skill
- Path: skills/blueprint/SKILL.md
- Status: inspired-by
- Source: antbotlab/blueprint
- URL: https://github.com/antbotlab/blueprint
- License: unknown
- Notes: The local skill already notes upstream inspiration and uses this project as a reference design.

## code-review
- Type: command
- Path: commands/code-review.md
- Status: adapted
- Source: PRPs-agentic-eng by Wirasm
- URL: unknown
- License: unknown
- Notes: The command already states that PR review mode was adapted from this workflow.

## code-explorer
- Type: agent
- Path: agents/code-explorer.md
- Status: adapted
- Source: Internal project-local agent library
- URL: unavailable
- License: unknown
- Notes: Imported as a model-neutral standalone agent prompt and kept focused on pre-implementation codebase analysis.

## code-reviewer-agent
- Type: agent
- Path: agents/code-reviewer.md
- Status: adapted
- Source: Internal project-local agent library
- URL: unavailable
- License: unknown
- Notes: Imported as a standalone reviewer prompt to satisfy agent references used by shared commands while avoiding tool-specific metadata.

## planner
- Type: agent
- Path: agents/planner.md
- Status: adapted
- Source: Internal project-local agent library
- URL: unavailable
- License: unknown
- Notes: Imported as a general planning agent because shared commands already reference `agents/planner.md`.

## python-reviewer-agent
- Type: agent
- Path: agents/python-reviewer.md
- Status: adapted
- Source: Internal project-local agent library
- URL: unavailable
- License: unknown
- Notes: Imported as a Python-specific review agent with tool-neutral wording.

## clickhouse-io
- Type: skill
- Path: skills/clickhouse-io/SKILL.md
- Status: adapted
- Source: Internal project-local skill library
- URL: unavailable
- License: unknown
- Notes: Added generalized exploratory-query and failure-mode guidance while stripping repo-specific table and path references.

## deployment-patterns
- Type: skill
- Path: skills/deployment-patterns/SKILL.md
- Status: adapted
- Source: Internal project-local skill library
- URL: unavailable
- License: unknown
- Notes: Added environment-asset promotion workflow and validation guidance derived from stage-to-production sync practices.

## senior-ml-engineer
- Type: skill
- Path: skills/senior-ml-engineer/SKILL.md
- Status: adapted
- Source: Internal project-local skill library
- URL: unavailable
- License: unknown
- Notes: Added reusable training-artifact discipline and registry handoff guidance while removing project-specific repo structure and helper assumptions.

## mlflow-model-registration
- Type: skill
- Path: skills/mlflow-model-registration/SKILL.md
- Status: adapted
- Source: Internal project-local skill pack
- URL: unavailable
- License: unknown
- Notes: Reworked a project-specific MLflow registration notebook into a general workflow for artifact verification, pyfunc registration, and operator handoff.

## senior-data-scientist-ml-yearning
- Type: skill
- Path: skills/senior-data-scientist/SKILL.md
- Status: inspired-by
- Source: Andrew Ng, Machine Learning Yearning
- URL: unavailable local source
- License: All rights reserved
- Notes: Added dev/test set strategy, primary-vs-guardrail metric guidance, and manual error-analysis workflow derived from the book's ML project strategy chapters.

## senior-ml-engineer-ml-yearning
- Type: skill
- Path: skills/senior-ml-engineer/SKILL.md
- Status: inspired-by
- Source: Andrew Ng, Machine Learning Yearning
- URL: unavailable local source
- License: All rights reserved
- Notes: Added bias-variance-data-mismatch diagnosis rules and an end-to-end vs pipeline decision rubric synthesized from the book.

## eval-harness-ml-yearning
- Type: skill
- Path: skills/eval-harness/SKILL.md
- Status: inspired-by
- Source: Andrew Ng, Machine Learning Yearning
- URL: unavailable local source
- License: All rights reserved
- Notes: Added optimizing-vs-satisficing metric guidance and eval-set distribution advice generalized from the book.
