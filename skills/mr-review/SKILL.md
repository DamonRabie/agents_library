---
name: mr-review
description: "Code review intelligence for MRs and PRs. Actions: review, review MR, review PR, check code, audit diff, security review, approve, request changes, comment, evaluate agent MR. Topics: correctness, security, data loss, performance, style, code smell, SQL injection, auth bypass, hardcoded secret, PEM key, token in code, N+1, race condition, missing migration, missing test, agent-authored MR, diff review, Python review, TypeScript review, SQL review, YAML review. Files: *.py, *.ts, *.tsx, *.sql, *.yaml, *.yml, Dockerfile, *.md. Severity: BLOCKER, HIGH, MEDIUM, LOW, NIT."
---
# MR-Review — Code Review Intelligence

A single severity-ordered rubric for reviewing any MR/PR — whether human-authored or agent-authored. Covers correctness, security, performance, and style in one pass. Particularly tuned for agent-authored MRs, which are the primary review workload now.

## When to Apply

### Must Use

- Reviewing any MR or PR before merge
- Security audit of any diff
- Reviewing an agent-authored MR (your primary use case)
- When asked to "review this code" or "check this diff"

### Recommended

- Before creating a PR (self-review)
- After a refactor "that shouldn't change behavior"
- Reviewing config changes (Dockerfile, CI YAML, compose)

### Skip

- Reading code for understanding (use codebase exploration)
- Writing new code (review is for already-written code)

## Severity Levels

| Level | Definition | Action |
|---|---|---|
| **BLOCKER** | Data loss, security vulnerability, correctness bug, broken deploy | Must fix before merge |
| **HIGH** | Performance regression, missing migration, missing test for critical path | Should fix before merge |
| **MEDIUM** | Anti-pattern, missing error handling, unclear naming, tech debt | Address in follow-up or in this MR |
| **LOW** | Minor style, cosmetic, nitpick | Optional |
| **NIT** | Typo, formatting | Author's choice |

## Review Order (always this priority sequence)

1. **Data loss / irreversibility** — Can this change destroy data? Is there a migration rollback? Is there a DROP TABLE?
2. **Security** — Auth bypass, injection, hardcoded secrets, token in code, over-permissioned endpoint.
3. **Correctness** — Logic bugs, off-by-one, null handling, race conditions, missing edge cases.
4. **Performance** — N+1 queries, unbounded list, missing index, O(n²) in hot path.
5. **Test coverage** — Is there a test for the new behavior? For the bug fix?
6. **Style / readability** — After all blockers resolved.

## Python-Specific Checklist

```
Security:
  [ ] No hardcoded secrets (API keys, passwords, tokens) in code or comments
  [ ] No PEM keys or recovery codes in committed files
  [ ] Auth is required on all non-public endpoints
  [ ] No eval() or exec() on user input
  [ ] No sql = f"SELECT ... {user_input}" (SQL injection)

Correctness:
  [ ] No bare except: that swallows all exceptions silently
  [ ] Async functions don't call blocking I/O (time.sleep, requests.get)
  [ ] No mutable default arguments (def f(x=[]):)
  [ ] Float used for money (use Decimal)
  [ ] datetime.now() in default argument (evaluated once at import)

Performance:
  [ ] No lazy load in loop (N+1)
  [ ] List endpoints have pagination
  [ ] No unbounded query (SELECT * without LIMIT)

Database:
  [ ] Alembic migration reviewed (no unintended drops, NOT NULL without default)
  [ ] downgrade() implemented
  [ ] Indexes on foreign key columns

Testing:
  [ ] New feature has integration test
  [ ] Bug fix has regression test that would have caught it
  [ ] Real DB used in integration tests (no SQLAlchemy mocks)
```

## TypeScript/React-Specific Checklist

```
Security:
  [ ] No dangerouslySetInnerHTML with user content
  [ ] API keys not in frontend code or env vars visible to browser
  [ ] Auth token stored in httpOnly cookie, not localStorage

Correctness:
  [ ] useEffect dependencies array complete (no stale closures)
  [ ] Async operations have loading/error states
  [ ] No direct DOM manipulation bypassing React

Performance:
  [ ] No expensive computation in render without useMemo
  [ ] Lists have stable key prop (not array index)
  [ ] Images have explicit width/height (no layout shift)
```

## SQL-Specific Checklist

```
  [ ] Dry-parse passed (no syntax error)
  [ ] No user input directly in query (use parameterized queries)
  [ ] NULL date boundaries handled (COALESCE or IS NOT NULL)
  [ ] JOIN fan-out checked (count(*) vs count(distinct id))
  [ ] FINAL clause on ReplacingMergeTree queries
  [ ] Synced files (production repo's job YAMLs) not edited directly
```

## YAML/Dockerfile Checklist

```
  [ ] Shell variables quoted in YAML scripts
  [ ] set -euo pipefail in all shell scripts
  [ ] docker compose run uses -T flag (no TTY assumption)
  [ ] Non-root USER in Dockerfile
  [ ] HEALTHCHECK defined
  [ ] Secrets not in ARG or ENV in Dockerfile
```

## Agent-Authored MR Review Protocol

Agent MRs require extra scrutiny because agents:
- Hallucinate method signatures (verify call sites)
- Miss multi-file consistency (check all affected files)
- Add unnecessary complexity ("future-proofing")
- May skip error handling
- Often don't add tests

**Extra checks for agent MRs:**
1. **Verify every external call signature** against the actual import/definition.
2. **Check all files changed are consistent** — especially schema ↔ migration ↔ test.
3. **Look for added complexity** — is there a simpler way to do this?
4. **Check test coverage explicitly** — agents often claim tests pass but skip adding them.
5. **Verify the acceptance criteria** are actually met by the code, not just by the commit message.

## Review Comment Format

```
[BLOCKER] app/api/v1/users.py:45 — auth is optional here; any unauthenticated request gets user data.
Fix: make token dependency non-optional.

[HIGH] alembic/versions/abc123.py — downgrade() is not implemented.
Fix: implement the reverse operation.

[MEDIUM] app/services/item.py:88 — potential N+1: user loaded inside loop.
Fix: use selectinload on the query above.

[NIT] app/schemas/item.py:12 — `item_id` could be `id` for consistency.
```

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "SQL injection"
#       python scripts/search.py "N+1 query"
#       python scripts/search.py "agent MR review"
```
