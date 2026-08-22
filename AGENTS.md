# Repository Guidelines

## Project Structure & Module Organization
This repository is a shared library of reusable agent assets. Keep the canonical content here and consume it from other tools through symlinks rather than duplicate copies. If local tool entrypoints such as `.agents/` or `.codex/` need skill access, point them at this repository with symlinks instead of maintaining mirrored copies. Primary folders:

- `skills/<skill-name>/SKILL.md`: main skill instructions, often with `agents/`, `scripts/`, `references/`, `assets/`, `fixtures/`, or `tests/`
- `archive/<skill-name>/SKILL.md`: retired or downloaded micro-skills kept as searchable source material; do not symlink these into consumers
- `commands/*.md`: slash-command style prompts and workflows
- `agents/`: standalone agent definitions not tied to a single skill
- `SOURCES.md`: provenance registry for imported or adapted material

The active install surface is the curated super-skill portfolio under `skills/`. Add broadly reusable lessons to the relevant super skill's `data/*.csv` when possible, or to the consuming repo's memory file when repo-specific. Create a new skill only when the domain is not covered by the current super-skill set.

## Build, Test, and Development Commands
There is no root build pipeline. Use lightweight inspection and skill-local validation instead:

- `rg --files skills commands agents`: inventory repository content quickly
- `find skills -maxdepth 2 -name 'SKILL.md'`: inspect skill packages
- `git diff --check`: catch whitespace and merge-marker issues before review
- `cd skills/skill-comply && pytest`: run the checked-in Python tests when editing that subproject
- `cd skills/skill-comply && uv run python -m scripts.run --dry-run <path>`: dry-run compliance tooling against a target Markdown asset

## Coding Style & Naming Conventions
Prefer Markdown-first, portable instructions. Use ASCII unless a file already requires Unicode. Name skill directories in `kebab-case`; the entry file must be `SKILL.md`. Keep tool-specific adapters additive, for example `skills/<name>/agents/openai.yaml`. When wiring consumers, prefer links such as `.agents/skills -> ../skills` or `.codex/skills -> ../skills` so both tools read the same source files. Preserve or add frontmatter for imported content when applicable: `origin`, `source_name`, `source_url`, `license`, `adaptation`.

## Testing Guidelines
For documentation changes, manually verify headings, links, and example paths. If a skill includes executable code, keep tests local to that skill, typically under `skills/<name>/tests/`, and follow `test_*.py` naming. Update fixtures alongside behavior changes. There is no repo-wide coverage gate today; run the narrowest relevant suite.

## Commit & Pull Request Guidelines
This repository has no established commit history yet, so use short imperative subjects such as `Add source entry for imported skill`. Keep commits scoped to one library concern. Pull requests should summarize affected paths, note whether content is copied or adapted, and update `SOURCES.md` whenever provenance changes. Include screenshots only when changing visual assets or rendered documentation output.
