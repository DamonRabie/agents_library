---
name: commit
description: "Use when the user asks to commit changes to git, create one or more commits, choose privacy-safe commit messages, apply the repo's gitmoji commit convention, or cleanly finish the current reviewed worktree into one or more well-explained commits. Also use for git trouble: diverged branch, pull/rebase conflicts, merge conflict resolution, accidentally staged files, undoing a local merge, recovering overwritten changes, stacked branches for dependent MRs."
---

# Commit

Commit the reviewed worktree cleanly and leave no ambiguous leftovers.

## Workflow

1. Run `git status --short` and inspect the changed files.
2. Review the relevant diffs before staging so the commit plan matches the actual changes.
3. Locate and inspect the project's canonical root README before staging. Check whether the reviewed changes alter anything it describes or should describe, including setup, usage, commands, configuration, architecture, supported behavior, or project status.
4. When the README would otherwise become incomplete or inaccurate, update it in the same commit scope. Preserve its structure and unrelated user edits. README review is always required; a README edit is required only when the change affects reader-facing durable project knowledge.
5. Do not stall the commit workflow over the README check. If no root README exists, it is already accurate, or the change has no reader-facing documentation impact, continue without editing it. Decide from the diff and existing documentation instead of pausing to ask whether an update is needed.
6. Check whether the reviewed changes materially update durable project knowledge that future agents should know, such as architecture, workflows, routing, feature phases, operating constraints, or repo-specific conventions.
7. If the answer is yes, update the project's memory file before any commit. Prefer the canonical source file when `AGENTS.md` or `CLAUDE.md` is a symlink or generated mirror. Preserve the existing format, tone, and section structure; keep the edit concise; record only stable guidance or milestones rather than transient implementation chatter.
8. Partition the worktree into one or more coherent commits. Split by behavior or purpose, not by file count.
9. If the user asks to "clean the worktree", plan to finish all reviewed remaining changes in this run, usually as multiple commits when the leftovers are unrelated.
10. Decide the full commit plan up front. If the remaining files are unclear, mixed with unrelated user edits, or not safe to commit, stop before making any commit and ask.
11. Stage only the files for the current commit. Prefer narrow pathspecs over broad staging when unrelated leftovers exist.
12. If the wrong file is staged, unstage it and fix the boundary before committing.
13. Draft the complete subject and body, then apply the commit-message safety gate below. Rewrite unsafe or uncertain details before running `git commit`.
14. Commit with the repo convention:

```text
:git_moji: TYPE: Commit description
```

Examples of `TYPE`:

- `feat` for new capability
- `fix` for a bug fix
- `chore` for maintenance, wiring, dependencies, or cleanup
- `docs` for documentation-only changes
- `refactor` for behavior-preserving restructuring
- `test` for test-only changes

15. Continue committing the remaining reviewed file groups until `git status --short` is clean for the agreed scope.

## Memory Update Rules

- Treat a memory update as required when the diff adds or changes stable project knowledge:
  - new architectural patterns or service boundaries
  - new canonical routes, entry points, or workflow shapes
  - completed phases or major capability milestones
  - repo-specific constraints or conventions future agents should follow
- Skip memory edits for purely local fixes, refactors with no workflow impact, test-only changes, formatting churn, or temporary debugging work.
- Prefer editing the source file behind `AGENTS.md` or `CLAUDE.md`:
  - if `AGENTS.md` or `CLAUDE.md` is a symlink, edit the symlink target
  - if one file is documented as generated from another memory file, edit the source file instead of the generated mirror
  - do not break, replace, or remove the link while updating memory
- Keep memory concise. Extend existing sections when possible instead of creating sprawling new sections.
- Preserve the document's current structure and naming unless the repo already uses a different memory format.
- Avoid logging unstable details such as one-off bug fixes, temporary commands, or short-lived branch context.

## Message Rules

