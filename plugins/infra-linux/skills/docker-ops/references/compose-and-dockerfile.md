# Dockerfile и Compose v2

## Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS build
WORKDIR /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim
RUN useradd --system --home-dir /app --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=build /install /usr/local
COPY --chown=app:app app/ /app/
USER app
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"
ENTRYPOINT ["python", "-m", "app"]
```

Правила:

- Multi-stage, чтобы builder toolchain не попал в runtime.
- `--mount=type=cache` для apt/pip/go — быстрее и меньше слой-шум.
- Не ставь `latest`. Не копируй `.env` и ключи в образ.
- `ENTRYPOINT` — процесс приложения PID 1. Не `bash -c` без `exec`.

Сборка:

```bash
docker buildx build --load -t registry.example.com/app:1.4.2 .
docker image inspect registry.example.com/app:1.4.2 --format '{{.Config.User}} {{.Config.ExposedPorts}}'
```

## compose.yaml

```yaml
name: app
services:
  api:
    image: registry.example.com/app:1.4.2
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file:
      - ./api.env
    environment:
      TZ: Europe/Moscow
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - api-data:/var/lib/app
      - ./config/api.yaml:/app/config.yaml:ro
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"]
      interval: 15s
      timeout: 3s
      retries: 3
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16.6
    restart: unless-stopped
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD_FILE: /run/secrets/pg_password
    secrets:
      - pg_password
    volumes:
      - pg-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 10s
      timeout: 5s
      retries: 5
    ports: []

secrets:
  pg_password:
    file: ./secrets/pg_password

volumes:
  api-data:
  pg-data:

networks:
  default:
    name: app-net
```

Публикация порта наружу — только если это нужно. Иначе `127.0.0.1:` или без `ports`.

## Команды Compose

```bash
docker compose config
docker compose up -d --remove-orphans
docker compose ps -a
docker compose logs -f --tail=200 api
docker compose restart api
docker compose pull && docker compose up -d
docker compose down             # сети/контейнеры, volumes остаются
docker compose down -v          # уничтожит named volumes
```

`up` без `--remove-orphans` оставляет старые сервисы после переименования.

## Сети и DNS

Compose DNS-имя = имя сервиса (`postgres`, не контейнер hostname).
Проверка из контейнера:

```bash
docker compose exec api getent hosts postgres
docker compose exec api wget -qO- http://127.0.0.1:8080/health
```
