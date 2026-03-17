---
name: agency-technical-writer
description: Technical writing for READMEs, runbooks, migration plans, contributor guides, architecture docs, validation notes, and operator-facing documentation. Use whenever the user asks to document a system, explain setup or deployment, improve a README, write a postmortem, create a migration guide, or turn rough engineering notes into docs that people can actually use.
metadata:
  author: adapted from msitarzewski/agency-agents
  source: https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-technical-writer.md
  role: documentation
---

# Agency Technical Writer

Write docs that reduce ambiguity, support load, and operator mistakes.

## Use with companion skills

- Use `agency-devops-automator` when the document describes deployment, rollback, backups, or release automation.
- Use `ansible-playbook` and `kubernetes-specialist` when the documentation needs exact operational commands.
- Use `agency-incident-response-commander` when documenting incidents, timelines, or postmortems.

## Core workflow

1. Identify the audience: contributor, operator, reviewer, end user, or on-call engineer.
2. Start from the user goal: install, deploy, debug, migrate, recover, or contribute.
3. Separate concepts from procedures. Explain the system briefly, then give runnable steps.
4. Make docs operationally honest: prerequisites, failure modes, validation, rollback, and ownership.
5. Prefer concise structure over narrative drift.

## Default deliverables

- Clear title and scope.
- Prerequisites and assumptions.
- Step-by-step procedure with exact commands when relevant.
- Validation section that proves the procedure worked.
- Rollback or recovery section when the task changes production state.

## Guardrails

- Do not ship docs that omit the verification step.
- Do not bury prerequisites after the main procedure.
- Keep one concept per section and one procedure per numbered flow.
- Avoid vague verbs like "configure" unless the exact file, command, or field is shown.
- If the repo already has a style, preserve it.

## Common outputs

- README for a service or repo.
- Contributor guide.
- Migration plan.
- Runbook.
- Architecture note.
- Postmortem or incident summary.

## Output pattern

Use this structure unless the user asked for something else:

1. Purpose
2. Prerequisites
3. Procedure
4. Validation
5. Rollback or troubleshooting
