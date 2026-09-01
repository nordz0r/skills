---
name: docker-ops
description: >-
  Практическая работа с Docker Engine и Docker Compose v2: Dockerfile,
  multi-stage, healthcheck, сети, volumes, bind mounts, логи, registry,
  docker compose up/down/config, BuildKit, non-root USER, restart policy.
  Используй этот skill при любых задачах по контейнерам на хосте: собрать
  образ, написать compose.yaml, починить Restarting, разобрать docker logs,
  docker inspect, overlay2, docker.sock, prune, CI image build. Триггеры:
  docker, dockerfile, docker compose, compose.yaml, container, image build,
  docker logs, healthcheck, bind mount, docker network, registry, dind.
---

# Docker Ops

Skill для Docker Engine и Compose v2 на Linux-хосте. Отдавай готовые
`Dockerfile`/`compose.yaml` и команды проверки, не общие советы.

Не используй как основной skill для Kubernetes, GitLab YAML или Ansible
модуля `community.docker` — там `gitlab-ci` и `ansible-playbook`.
GitLab `docker:dind` разбирай вместе с `gitlab-ci`.

## Когда использовать

- Написать или починить Dockerfile / compose.yaml.
- Контейнер в `Restarting`, unhealthy, не резолвит DNS, не видит volume.
- Сборка образа, теги, push в registry.
- Сети, порты, bind mounts, named volumes, tmpfs.
- Логи, `inspect`, `events`, disk от overlay2.

## Workflow

1. Уточни runtime: `docker version`, `docker compose version`. Compose v2 —
   это `docker compose`, не `docker-compose`.
2. Если есть compose — сначала `docker compose config` и `ps -a`.
3. Симптом снимай с контейнера: `ps`, `logs --tail`, `inspect`, `health`.
4. Код/конфиг меняй декларативно в Dockerfile/compose, не `docker exec` как
   постоянный фикс.
5. Проверка: контейнер healthy, порт слушает, volume на месте, тег не `latest`
   в prod.

## Правила

- Теги фиксируй. `latest` только для локального эксперимента.
- В prod — `USER` не root, `read_only` + `tmpfs` где можно, drop Linux caps.
- Bind-mount конфигов: `:ro`. Данные — named volume или явный data-path.
- Healthcheck обязателен, если от него зависит `depends_on: condition`.
- Секреты не в ENV в image history. `env_file`, tmpfs, Docker secrets.
- `network_mode: host` — исключение, не дефолт.

## Companion skills

- Хост systemd/journald/диск → `administering-linux`.
- Сборка в GitLab CI / dind / registry → `gitlab-ci`.
- Раскатка compose через Ansible → `ansible-playbook`.
- Amnezia-контейнеры `/opt/amnezia` → `amnezia-vpn`.

## References

- `references/compose-and-dockerfile.md` — шаблоны Dockerfile и Compose.
- `references/debug.md` — диагностика контейнеров, сетей, диска, daemon.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: docker dockerfile compose.yaml docker compose healthcheck bind mount overlay2 registry image build container logs inspect restarting dind buildkit
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