- Treat the full commit message as durable, broadly visible metadata, including subjects, bodies, trailers, merge messages, revert messages, and text generated from branch or issue titles.
- Describe the high-level intent and outcome, not the underlying sensitive evidence. Commit-message safety overrides the normal preference for specificity.
- Never include secrets or authentication material, even if already present in the diff, logs, a ticket, or a user-provided draft. This includes passwords, tokens, keys, certificates, cookies, authorization headers, connection strings, and secret locations or names.
- Never disclose security-related details. Do not name a vulnerability, weakness, exploit or attack path, affected endpoint, bypass, incident, scanner finding, protection gap, attack precondition, or exact security control/configuration. For security-sensitive work, use a neutral description of the general code behavior without identifying the security concern.
- Never include literal or identifying data. Exclude personal, customer, employee, vendor, business, warehouse, production, training, evaluation, or model-output values; row or payload samples; query literals; prompts; record counts; exact timestamps; account, tenant, order, ticket, issue, or trace identifiers; emails; phone numbers; addresses; internal hostnames, IPs, URLs, ports, database/schema/table/bucket/cluster names, and private project or service names.
- Do not paste source snippets, commands containing values, logs, stack traces, error messages, query results, scanner output, or ticket text into the message. Summarize the change at a non-sensitive level.
- Mention a file, path, component, or public issue reference only when its name is already non-sensitive and adds useful context. Otherwise use a generic area such as `request handling`, `configuration`, `validation`, or `processing`.
- If any detail might be sensitive or data-bearing, omit or generalize it. If a useful body cannot be written safely, use a minimal sanitized body or omit the body; never trade confidentiality for detail.
- Review user-supplied and Git-generated messages under the same rules. Do not blindly preserve an unsafe proposed subject, merge message, squash message, revert subject, issue title, or trailer.
- Pick the gitmoji and type that best fit the staged change.
- Use a clear, concise subject.
- Use imperative mood where practical.
- Do not end the subject with a period.
- Add a second `-m` body when the commit touches multiple files, non-trivial logic, migrations, config, or user-visible behavior, unless doing so would disclose or imply sensitive information.
- Make the second `-m` informative rather than generic. Explain what changed, why it changed, and which files or areas carry the important parts.
- Mention key files or areas in the body only after confirming that their names are safe, with one short line per file or group when that improves scanability.
- Keep the body specific to the staged diff. Do not repeat boilerplate.

Preferred body shape:

```text
Why:
- <non-sensitive reason for the change>

What:
- <safe file or generic area>: <non-sensitive change and impact>
- <safe file or generic area>: <non-sensitive change and impact>
```

Example:

```text
git commit -m ":bug: fix: correct request validation" -m "Why:
- align behavior with current requirements

What:
- request handling: update validation and related checks"
```

## Guardrails

- Always inspect the root README, but do not create or change it merely to prove that the check happened.
- Do not pause or leave an otherwise authorized commit unfinished solely because the README is missing, already current, or unaffected.
- Do not commit before handling any required memory update.
- Default to finishing the reviewed worktree in this run. Do not stop after the first commit if reviewed changes still remain.
- Do not stage unrelated user changes unless the user explicitly asked to commit everything.
- Do not rewrite, reset, or discard changes to make staging easier.
- If the user asked to clean the worktree, prefer separate commits over one mixed commit when that keeps unrelated changes understandable.
- If one leftover file or deletion is outside the main change set but is still clearly safe to commit, commit it separately rather than leaving the tree dirty.
- If the worktree contains pre-existing unrelated changes, do not start committing around them blindly. Either isolate a safe reviewed subset and explain what remains, or ask before proceeding.
- If the user asked to commit the current work and the remaining reviewed changes can be grouped safely, create as many commits as needed so the worktree is clean at the end.
- If no files are changed or staged, stop and report that there is nothing to commit.

## Git Rescue Recipes

