# GitLab Runner

## Токены

Registration token (`gitlab-runner register --registration-token`) устарел.
С GitLab 16+ используй authentication token runner'а, созданный в UI
(instance / group / project) или API.

```bash
gitlab-runner --version
gitlab-runner status
gitlab-runner verify
gitlab-runner list
```

`config.toml` живёт в `/etc/gitlab-runner/config.toml` на хосте или
в volume контейнера runner'а.

Не коммить `config.toml` с токенами.

## Docker executor (типичный self-hosted)

```toml
concurrent = 4
check_interval = 3

[session_server]
  session_timeout = 1800

[[runners]]
  name = "docker-host-01"
  url = "https://gitlab.example.com"
  token = "glrt-..."
  executor = "docker"
  [runners.docker]
    image = "python:3.12-bookworm"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 268435456
    network_mtu = 0
    tls_verify = false
    allowed_images = ["python:*", "docker:*", "registry.example.com/*"]
    allowed_services = ["docker:*", "postgres:*", "redis:*"]
```

`privileged = true` нужен почти только для dind. Не включай на shared runner.

## Runner в Docker

```bash
docker run -d --name gitlab-runner --restart unless-stopped \
  -v gitlab-runner-config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:v17.11.0
```

Socket mount даёт runner'у управление Docker-хостом. Это полный root.
Для изоляции — отдельный VM или Kubernetes executor.

## Offline / stuck jobs

```bash
gitlab-runner verify
journalctl -u gitlab-runner -e --no-pager
docker logs gitlab-runner --tail 200
ss -lntup | grep gitlab
```

Частые причины:

- Неверный `url` (внутренний hostname, который runner не резолвит).
- Token reset в UI, а `config.toml` старый.
- Disk full на `/var/lib/docker` → executor не стартует контейнер.
- Tags на job есть, на runner нет (или наоборот `untagged`).
- Protected runner, а pipeline с unprotected branch.

Job tags должны совпасть. Job без tags не поедет на runner с
`run_untagged = false`.

## Registry с self-signed / внутренним CA

На runner host:

```bash
mkdir -p /etc/docker/certs.d/registry.example.com
cp corp-ca.crt /etc/docker/certs.d/registry.example.com/ca.crt
systemctl restart docker
```

В kaniko — `--registry-certificate` или монтирование CA.

## Job token allowlist

По умолчанию `CI_JOB_TOKEN` из проекта A не ходит в проект B.
Для `include:project` и pull образов из чужого registry-проекта добавь
allowlist в Settings → CI/CD → Job token permissions.

## Безопасность

- Shared runner = любой, кто может создать проект, выполняет код на этом хосте.
- Не используй shell executor для untrusted проектов.
- Masked variables + protected variables на prod deploy.
- Cache на shared runner может утечь между jobs, если ключ слабый.
