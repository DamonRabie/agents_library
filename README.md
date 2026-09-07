# Agents Library

Central library of reusable skills, agents, and commands for AI-assisted development workflows — shared by both **Claude Code** and **Codex**.

This repository is intended to be a working collection rather than a pristine upstream mirror. Some entries are authored locally, some are imported from other sources, and some are adapted over time to fit project-specific workflows. Source attribution is tracked so imported material stays traceable after local edits.

The operating model is a single canonical library consumed through symlinks — never copies. Claude Code and Codex point at the same underlying files so content stays synchronized and never drifts between tool-specific directories.

This README covers two jobs:

1. **[Install the skills globally](#1-install-skills-globally)** so every repo you open in Claude Code or Codex has the full portfolio available immediately.
2. **[Make any repo compatible with both tools](#2-make-a-repo-compatible-with-both-claude-code-and-codex)** — the CLAUDE.md/AGENTS.md pair, the dot-directory adapters, and the audit skill that checks and fixes both.

---

## 1. Install Skills Globally

Claude Code reads skills from `~/.claude/skills/`; Codex reads from `~/.codex/skills/`. Symlinking the whole `skills/` folder of this repo into both locations makes every super skill available in every project, in both tools, with zero per-project setup.

Run this once per machine (idempotent — safe to re-run any time a skill is added or renamed):

```bash
# From the root of this repo:
CANONICAL="$(pwd)/skills"

for dest in ~/.claude/skills ~/.codex/skills; do
  mkdir -p "$dest"
  for skill in "$CANONICAL"/*/; do
    name="$(basename "$skill")"
    ln -sfn "$CANONICAL/$name" "$dest/$name"
  done
done
```

Verify:

```bash
ls -la ~/.claude/skills   # every skills/<name> should appear as a symlink
ls -la ~/.codex/skills    # same set, same targets
```

**Why loop over the directory instead of a hardcoded list:** new skills added to `skills/` are picked up automatically on the next run — nothing to remember to update here.

**Uninstalling / removing a retired skill:** delete the symlink from both `~/.claude/skills/<name>` and `~/.codex/skills/<name>`; the canonical copy lives only in this repo (or `archive/` if retired, see below).

---

## 2. Make a Repo Compatible with Both Claude Code and Codex

Two cases: making **this library repo itself** self-consistent (already done, see below), and making **any other repo** ready to be worked on by both tools.

### For any other repo — use the `agent-ready` skill

Once skills are installed globally (step 1), the `agent-ready` skill is available in every repo. It is the audit-and-repair tool for exactly this job:

```
"make this repo agent-ready"
"audit this codebase for agent compatibility"
```

It checks and fixes: git initialized, `CLAUDE.md`/`AGENTS.md` present and adequate, `make verify`/`test`/`run`/`deploy` targets, no secrets in the tree, `artifacts/` gitignored, and — the part relevant here — that skills are wired as **symlinks, never copies**, and that both tools' entrypoints resolve to the same files.

### Manual setup (what `agent-ready` automates)

From the target repo's root:

```sh
mkdir -p .agent_library .claude .agents .codex
cp -R /path/to/agents_library/skills .agent_library/
cp -R /path/to/agents_library/commands .agent_library/
cp -R /path/to/agents_library/agents .agent_library/
touch .agent_library/AGENT_MEMORY.md

ln -s .agent_library/AGENT_MEMORY.md AGENTS.md
ln -s .agent_library/AGENT_MEMORY.md CLAUDE.md

ln -s ../.agent_library/skills .claude/skills
ln -s ../.agent_library/commands .claude/commands
ln -s ../.agent_library/skills .agents/skills
ln -s ../.agent_library/commands .agents/commands
ln -s ../.agent_library/skills .codex/skills
ln -s ../.agent_library/commands .codex/commands
```

Replace `/path/to/agents_library` with the absolute path to this repository. Keep project-specific working memory in `.agent_library/AGENT_MEMORY.md`; `AGENTS.md` and `CLAUDE.md` stay symlinks to that one file so both tool entrypoints read identical instructions — never let them diverge into two separate docs.

**If skills are already installed globally (step 1), this local copy step is optional** — Claude Code and Codex both already see the full skill portfolio without it. Do it anyway when: the repo needs to work on a machine without the global install (a teammate's laptop, CI), or the repo wants a deliberately scoped/pinned subset of skills rather than the whole portfolio.

After the files and symlinks are in place, call `$curate-from-source` for the new project to inspect context and trim to the best-fitting skills, commands, and agents, keeping only durable, general-purpose assets in `.agent_library`.

### How this repo satisfies its own contract

This library is also a valid Claude Code / Codex repo in its own right. Its dot-directories already point at the canonical folders:

```
.agents/skills   -> ../skills       .codex/skills   -> ../skills
.agents/commands -> ../commands     .codex/commands -> ../commands
.agents/agents   -> ../agents       .codex/agents   -> ../agents
```

`AGENTS.md` at the repo root is the single memory file both tools read (no separate `CLAUDE.md` needed here — `AGENTS.md` is the canonical name and Claude Code reads it directly).

---

## Structure

```text
skills/     Active super skills — symlinked into ~/.claude/skills and ~/.codex/skills, and into consumer repos
archive/    Retired/downloaded micro-skills — searchable source material, never symlinked
commands/   Slash-command style prompts and workflows
agents/     Standalone agent definitions and notes
SOURCES.md  Registry of imported or adapted material
```

Some skills also bundle agent definitions under `skills/<name>/agents/`.

## Super Skills Portfolio (current canonical set)

13 super skills replace the previous pile of ~215 downloaded micro-skills. All 13 are installed globally via [step 1](#1-install-skills-globally); the "typical use" column is a guide to which ones matter most for a given repo, not a restriction.

| Skill | Domain | Typical use |
|---|---|---|
| `prove-it` | Verification / acceptance criteria | Every repo |
| `ci-deploy` | Docker, CI/CD, VPS deploy | Every repo |
| `mr-review` | Code review (all languages) | Every repo |
| `idea-to-issues` | Interrogate → design → issues | Every repo |
| `agent-ready` | Repo auditing and repair | Every repo (run first on a new repo) |
| `commit` | Git commit discipline, README synchronization, and rescue recipes | Every repo |
| `data-warehouse` | ClickHouse OLAP, SQL quality | Data warehouse repos |
| `data-pipelines` | Airflow, PySpark | Pipeline/orchestration repos |
| `llm-pipelines` | Batch LLM/DSPy pipeline engineering | Repos with an LLM processing step |
| `ml-experiments` | ML lifecycle, HPO, debugging, MLflow hygiene | ML training repos |
| `model-serving` | ONNX, MLflow registry, Triton | Model-serving repos |
| `remote-ops` | Remote VM/SSH/GPU/offline-environment ops | Any repo trained or run on a remote machine |
| `python-backend` | FastAPI, SQLAlchemy, Alembic | Python backend services |

**Archive:** all other downloaded skills are in `archive/`. Source reference material, never symlinked.

## Usage Model

- This repository is the source of truth.
- Claude Code and Codex consume these assets through symlinks — globally (step 1) and/or per-repo (step 2).
- Do not maintain duplicate copies of the same skill or command for each tool unless the formats genuinely diverge.
- If a tool needs a wrapper or adapter, keep the shared logic here and make the adapter thin.

```text
tool config path -> symlink -> this repository
```

That keeps edits centralized and avoids drift between agent environments — editing a skill here updates it everywhere it's linked, instantly.

## Compatibility

### Claude Code

- Primary format: `SKILL.md`
- Optional skill-local agent definitions: `agents/openai.yaml`
- Commands are stored as Markdown prompt files in `commands/`

### Codex

- Markdown-based skills and command references can be reused directly
- Any tool-specific wrappers or metadata should be kept additive, not required
- Prefer portable plain-text instructions over platform-specific assumptions

When adding new content, keep the core logic in Markdown first and treat platform-specific files as thin adapters around the shared source files.

## Source Attribution

If a skill, command, or agent is imported or adapted from another source:

1. Preserve attribution in the file itself when possible.
2. Add or keep source metadata in frontmatter when the format supports it.
3. Register the item in [SOURCES.md](SOURCES.md).
4. Note whether the local version is copied, adapted, or only inspired by the source.
5. Record license information when known.

Recommended frontmatter fields for imported Markdown assets:

```yaml
origin: community
source_name: Example Project
source_url: https://github.com/example/project
license: MIT
adaptation: adapted for local workflows
```

Not every file needs every field, but imported material should be traceable without guessing.

## Import Workflow

1. Copy or add the external skill, agent, or command into the appropriate folder.
2. Normalize naming and layout to fit this repository.
3. Edit the content for local project needs.
4. Add attribution metadata to the file if supported.
5. Add an entry to `SOURCES.md`.

## Conventions

- Prefer ASCII unless a file already requires Unicode.
- Keep reusable instructions generic; move project-specific details into local adaptations (a repo's own `CLAUDE.md`/`AGENTS.md`), never into the shared skill.
- No project codenames, hostnames, IPs, usernames, or other confidential detail belongs in a skill — genericize the example instead.
- Avoid deleting upstream attribution unless the content has been fully rewritten and no longer derives from the source.
- If an item has been heavily modified, describe it as `adapted` rather than `copied`.
- Prefer symlinking shared assets into tool-specific locations instead of copying them.

## Maintenance Rule

A lesson learned in any repo gets **one line** in the relevant super skill's `data/*.csv` (if general) or the repo's own `CLAUDE.md`/`AGENTS.md` (if project-specific). Never create a new micro-skill for a lesson that fits in an existing super skill's data file.

New skill creation requires a domain that none of the current 13 cover. The bar is high.