Use these when the worktree or branch state is broken. Always run `git status`, `git log --oneline -5 --all --graph`, and (before anything destructive) note the current commit hash — `git reflog` can recover almost anything committed.

### Branch diverged from master (push rejected / "have diverged")

1. Commit or stash local work first — never resolve divergence with a dirty tree.
2. `git fetch origin` then `git rebase origin/master` (default for feature branches; keeps history linear and satisfies "rebase before merge" policies).
3. Resolve conflicts one commit at a time (see below), `git rebase --continue`.
4. Push with `git push --force-with-lease` (never bare `--force`) — only on your own feature branches, never a shared branch.

### Pull caused conflicts

1. Don't panic-abort blindly: check `git status` for `both modified` files.
2. For each conflicted file decide the side deliberately: `git checkout --ours <file>` / `--theirs <file>` when one side wholly wins, manual merge when both matter. On explicit user policy like "keep mine for X, accept theirs elsewhere", apply exactly that per-path and list the result.
3. `git add` resolved files, then `git rebase --continue` / `git commit` (merge case).
4. If the state becomes confusing, `git rebase --abort` / `git merge --abort` returns to the pre-pull state — say so before retrying with a plan.

### Wrong files staged / need to switch branches

- Unstage without losing edits: `git restore --staged <file>` (all: `git reset`).
- Carry uncommitted work across branches: `git stash push -m "wip"` → switch → `git stash pop`.

### Undo a local merge (not pushed)

- `git reset --merge ORIG_HEAD` right after the merge; or `git reset --hard <pre-merge-hash>` from reflog. If already pushed, use `git revert -m 1 <merge-commit>` instead — never rewrite pushed shared history.

### My changes were overwritten / lost

1. `git reflog` — find the commit where the work last existed.
2. Inspect with `git show <hash> -- <file>`; recover with `git checkout <hash> -- <file>` or `git cherry-pick <hash>`.
3. If the work was never committed, check `git stash list` and editor local history before declaring it lost.

### Stacked branches for dependent work

When issue B depends on issue A whose MR is still open: branch B **from A's branch**, not from master (`git checkout -b feat-b feat-a`). Open B's MR targeting A's branch (retarget to master after A merges). After A changes, rebase B onto the updated A: `git rebase feat-a`. Creating B from master while A is unmerged silently drops A's work from B's context.

### Protecting master hygiene

- Before opening an MR, rebase the branch on latest master so the MR is not "N commits behind".
- Commits on the default branch by accident: `git branch rescue && git reset --hard origin/master` — the work lives on `rescue`.

**Teaching mode:** when the user asks "teach me" or seems unsure, explain each command's effect in one line before running it, and show the before/after `git log --oneline` so the fix is understandable, not magic.

## Validation

- Confirm the root README was inspected and that any reader-facing facts changed by the commit remain accurate. If no README exists or no edit is needed, treat the check as complete and continue.
- If a memory update may be needed, inspect `AGENTS.md`, `CLAUDE.md`, and any linked source file before staging to determine the correct edit target.
- After a memory edit, review that diff as part of the commit plan and confirm the link or generated-file relationship still holds.
- After staging, run `git diff --cached --stat`.
- If the staged diff is ambiguous, inspect `git diff --cached`.
- If the staged diff includes files outside the intended commit boundary, unstage them before committing.
- Before `git commit`, reread the exact final subject and body as a standalone public artifact. Confirm that every literal, identifier, filename, path, URL, trailer, and technical detail passes the message-safety rules; generalize or remove anything uncertain.
- For merge, squash, cherry-pick, and revert workflows, inspect any generated message before accepting it because source subjects, branch names, issue titles, and trailers can reintroduce sensitive details.
- After each commit, run `git status --short` again to confirm what remains.
- Before finishing, verify whether the worktree is clean. If it is not clean, explain exactly which files remain and why they were not committed.
- After committing, report the short commit hash, subject, body summary, and files included.
