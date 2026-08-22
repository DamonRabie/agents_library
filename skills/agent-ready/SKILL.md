---
name: agent-ready
description: "Agent-readiness auditing and repair for any repo. Actions: audit repo, check repo, make repo agent-ready, scan codebase, add CLAUDE.md, add Makefile, fix skills, check git, add verify target, check secrets, standardize repo, onboard repo for agents. Topics: git init, CLAUDE.md quality, AGENTS.md, make verify, make test, make run, make deploy, skills manifest, symlinks not copies, artifacts convention, secrets out of tree, agent compatibility, repo compatibility, gap report, agent contract. Triggers: 'is this repo ready for agents', 'set up this repo', 'onboard this repo', 'audit this codebase', 'make this agent-friendly'."
---
# Agent-Ready — Repo Auditing & Repair

The meta-skill. Run it on any repo to produce a gap report and fixes. Every super skill pays dividends only when the repo satisfies the agent contract defined here. This skill defines that contract and fixes deviations.

## When to Apply

### Must Use

- Before dispatching the first agent worker to a new repo
- When an agent is producing unexpected results due to repo confusion
- When starting work on a repo that hasn't been used with agents yet
- Explicit request: "make this repo agent-ready" or "audit this codebase"

### Recommended

- Quarterly repo health check on all active repos
- When merging a fork or cloning a new project to work in
- When a new team member sets up their environment

### Skip

- Repos already passing all checks below
- Read-only / archived repos

## The Agent Contract (every active repo must satisfy)

| Check | Required | Why |
|---|---|---|
| git initialized | CRITICAL | Every agent mistake is unrecoverable without git |
| CLAUDE.md or AGENTS.md present | CRITICAL | Agent has no project context without it |
| `make verify` works | CRITICAL | Agent can't validate its own changes |
| `make test` works | HIGH | Full test suite for regression detection |
| `make run` works (if applicable) | HIGH | Agent can't test user-visible behavior |
| `make deploy` works (if applicable) | HIGH | Same script as CI kills debug-by-pushing |
| No secrets in tree | CRITICAL | Accidental commit leaks credentials |
| Skills: symlinks not copies | HIGH | Copies drift; symlinks stay canonical |
| artifacts/ directory exists + gitignored | MEDIUM | Agent outputs land in known location |
| .gitignore present | HIGH | Prevents .env, caches, secrets from being committed |

## Audit Procedure

Run this for any repo:

```bash
# 1. Git
[ -d .git ] && echo "GIT: OK" || echo "GIT: MISSING — run: git init"

# 2. CLAUDE.md / AGENTS.md
[ -f CLAUDE.md ] || [ -f AGENTS.md ] && echo "CLAUDE.md: OK" || echo "CLAUDE.md: MISSING"

# 3. Makefile with required targets
for target in verify test run deploy; do
    grep -q "^$target:" Makefile 2>/dev/null && echo "make $target: OK" || echo "make $target: MISSING"
done

# 4. Secrets scan
grep -rI "password\|secret\|token\|api_key\|private_key" --include="*.py" --include="*.ts" \
     --include="*.yaml" --include="*.yml" --include="*.json" \
     --exclude-dir=".git" --exclude-dir="node_modules" . | \
     grep -v "os.environ\|getenv\|Settings\|BaseSettings\|process.env\|# noqa" | head -20

# 5. Skill installation (symlinks vs copies)
[ -d .claude/skills ] && \
    (find .claude/skills -type l | wc -l | xargs echo "symlinks:") && \
    (find .claude/skills -type d -mindepth 1 | wc -l | xargs echo "directories (should be 0 if all symlinked):")

# 6. artifacts/ gitignored
[ -f .gitignore ] && grep -q "artifacts" .gitignore && echo "artifacts/: gitignored" || echo "artifacts/: NOT gitignored"
```

## CLAUDE.md Quality Rubric

A good CLAUDE.md answers these questions for an agent starting cold:

