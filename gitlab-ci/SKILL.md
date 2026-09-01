---
name: gitlab-ci
description: >-
  Практическая работа с self-hosted GitLab CI/CD: .gitlab-ci.yml, rules,
  include/components, needs DAG, cache/artifacts, environments, GitLab
  Container Registry, runners (docker/shell/kubernetes), docker:dind,
  CI_JOB_TOKEN, masked variables, CI/CD catalogs. Используй этот skill при
  любых задачах по GitLab pipeline, runner, .gitlab-ci.yml, registry,
  merge request pipelines, job failed, yaml invalid, dind TLS, runner
  registration/authentication token. Триггеры: gitlab, gitlab-ci,
  .gitlab-ci.yml, gitlab runner, dind, CI_REGISTRY, CI_JOB_TOKEN,
  pipeline failed, include:component, rules:if.
---

# GitLab CI

Skill для GitLab CI/CD, особенно self-hosted. Пиши YAML и команды runner'а,
которые можно сразу катить.

Не используй для GitHub Actions (`gh-actions`) и не подменяй собой
`docker-ops`, если задача только про Dockerfile без pipeline.

## Когда использовать

- Собрать или починить `.gitlab-ci.yml`.
- Job failed, YAML invalid, runner offline, dind не видит docker.sock.
- Registry login, tag, push.
- include/templates/components, rules, workflow, needs.
- Runner: executor docker/shell/k8s, tags, privileged, tokens.

## Workflow

1. Зафиксируй GitLab и runner: версия инстанса, executor, tags, protected.
2. Читай pipeline как DAG: `stages` vs `needs`, `rules`, `workflow:rules`.
3. Не используй deprecated `only:`/`except:` — только `rules:`.
4. Образы и теги пинь. `image: docker:latest` не годится.
5. Секреты — masked/protected CI variables, Vault, file-type variables.
   Не `CI_JOB_TOKEN` в чужой проект без явной job token allowlist.
6. Проверка: pipeline editor / `glab ci lint`, затем пустой MR pipeline,
   затем deploy job с `when: manual` на prod.

## Минимальный каркас

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

- Dockerfile/compose внутри job → `docker-ops`.
- Деплой хоста через Ansible из job → `ansible-playbook`.
- Обвязка delivery/rollback как процесс → `agency-devops-automator`.

## References

- `references/pipelines.md` — YAML-паттерны: build, dind, rules, cache.
- `references/runners.md` — runner tokens, executors, dind, registry.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: gitlab gitlab-ci .gitlab-ci.yml runner dind CI_REGISTRY CI_JOB_TOKEN rules include component artifacts cache pipeline job failed
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
