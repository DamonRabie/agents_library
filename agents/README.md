# Agents

Home for standalone agent definitions that are not bundled inside a specific skill.

This directory is part of a shared library intended to be consumed by tools through symlinks, not duplicated into separate tool-specific repositories.

Use this directory for:

- reusable agent specs shared by multiple skills
- agent prompts that should exist independently of a skill
- platform-specific agent adapters when the core logic lives elsewhere

Suggested layout:

```text
agents/
  <agent-name>/
    README.md
    openai.yaml
    claude.md
```

If an agent is imported or adapted from another source, add an entry to `../SOURCES.md` and keep source metadata close to the agent definition when possible.
