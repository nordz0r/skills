---
name: agency-database-optimizer
description: Database design, migration safety, indexing, EXPLAIN analysis, query tuning, connection management, and production-safe PostgreSQL or MySQL changes. Use whenever the user mentions Postgres, PostgreSQL, MySQL, MariaDB, slow queries, schema design, migrations, locking risk, indexing, or wants to move an app between database engines safely.
metadata:
  author: adapted from msitarzewski/agency-agents
  source: https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-database-optimizer.md
  role: database-performance
---

# Agency Database Optimizer

Treat database changes as production changes, not just SQL edits.

## Use with companion skills

- Use `agency-devops-automator` when DB changes are part of a deployment pipeline or migration wave.
- Use `agency-sre` when performance or availability symptoms need measurement and alerting.
- Use `nextcloud-admin` when the task touches a live Nextcloud instance and app or user state matters.

## Core workflow

1. Understand the workload: read-heavy, write-heavy, mixed, batch, background jobs, or latency-sensitive paths.
2. Identify risk before tuning: data size, lock scope, migration direction, rollback path, backup freshness, and maintenance window.
3. Analyze queries with evidence. Prefer `EXPLAIN`, `EXPLAIN ANALYZE`, actual row counts, and index coverage over hunches.
4. Fix the data access pattern before brute-force scaling. Remove N+1 patterns, bad filters, or missing predicates before adding hardware.
5. Make migrations reversible when feasible and explicit about irreversibility when not.

## Default deliverables

- Query or schema diagnosis with the likely bottleneck.
- Safe migration plan, including backup and rollback implications.
- Recommended indexes, schema changes, or query rewrites.
- Validation steps for correctness and performance after the change.

## Guardrails

- Take backups seriously before invasive changes.
- Call out lock risk and long-running migration risk explicitly.
- Avoid hand-wavy "add an index" advice without tying it to query shape.
- Prefer Postgres-native patterns when the target system is PostgreSQL; do not carry MySQL assumptions blindly.
- Preserve application compatibility: drivers, connection strings, collations, text search, and transaction semantics matter.

## Useful review angles

- Missing indexes on join keys and common filter columns.
- Partial or composite indexes for dominant query patterns.
- Connection pool sizing and idle transaction issues.
- ORM-generated query bloat or N+1 behavior.
- Engine migration gaps: JSON behavior, full-text search, autoincrement semantics, timezone handling.

## Output pattern

Use this structure unless the user asked for something else:

1. Current workload and risk profile
2. Findings
3. Recommended schema or query changes
4. Migration and rollback notes
5. Validation commands or checks
