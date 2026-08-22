---
name: curate-from-source
description: Curate this shared skills, agents, and commands library from an external source such as a skill pack, repo, docs set, book, standard, or article. Use when Codex needs to inspect source material, decide what is durable and generalizable, reject project-specific knowledge, then merge into existing library assets or create/enrich new ones with provenance and a high evidence bar.
---

# Curate From Source

Turn a provided source into high-quality updates for the shared library. The goal is not faithful copying. The goal is durable, general-use guidance with clear provenance.

## Core Rules

- Treat this repository as the canonical library. Edit the source files here, not symlinked mirrors used by Claude Code or Codex.
- Import only knowledge that is durable across projects.
- Do not transfer project-specific details unless they can be rewritten into a general pattern without leaking local assumptions.
- Prefer improving an existing skill, command, or agent over creating a near-duplicate.
- Preserve provenance for imported or adapted material in the target file when possible and in `SOURCES.md`.
- Keep the library model-neutral by default. Add tool-specific wrappers only when they are thin adapters around shared logic.
- Do not promote weak, stale, promotional, or unverified claims into canonical guidance.

## Workflow

### 1. Classify the source

Identify:

- source type: skill pack, repository, documentation set, book, paper, standard, article, notes
- authority: primary, secondary, or mixed
- scope: single workflow, domain reference, broad collection
- trust constraints: license, confidentiality, or unclear provenance

If the source is long, mixed, or ambiguous, read `references/source-triage.md` before deciding what to transfer.

If the source appears confidential, proprietary, or license-restricted in a way that makes reuse unsafe, stop and ask before importing.

### 2. Extract only transferable knowledge

Look for reusable:

- workflows
- decision rules
- validation checklists
- failure modes
- reference patterns
- agent prompts
- command structures

Classify each candidate as:

- `durable-general`: safe to reuse across many projects
- `conditional-general`: reusable after rewriting or scoping
- `project-specific`: keep out of this library

Drop `project-specific` content. Rewrite `conditional-general` content into neutral, reusable instructions before merging it.

### 3. Decide the library action

Choose one action per candidate:

- `merge`: an existing skill or command already covers the workflow and should be improved
- `create`: the workflow is missing and durable enough to justify a new asset
- `enrich`: add references, examples, or validation depth to an existing asset without changing scope
- `skip`: the content is too narrow, too weak, too redundant, or too project-specific

Prefer `merge` over `create`. Prefer `skip` over adding shallow or duplicate material.

### 4. Implement the update

When updating the library:

- preserve the shared Markdown-first structure
- normalize names, layout, and language to fit this repository
- remove local paths, repo names, internal team language, secrets, environment assumptions, and one-off operational details
- convert source-specific examples into generic examples unless the named technology is itself the reusable subject
- update multiple existing skills if the source improves more than one domain
- keep new skills focused; create references only when the detailed material is large and selectively useful

For source types:

- imported skill or repo: preserve the useful workflow, strip local wrappers, then merge or create as needed
- docs set or standard: extract current, primary-source procedures and edge cases
- book or other high-authority source: synthesize durable concepts into new or existing skills instead of copying chapter structure or prose

If the source makes claims about unstable tools, APIs, or frameworks, verify those claims against current primary documentation before making them canonical.

### 5. Record provenance

For imported or adapted assets:

- keep attribution in-file when the file format supports it
- add or update the entry in `SOURCES.md`
- state whether the result is `copied`, `adapted`, or `inspired-by`
- record source name, URL, and license when known

### 6. Validate the result

Before finishing:

- read every edited file end-to-end
- verify the content stayed general and did not import project-local assumptions
- verify there is no redundant overlap with nearby skills or commands
- verify the trigger description still matches the actual scope
- run `quick_validate.py` or an equivalent structure check on any new skill directory

If a source spans several major concepts, do not stop after the first obvious update. Make sure coverage is complete enough to reflect the valuable parts of the source without importing irrelevant detail.

## Quality Bar

Only keep material that clears all of these checks:

- actionable: another agent could use it to do real work
- generalizable: useful outside the original project
- evidence-backed: supported by the source and, when needed, by current primary docs
- non-duplicative: materially improves the library instead of echoing it
- durable: likely to remain useful after the original project context is gone

If any check fails, rewrite, merge more narrowly, or skip the content.
