---
name: knowledge-ops
description: Knowledge base management, ingestion, sync, and retrieval across multiple storage layers (local files, MCP memory, vector stores, Git repos). Use when the user wants to save, organize, sync, deduplicate, or search across their knowledge systems.
origin: ECC
---

# Knowledge Operations

Manage knowledge across repo-local memory, tracker truth, durable notes, and optional semantic stores.

Default to model-neutral storage. This repo is used by multiple agentic tools, so shared facts should live in canonical repo surfaces unless the fact or config is genuinely tool-specific.

## When to Activate

- User wants to save information to their knowledge base
- Ingesting documents, conversations, or data into structured storage
- Syncing knowledge across systems (local files, MCP memory, Supabase, Git repos)
- Deduplicating or organizing existing knowledge
- User says "save this to KB", "sync knowledge", "what do I know about X", "ingest this", "update the knowledge base"
- Any knowledge management task beyond simple memory recall

## Repository Rules

- Treat symlinks as intentional wiring. Inspect with `ls -l` or `find . -type l -ls` when paths look surprising, but do not replace symlinks with regular files.
- Canonical shared memory is `.agent-library/AGENTS_MEMORY.md`; root `AGENTS.md` and `CLAUDE.md` are symlinks to it.
- Canonical shared agent assets live in `.agent-library/{agents,skills,commands,rules,config}`.
- Tool entrypoints may be symlinks into `.agent-library`, for example `.claude/agents`, `.claude/commands`, `.claude/skills`, `.codex/agents`, and `.agents/skills`.
- Edit the canonical `.agent-library` file first. Do not create divergent copies under `.claude`, `.codex`, `.agents`, or another model-specific directory.
- Store guidance in the most general form possible. Use model-specific names only for real tool contracts, such as Codex config, Claude command metadata, or OpenAI skill UI metadata.

## Knowledge Architecture

### Layer 1: Active Execution Truth
- **Sources:** GitHub issues, PRs, discussions, release notes, Linear issues/projects/docs
- **Use for:** the current operational state of the work
- **Rule:** if something affects an active engineering plan, roadmap, rollout, or release, prefer putting it here first

### Layer 2: Repo-Local Shared Memory
- **Path:** `.agent-library/AGENTS_MEMORY.md`, surfaced through root `AGENTS.md` and `CLAUDE.md` symlinks
- **Use for:** durable project facts, repo conventions, validation notes, routing guidance, and cross-agent operating rules
- **Rule:** keep it concise, durable, and model-neutral

### Layer 3: Tool-Specific Memory or Config
- **Sources:** `.codex/`, `.claude/`, `~/.claude/projects/*/memory/`, skill UI metadata, MCP server config
- **Use for:** behavior that only one model or harness can consume
- **Rule:** keep shared instructions out of tool-specific stores unless the tool requires that location

### Layer 4: MCP Memory Server or Semantic Store
- **Access:** MCP memory tools (create_entities, create_relations, add_observations, search_nodes)
- **Use for:** Semantic search across all stored memories, relationship mapping
- **Cross-session persistence with queryable graph structure**

### Layer 5: Knowledge Base Repo or Durable Document Store
- **Use for:** curated durable notes, session exports, synthesized research, operator memory, long-form docs
- **Rule:** this is the preferred durable store for cross-machine context when the content is not repo-owned code

### Layer 6: External Data Store
- **Use for:** Structured data, large document storage, full-text search
- **Good for:** Documents too large for memory files, data needing SQL queries

### Layer 7: Local Context or Archive Folder
- **Use for:** human-facing notes, archived gameplans, local media organization, temporary non-code docs
- **Rule:** writable for information storage, but not a shadow code workspace
- **Do not use for:** active code changes or repo truth that should live upstream

## Ingestion Workflow

When new knowledge needs to be captured:

