---
name: ci-deploy
description: "CI/CD and deployment intelligence. Docker, docker compose, GitLab CI, GitHub Actions, VPS deploy, Caddy, nginx, containers, pipelines, builds. Actions: build, deploy, fix CI, debug pipeline, dockerize, push image, run container, configure CI, write Dockerfile, write gitlab-ci.yml, write github workflow, rollback, restart service, harden production, add healthcheck, configure reverse proxy, zero-downtime deploy, force-recreate, shell scripting for CI. Files: Dockerfile, docker-compose.yml, .gitlab-ci.yml, .github/workflows/*.yml, Makefile, Caddyfile, nginx.conf. Symptoms: CI fails, build fails, deploy hangs, container exits, pipeline error, job fails, compose run hangs, stdin issue, TTY issue, shell quoting error, permission denied in container, port not exposed, healthcheck failing, service not restarting, rollback needed, CI debug by pushing."
---
# CI-Deploy — Container, CI/CD & Deployment Intelligence

The skill for everything from Dockerfile authorship to VPS production deploys. Targets the single most expensive pattern in your git history: push → watch CI fail → patch → repeat. The rule is **CI must pass locally first** — every CI step is reproducible as a plain shell command.

## When to Apply

### Must Use

- Writing or editing a Dockerfile, docker-compose.yml, .gitlab-ci.yml, .github/workflows/*.yml
- Debugging a CI failure (any stage: build, test, deploy)
- Writing a deploy script or Makefile deploy target
- Configuring a reverse proxy (Caddy, nginx) or production hardening
- Any `docker compose run` in a shell script (stdin/TTY traps)
- After any change to CI pipeline config before pushing
- Rolling back a deploy or diagnosing a failed deploy

### Recommended

- Adding a new service to docker-compose
- Changing environment variable handling between dev and prod
- Writing a Makefile with build/test/run/deploy targets
- First deploy to a new VPS
- Any production hardening pass

### Skip

- Pure application logic with no infra changes
- Database query optimization
- ML training without serving component
- API design with no deploy concern

## Rule Categories by Priority

| Priority | Category | Impact | Key Checks | Anti-Patterns |
|---|---|---|---|---|
| 1 | Local-first CI | CRITICAL | Run every CI step locally before push | Push → fail → patch loop |
| 2 | Shell quoting | CRITICAL | Quote all vars; use set -euo pipefail | Unquoted vars in YAML scripts |
| 3 | stdin/TTY | CRITICAL | Use -T flag with compose run in scripts | Hanging compose run in CI |
| 4 | Docker hygiene | HIGH | Non-root, healthcheck, .dockerignore, multi-stage | Root user in container; no healthcheck |
| 5 | Secret handling | HIGH | Env vars only; never bake secrets into image | ARG SECRET in Dockerfile |
| 6 | Deploy safety | HIGH | Backup before; test rollback path; --force-recreate | Deploy without rollback plan |
| 7 | Reverse proxy | MEDIUM | Caddy auto-HTTPS; nginx upstream health | Proxy to 0.0.0.0 without auth |
| 8 | Image caching | MEDIUM | BuildKit cache mounts; layer order | Invalidating cache on every build |

## The Local-First CI Protocol

Before any push to a branch that runs CI:

1. **Identify the failing CI step.** Read the `.gitlab-ci.yml` or `.github/workflows/*.yml` job.
2. **Reproduce it locally** as a plain shell command (no CI runner needed):
   ```bash
   # CI script says:  docker compose run app pytest
   # Reproduce:
   docker compose run -T --rm app pytest
   ```
3. **Fix it locally until it passes.**
4. Then push. CI will pass.

**Never patch by pushing.** Every "Fix CI: …" commit that could have been a local fix is a violation of this protocol.

## Shell Quoting Rules for YAML

```yaml
# BAD — unquoted: fails when value has spaces or special chars
script:
  - echo $MY_VAR
  - docker run $IMAGE_NAME

# GOOD — always quote
script:
  - echo "$MY_VAR"
  - docker run "$IMAGE_NAME"

# BAD — missing pipefail: silent failures pass CI
script:
  - ./build.sh && ./test.sh

# GOOD — explicit failure propagation
script:
  - set -euo pipefail
  - ./build.sh
  - ./test.sh
```

## stdin/TTY Trap — docker compose run

```bash
# BAD — hangs in CI (no TTY available)
docker compose run app python manage.py migrate

# GOOD — always use -T in scripts/CI; --rm cleans up
docker compose run -T --rm app python manage.py migrate

# BAD — stdin consumed by compose, kills calling script
deploy.sh:
  docker compose run app ./entrypoint.sh

# GOOD — redirect stdin explicitly
docker compose run -T --rm app ./entrypoint.sh < /dev/null
```

## Dockerfile — Non-Negotiable Rules

```dockerfile
# 1. Multi-stage: separate build from runtime
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

# 2. Non-root user (REQUIRED)
RUN useradd -m appuser
USER appuser

# 3. Healthcheck (REQUIRED for compose services)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 4. EXPOSE the port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## .dockerignore — Always Present

```
.git
.env
.env.*
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
node_modules
.venv
venv
dist
build
*.log
artifacts/
```

## Docker Compose — Dev vs Prod Pattern

```yaml
# docker-compose.yml (base, shared)
services:
  app:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}

# docker-compose.override.yml (dev — auto-loaded locally)
services:
  app:
    volumes:
      - .:/app
    command: uvicorn app.main:app --reload

# docker-compose.prod.yml (prod — explicit)
services:
  app:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

## GitLab CI Pipeline Structure

```yaml
stages:
  - verify
  - build
  - test
  - deploy

variables:
  IMAGE_TAG: "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"

verify:
  stage: verify
  script:
    - make verify  # same command as local

build:
  stage: build
  script:
    - docker build -t "$IMAGE_TAG" .
    - docker push "$IMAGE_TAG"

deploy:
  stage: deploy
  script:
    - make deploy IMAGE_TAG="$IMAGE_TAG"
  only:
    - main
```

## VPS Deploy Playbook

```bash
#!/bin/bash
set -euo pipefail

# 1. Pull new image
docker pull "$IMAGE_TAG"

# 2. Backup DB before any migration
pg_dump "$DATABASE_URL" > "backup_$(date +%Y%m%d_%H%M%S).sql"

# 3. Run migrations
docker compose run -T --rm app alembic upgrade head

# 4. Zero-downtime restart (force-recreate ensures new image)
docker compose up -d --force-recreate --no-deps app

# 5. Verify service is healthy
sleep 5
curl -f http://localhost/health || { echo "Deploy failed — rolling back"; docker compose down && docker compose up -d; exit 1; }

echo "Deploy successful: $IMAGE_TAG"
```

## Caddy Reverse Proxy (preferred)

```caddyfile
yourdomain.com {
    reverse_proxy localhost:8000
    # Caddy handles TLS automatically via Let's Encrypt
}

# With basic auth gate for staging
staging.yourdomain.com {
    basicauth {
        admin $2a$14$...  # bcrypt hash
    }
    reverse_proxy localhost:8001
}
```

## Production Hardening Checklist

Use `scripts/search.py "production hardening"` for full list. Key items:

- [ ] Non-root user in all containers
- [ ] No secrets in environment via `.env` checked in (use secrets manager or CI vars)
- [ ] Healthcheck on all compose services
- [ ] `restart: unless-stopped` on all prod services
- [ ] `--force-recreate` in deploy (ensures new image, not cached layer)
- [ ] Basic-auth or auth middleware on any admin/staging endpoint
- [ ] Firewall allows only 80/443 + SSH on VPS
- [ ] `make deploy` runs the same script CI runs (no manual steps)
- [ ] Rollback tested in staging before going to prod

## Search

```bash
python scripts/search.py "<query>"
# e.g.: python scripts/search.py "compose run hang"
#       python scripts/search.py "gitlab ci quoting"
#       python scripts/search.py "non-root container"
```
