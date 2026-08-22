# Project Context Artifact Format

Use this only when the user explicitly asks for documentation or when the final implementation plan needs a durable glossary, contract, or operating note. Do not create or update these artifacts automatically during the interview.

Prefer project or domain-specific docs under `docs/<project>/` or `docs/<domain>/` over a generic root context file.

## Glossary

For stable project terms:

```markdown
# <Project Or Domain> Glossary

## Terms

### <Term>

- Meaning: <business, product, technical, or ML meaning>
- Grain or scope: <request, user, account, event, row, job, model, document, etc.>
- Source: <database table, artifact, service, config, UI, manual process, or external system>
- Not the same as: <nearby overloaded terms>
- Used by: <services, scripts, artifacts, metrics, docs, dashboards, or issues>
```

Good terms are usually about ownership, data grain, contract meaning, model responsibility, workflow boundaries, or evaluation decisions. Avoid documenting transient implementation details.

## Contracts

For durable interfaces, data contracts, artifacts, or operating contracts:

```markdown
# <Project Or Domain> Contracts

## <Contract Name>

- Type: <API, table, artifact, event, model output, UI workflow, report, etc.>
- Location: `<path, endpoint, table, topic, dashboard, or service>`
- Producer: `<service, script, job, team, or manual process>`
- Consumers: `<services, scripts, users, teams, notebooks, dashboards, or reports>`
- Grain: <one row per ...>
- Keys: <unique or grouping keys>
- Required fields:
  - `<field>`: <type and meaning>
- Null or error semantics: <allowed, rejected, defaulted, retried, or surfaced>
- Timing and consistency: <freshness, ordering, latency, idempotency, or backfill assumptions>
- Validation: <unit test, contract test, smoke run, row count, schema check, or dashboard>
```

## Operational Notes

For runbooks or operational ledgers, record:

- date and owner
- artifact hashes, build IDs, dataset versions, or release IDs when available
- run IDs, dashboards, metric gates, or issue links
- decisions made
- blockers
- next action
