---
name: python-backend
description: "Python service engineering intelligence. Actions: design, build, fix, review, migrate, test, refactor, add endpoint, add model, debug, optimize. Stack: FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, MySQL, pytest, asyncio, uvicorn, celery, redis, docker. Topics: API design, pagination, error handling, versioning, auth patterns, JWT, single-owner auth, OAuth2, Postgres schema, MySQL schema, alembic migration, autogenerate review, data migration, rollback, pytest fixtures, factories, async tests, config management, secrets handling, background jobs, CORS, rate limiting. Files: app/, schemas/, models/, migrations/, tests/, pyproject.toml, alembic.ini. Symptoms: migration fails, test fails, N+1 query, slow endpoint, auth bypass, import error, alembic head mismatch, foreign key error, async issue, celery task not running."
---
# Python-Backend — Python Service Engineering

Complete guide for FastAPI + SQLAlchemy + Alembic backends. Covers API design, database patterns, migration discipline, testing strategy, and secrets management.

## When to Apply

### Must Use

- Writing or reviewing FastAPI routers, Pydantic schemas, SQLAlchemy models
- Writing or reviewing Alembic migrations
- Writing or reviewing pytest test suites
- Designing API contracts (pagination, error handling, auth)
- Debugging: N+1, slow queries, migration failures, auth issues, async errors

### Recommended

- Reviewing any Python service before merging
- Setting up a new service or adding a new resource
- Adding background tasks (Celery, FastAPI background tasks)

### Skip

- ML training logic (use ml-experiments)
- ClickHouse analytics queries (use data-warehouse)
- Frontend/React code (use ui-ux-pro-max)
- CI/CD pipeline setup (use ci-deploy)

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Migration safety | CRITICAL | Review autogenerate; test rollback; no data loss | Blind autogenerate commit |
| 2 | Auth correctness | CRITICAL | Auth required on all non-public endpoints; no bypass | Optional auth on sensitive routes |
| 3 | API contract | HIGH | Pagination on all list endpoints; consistent error schema | Unbounded list return |
| 4 | N+1 prevention | HIGH | Explicit relationship loading; no lazy load in loops | Lazy load in response serializer |
| 5 | Async discipline | HIGH | No blocking I/O in async path; use run_in_executor | time.sleep() in async function |
| 6 | Testing pyramid | HIGH | Domain services: unit; DB/API: real database | Mock SQLAlchemy in integration tests |
| 7 | Secrets management | HIGH | Env vars via pydantic Settings; never hardcoded | Hardcoded secrets in code or YAML |
| 8 | Error handling | MEDIUM | HTTPException with proper status codes; structured errors | Bare 500 for all errors |

## FastAPI Service Layout

```
app/
  api/           # FastAPI routers, one module per resource
    v1/
      users.py
      items.py
      router.py  # register all routers here
  core/          # config, settings, db session, security
    config.py    # pydantic Settings
    db.py        # async engine + session factory
    security.py  # JWT helpers
  domain/        # pure domain logic (no FastAPI/SQLAlchemy imports)
    services/
    exceptions.py
  models/        # SQLAlchemy ORM models
  schemas/       # Pydantic request/response schemas
tests/
  conftest.py    # shared fixtures (test DB, client)
  test_*.py
alembic/
pyproject.toml
```

## API Design Rules

```python
# 1. Pagination — ALL list endpoints
@router.get("/items", response_model=Page[ItemOut])
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    ...

# 2. Consistent error schema
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None  # machine-readable code

# 3. Versioning — prefix all routes with /api/v1/
app.include_router(router, prefix="/api/v1")

# 4. Auth — never optional on sensitive endpoints
async def require_user(token: str = Depends(oauth2_scheme)) -> User:
    # raises 401 if invalid — never returns None
    ...

# 5. HTTP status codes
# 200 = success; 201 = created; 204 = no content
# 400 = bad request (validation); 401 = unauthenticated; 403 = unauthorized
# 404 = not found; 409 = conflict; 422 = unprocessable; 500 = server error
```

## Alembic Migration Discipline

```bash
# Generate migration
alembic revision --autogenerate -m "add_users_table"

# ALWAYS review the generated migration before committing:
# 1. Check for unintended table drops
# 2. Check for column type changes that lose data
# 3. Check that data migrations are in a separate migration
# 4. Check upgrade() AND downgrade() are both valid

# Test the migration (forward + backward)
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# Check for drift (no uncommitted changes)
alembic check
```

**Migration anti-patterns:**
- `op.drop_table()` without confirming no data needed
- Column type narrowing (`VARCHAR(256)` → `VARCHAR(64)`) without data check
- `NOT NULL` column added without server_default or explicit backfill
- Data migration logic inside schema migration (split them)

## SQLAlchemy — N+1 Prevention

```python
# BAD — N+1: separate query per item
async def get_items_with_users(db):
    items = await db.execute(select(Item))
    for item in items.scalars():
        user = await db.get(User, item.user_id)  # N queries

# GOOD — joinedload or selectinload
from sqlalchemy.orm import selectinload

async def get_items_with_users(db):
    result = await db.execute(
        select(Item).options(selectinload(Item.user))
    )
    return result.scalars().all()  # single query with JOIN

# RULE: use selectinload for collections, joinedload for single relationships
```

## Async Discipline

```python
# BAD — blocking call in async path
async def bad_endpoint():
    time.sleep(1)                          # blocks event loop
    result = requests.get("http://...")    # blocking HTTP

# GOOD — non-blocking
import asyncio
import httpx

async def good_endpoint():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        result = await client.get("http://...")

# For CPU-bound tasks, use run_in_executor
import asyncio
async def cpu_intensive():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, heavy_cpu_function, arg)
```

## Testing Strategy

```python
# conftest.py — real database, not mocked
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

TEST_DB_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def engine():
    return create_async_engine(TEST_DB_URL)

@pytest.fixture
async def db(engine):
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()  # clean state per test

@pytest.fixture
async def client(db):
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Unit test — domain service (no DB)
def test_calculate_discount():
    result = discount_service.calculate(price=100, code="HALF")
    assert result == 50

# Integration test — API + real DB
async def test_create_user(client, db):
    resp = await client.post("/api/v1/users", json={"email": "a@b.com"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "a@b.com"
```

## Config & Secrets

```python
# pydantic Settings — reads from env, never hardcoded
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    AUTH_ENABLED: bool = True

    class Config:
        env_file = ".env"  # development only; CI/prod use real env vars

settings = Settings()
```

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "alembic migration"
#       python scripts/search.py "N+1 query"
#       python scripts/search.py "async blocking"
```