- [ ] **What is this repo?** (1-sentence purpose)
- [ ] **Tech stack** (language, framework, DB, key tools)
- [ ] **How do I run it locally?** (`make run` or explicit commands)
- [ ] **How do I verify my changes?** (`make verify` or explicit commands)
- [ ] **Repo-specific conventions** (naming, layering, forbidden patterns)
- [ ] **Where do outputs/artifacts go?** (usually `artifacts/`)
- [ ] **What must NOT be committed?** (secrets, caches, generated files)
- [ ] **Any cross-repo dependencies?** (e.g., a review repo whose CI syncs files into a production repo)

CLAUDE.md must NOT contain:
- Generic programming advice (belongs in super skills)
- Full copies of skill content (link to the skill instead)
- Project-specific secrets or URLs that change per environment

## Fix Recipes

### git not initialized
```bash
git init
echo ".env\n.env.*\n__pycache__\n*.pyc\nnode_modules\n.venv\nartifacts/" > .gitignore
mkdir -p artifacts
echo "artifacts/" >> .gitignore
```

### CLAUDE.md missing
```bash
cat > CLAUDE.md << 'EOF'
# CLAUDE.md — <repo-name>

## Purpose
<1-sentence description>

## Stack
<language, framework, DB>

## Commands
```bash
make verify   # lint + typecheck + unit tests
make test     # full test suite
make run      # start locally
make deploy   # production deploy (same as CI)
```

## Conventions
<project-specific rules>

## Artifacts
All outputs, screenshots, and working files go in `artifacts/` (gitignored).
EOF
```

### Skills: replace copies with symlinks
```bash
# From within the repo root:
CANONICAL="<path-to-canonical-agents-library>/skills"   # the single source-of-truth library repo
mkdir -p .claude/skills

for skill in prove-it ci-deploy data-warehouse python-backend mr-review; do
    [ -d "$CANONICAL/$skill" ] || continue
    [ -e ".claude/skills/$skill" ] && rm -rf ".claude/skills/$skill"
    ln -sf "$CANONICAL/$skill" ".claude/skills/$skill"
    echo "Symlinked: $skill"
done
```

### Make verify missing
Add to Makefile (adapt to actual stack):
```makefile
verify:  ## Cheapest full check: lint + typecheck + dry-parse + unit tests
	<lint command>
	<typecheck command>
	<unit test command>
```

### secrets in tree
```bash
# Move to safe location
mv sensitive-file.txt ~/sensitive-file.txt.SAFE
echo "sensitive-file.txt" >> .gitignore

# If already committed — requires history rewrite (warn user)
git filter-branch --force --index-filter \
    'git rm --cached --ignore-unmatch sensitive-file.txt' HEAD
```

## Skill Installation Guide (canonical library + symlinks)

**Rule:** Every repo's `.claude/skills/` (and `.codex/skills/`) contains ONLY symlinks to the canonical `agents_library/skills/`. Never copies.

**All 13 super skills are installed globally** (`~/.claude/skills/`, `~/.codex/skills/`) — see the library's README, "Install Skills Globally". The table below is a guide to which ones matter most per repo type, not a restriction; per-repo symlinking (this skill's "Skills: replace copies with symlinks" recipe) is only needed for a repo that must work without the global install (a teammate's machine, CI) or wants a deliberately scoped subset.

**Typical skill set per repo type:**

| Repo type | Recommended skills |
|---|---|
| Python API service | python-backend, prove-it, ci-deploy, mr-review |
| Airflow/Spark pipeline | data-pipelines, data-warehouse, prove-it, mr-review |
| ML training | ml-experiments, model-serving, remote-ops, prove-it, mr-review |
| Model serving | model-serving, ci-deploy, prove-it, mr-review |
| Batch LLM/DSPy pipeline | llm-pipelines, data-warehouse, prove-it, mr-review |
| Remote/GPU-VM heavy work | remote-ops, ml-experiments, prove-it |
| Frontend | ui-ux-pro-max, prove-it, ci-deploy, mr-review |
| Full-stack app | python-backend, ui-ux-pro-max, prove-it, ci-deploy, mr-review |
| Job search / personal | idea-to-issues, mr-review |

Universal (broadly useful regardless of repo type): prove-it, ci-deploy, mr-review, idea-to-issues, agent-ready, commit

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "skills symlinks"
#       python scripts/search.py "CLAUDE.md missing"
#       python scripts/search.py "secrets in tree"
```
