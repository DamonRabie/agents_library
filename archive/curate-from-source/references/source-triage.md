# Source Triage Rubric

Use this rubric when the source is long, mixed, high-authority, or likely to contain both reusable and project-specific material.

## 1. Transferability Test

Keep material only if the answer is "yes" to most of these:

- Would this still be useful in a different project?
- Is the guidance procedural, structural, or conceptual rather than tied to one codebase?
- Can the instruction survive after removing local names and paths?
- Is the claim supported by the source rather than implied by style or marketing?

Usually reject material like:

- internal repo paths and folder maps
- team names, role assignments, ticket rituals
- one-off migrations, rollout dates, incident details
- company-specific business rules presented without a broader pattern
- environment variables, credentials, or infrastructure assumptions unique to one system

## 2. Rewrite vs Reject

Rewrite when the underlying pattern is reusable:

- "Run `deploy/foo.sh` before every schema change"
  becomes
  "Add an explicit pre-deploy safety check before schema-changing operations."

- "Use Service X to notify Ops Team Y"
  becomes
  "Define an escalation and notification path for operational failures."

Reject when the content only makes sense inside the original project:

- "Store partner overrides in `billing_v2.partner_edges`"
- "Reviewer must ping the Cairo marketplace squad lead"

## 3. Source-Type Handling

### Imported skills, agents, or command packs

- Preserve useful workflow structure.
- Remove branding, local memory references, and harness-specific assumptions unless they are the reusable subject.
- Merge into an existing local asset when the overlap is strong.

### Documentation sets, manuals, and standards

- Prefer primary documentation over summaries.
- Extract operational rules, edge cases, and validation steps.
- Verify unstable technical details if the docs may be outdated.

### Books, papers, and other high-authority sources

- Treat them as concept and method sources, not as templates to copy verbatim.
- Distill durable frameworks, heuristics, and evaluation methods.
- Update multiple skills when the material spans several domains.

### Project docs and runbooks

- Mine them for general patterns only.
- Strip local architecture, names, environments, and current-state details.
- Skip them entirely if the reusable content is too thin after generalization.

## 4. Merge Matrix

- Improve existing skill: when scope already exists and the source adds better workflow, coverage, or validation
- Create new skill: when the workflow is durable, distinct, and missing
- Enrich references: when the core skill exists but needs deeper reference material
- Skip: when the source adds only style, duplication, or project-local facts

## 5. Canonical Quality Checks

Before finalizing, confirm:

- the updated asset is stronger than the previous version
- the guidance is complete enough to matter, not a shallow summary
- examples are neutral or intentionally technology-specific
- provenance is recorded in-file when possible and in `SOURCES.md`
- the result reads like a source of truth, not rough notes from an import session
