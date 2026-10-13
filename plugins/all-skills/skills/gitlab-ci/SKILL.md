---
name: gitlab-ci
description: "Self-hosted GitLab CI: .gitlab-ci.yml, MR pipelines, kaniko, CI_REGISTRY_IMAGE, when:manual, rules, runners, docker:dind. Not GitHub Actions and not generic Terraform. Triggers: gitlab-ci, gitlab runner, .gitlab-ci.yml, kaniko, CI_REGISTRY, dind, pipeline failed, include:component."
---

# GitLab CI

Skill for GitLab CI/CD, especially self-hosted. Write YAML and runner commands
that can be rolled out right away.

Do not use it for GitHub Actions (`gh-actions`), and do not use it instead of
`docker-ops` when the task is only about a Dockerfile without a pipeline.

## When to use

- Build or fix `.gitlab-ci.yml`.
- Job failed, YAML invalid, runner offline, dind cannot see docker.sock.
- Registry login, tag, push.
- include/templates/components, rules, workflow, needs.
- Runner: docker/shell/k8s executor, tags, privileged, tokens.

## Workflow

1. Pin down GitLab and the runner: instance version, executor, tags, protected.
2. Read the pipeline as a DAG: `stages` vs `needs`, `rules`, `workflow:rules`.
3. Do not use deprecated `only:`/`except:` — `rules:` only.
4. Pin images and tags. `image: docker:latest` is not acceptable.
5. Secrets: masked/protected CI variables, Vault, file-type variables.
   No `CI_JOB_TOKEN` into another project without an explicit job token allowlist.
6. Verify: pipeline editor / `glab ci lint`, then an empty MR pipeline,
   then a deploy job with `when: manual` for prod.

## Minimal skeleton

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH

stages: [build, test, deploy]

default:
  interruptible: true

variables:
  FF_TIMESTAMPS: "true"

include:
  - local: /ci/templates/*.yml
```

## Companion skills

- Dockerfile/compose inside a job → `docker-ops`.
- Host deploy via Ansible from a job → `ansible-playbook`.
- Delivery/rollback as a process → `agency-devops-automator`.

## References

- `references/pipelines.md` — YAML patterns: build, dind, rules, cache.
- `references/runners.md` — runner tokens, executors, dind, registry.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: gitlab gitlab-ci .gitlab-ci.yml runner dind CI_REGISTRY CI_JOB_TOKEN rules include component artifacts cache pipeline job failed
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
