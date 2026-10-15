---
name: docker-ops
description: "Hands-on Docker Engine and Docker Compose v2: Dockerfile, multi-stage, healthcheck, networks, volumes, bind mounts, logs, registry, docker compose up/down/config, BuildKit, non-root USER, restart policy. Use for any container task on a host: build an image, write compose.yaml, fix Restarting, read docker logs, docker inspect, overlay2, docker.sock, prune, CI image build. Triggers: docker, dockerfile, docker compose, compose.yaml, container, image build, docker logs, healthcheck, bind mount, docker network, registry, dind, контейнер, образ, логи, докер."
---

# Docker Ops

Skill for Docker Engine and Compose v2 on a Linux host. Hand over ready
`Dockerfile`/`compose.yaml` files and verification commands, not generic advice.

Do not use it as the primary skill for Kubernetes, GitLab YAML or the Ansible
`community.docker` module — those are `gitlab-ci` and `ansible-playbook`.
Handle GitLab `docker:dind` together with `gitlab-ci`.

## When to use

- Write or fix a Dockerfile / compose.yaml.
- Container is `Restarting`, unhealthy, cannot resolve DNS, cannot see a volume.
- Image build, tags, push to a registry.
- Networks, ports, bind mounts, named volumes, tmpfs.
- Logs, `inspect`, `events`, disk used by overlay2.

## Workflow

1. Confirm the runtime: `docker version`, `docker compose version`. Compose v2 is
   `docker compose`, not `docker-compose`.
2. If there is a compose file, run `docker compose config` and `ps -a` first.
3. Take symptoms from the container: `ps`, `logs --tail`, `inspect`, `health`.
4. Change code/config declaratively in the Dockerfile/compose; `docker exec` is not
   a permanent fix.
5. Verify: container healthy, port listening, volume in place, no `latest` tag
   in prod.

## Rules

- Pin tags. `latest` only for local experiments.
- In prod: non-root `USER`, `read_only` + `tmpfs` where possible, drop Linux caps.
- Config bind mounts: `:ro`. Data: a named volume or an explicit data path.
- A healthcheck is mandatory when `depends_on: condition` relies on it.
- No secrets in ENV baked into image history. Use `env_file`, tmpfs, Docker secrets.
- `network_mode: host` is the exception, not the default.

## Companion skills

- Host systemd/journald/disk → `administering-linux`.
- Builds in GitLab CI / dind / registry → `gitlab-ci`.
- Rolling out compose via Ansible → `ansible-playbook`.
- Amnezia containers `/opt/amnezia`: container ops stay here; AWG/Xray config values → `amnezia-vpn`.

## References

- `references/compose-and-dockerfile.md` — Dockerfile and Compose templates.
- `references/debug.md` — diagnosing containers, networks, disk, the daemon.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: docker dockerfile compose.yaml docker compose healthcheck bind mount overlay2 registry image build container logs inspect restarting dind buildkit
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