### 1. Classify
What type of knowledge is it?
- Repo convention or project fact -> `.agent-library/AGENTS_MEMORY.md`
- Agent asset behavior -> canonical `.agent-library/{agents,skills,commands,rules,config}` file
- Model-specific behavior -> the smallest relevant `.claude`, `.codex`, or model metadata surface
- Business decision -> active tracker first, then shared memory or durable docs if still useful
- Active roadmap / release / implementation state -> GitHub + Linear first
- Personal preference -> user-scoped memory when available, not repo memory unless it affects the repo
- Reference info -> durable docs or semantic memory, with a short repo-memory pointer only if frequently needed
- Large document -> external data store + summary in memory
- Conversation/session -> knowledge base repo + short shared-memory summary only when it changes durable project behavior

### 2. Deduplicate
Check if this knowledge already exists:
- Resolve symlinks and search canonical targets, not every linked path as a separate document
- Search repo memory, agent-library docs, and relevant skill/rule files for existing entries
- Query MCP memory with relevant terms
- Check whether the information already exists in GitHub or Linear before creating another local note
- Do not create duplicates. Update existing entries instead.

### 3. Store
Write to appropriate layer(s):
- Update `.agent-library/AGENTS_MEMORY.md` for repo-wide facts that every agent should see
- Update the relevant skill, rule, command, agent, or config file when the information belongs to that asset
- Use model-specific memory/config only when a model or harness needs a distinct contract
- Use MCP memory for semantic searchability and relationship mapping when available and useful
- Update GitHub / Linear first when the information changes live project truth
- Use a knowledge base repo or durable document store for long-form additions

### 4. Index
Update relevant indexes or summary files. If files are symlinked, update the canonical target and verify linked entrypoints see the same content.

## Sync Operations

### Conversation Sync
Periodically sync conversation history into the knowledge base:
- Sources: Claude session files, Codex sessions, other agent sessions
- Destination: knowledge base repo
- Generate a session index for quick browsing
- Commit and push

### Workspace State Sync
Mirror important workspace configuration and scripts to the knowledge base:
- Generate directory maps with symlink targets included
- Redact sensitive config before committing
- Track changes over time
- Do not treat the knowledge base or archive folder as the live code workspace

### GitHub / Linear Sync
When the information affects active execution:
- update the relevant GitHub issue, PR, discussion, release notes, or roadmap thread
- attach supporting docs to Linear when the work needs durable planning context
- only mirror a local note afterwards if it still adds value

### Cross-Source Knowledge Sync
Pull knowledge from multiple sources into one place:
- Claude/ChatGPT/Grok conversation exports
- Browser bookmarks
- GitHub activity events
- Write status summary, commit and push

## Memory Patterns

```
# Short-term: current session context
Use TodoWrite for in-session task tracking

# Repo-local shared memory
Write durable cross-agent repo facts to .agent-library/AGENTS_MEMORY.md

# Tool-specific memory/config
Use .claude, .codex, ~/.claude, or skill metadata only for tool-specific behavior

# Long-term: GitHub / Linear / KB
Put active execution truth in GitHub + Linear
Put durable synthesized context in the knowledge base repo

# Semantic layer: MCP knowledge graph
Use mcp__memory__create_entities for permanent structured data
Use mcp__memory__create_relations for relationship mapping
Use mcp__memory__add_observations for new facts about known entities
Use mcp__memory__search_nodes to find existing knowledge
```

## Best Practices

- Keep memory files concise. Archive old data rather than letting files grow unbounded.
- Use frontmatter (YAML) for metadata on all knowledge files.
- Deduplicate before storing. Search first, then create or update.
- Prefer one canonical home per fact set. Avoid parallel copies of the same plan across local notes, repo files, and tracker docs.
- Prefer model-neutral wording for shared repo instructions. Name a model or harness only when the instruction cannot be expressed generically.
- Preserve symlink wiring. A symlinked path is an entrypoint to the canonical file, not a duplicate to "fix".
- Redact sensitive information (API keys, passwords) before committing to Git.
- Use consistent naming conventions for knowledge files (lowercase-kebab-case).
- Tag entries with topics/categories for easier retrieval.

## Quality Gate

Before completing any knowledge operation:
- no duplicate entries created
- symlinks were preserved and canonical targets were edited
- shared guidance is model-neutral unless explicitly tool-specific
- sensitive data redacted from any Git-tracked files
- indexes and summaries updated
- appropriate storage layer chosen for the data type
- cross-references added where relevant
