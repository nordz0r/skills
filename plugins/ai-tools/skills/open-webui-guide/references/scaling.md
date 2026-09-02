# Масштабирование и Production-деплой

## Содержание
1. [Архитектура для масштабирования](#архитектура-для-масштабирования)
2. [Чеклист production-деплоя](#чеклист-production-деплоя)
3. [База данных](#база-данных)
4. [Redis](#redis)
5. [WebSocket кластер](#websocket-кластер)
6. [Горизонтальное масштабирование](#горизонтальное-масштабирование)
7. [Docker Compose для production](#docker-compose-для-production)
8. [Kubernetes](#kubernetes)
9. [Reverse proxy](#reverse-proxy)
10. [Мониторинг](#мониторинг)
11. [Бэкапы](#бэкапы)
12. [Типичные проблемы при масштабировании](#типичные-проблемы)

---

## Архитектура для масштабирования

### Один сервер (до ~50 пользователей)

```
[Nginx] → [Open WebUI] → [SQLite] + [Ollama]
```

Подходит для небольших команд. SQLite с WAL, Ollama на той же машине.

### Средний масштаб (50-500 пользователей)

```
[Nginx/Traefik]
    ├── [Open WebUI #1] ──┐
    ├── [Open WebUI #2] ──┤── [PostgreSQL]
    └── [Open WebUI #3] ──┘        │
              │                     │
         [Redis] ←──────────────────┘
              │
    [Ollama / vLLM кластер]
```

### Высокая нагрузка (500+ пользователей)

```
[CDN/WAF]
    │
[Load Balancer (sticky sessions)]
    ├── [Open WebUI Pod #1-N] ──── [PostgreSQL Primary]
    │         │                         │
    │    [Redis Cluster/Sentinel]  [PostgreSQL Replica]
    │
    ├── [Ollama Pool]
    ├── [vLLM / TGI Pool]
    └── [Pipeline Servers]
```

---

## Чеклист production-деплоя

### Обязательно

- [ ] `WEBUI_SECRET_KEY` — стабильный случайный ключ (не менять после деплоя!)
- [ ] PostgreSQL вместо SQLite
- [ ] Redis для WebSocket и token revocation
- [ ] HTTPS (через reverse proxy)
- [ ] `WEBUI_AUTH_COOKIE_SECURE=true`
- [ ] `DEFAULT_USER_ROLE=pending` (ручное одобрение пользователей)
- [ ] Бэкапы БД

### Рекомендуется

- [ ] `ENABLE_AUDIT_LOGS_FILE=true`
- [ ] OpenTelemetry для мониторинга
- [ ] Rate limiting на уровне reverse proxy
- [ ] Ограничить `CORS_ALLOW_ORIGIN` до конкретного домена
- [ ] Настроить `DATABASE_POOL_SIZE` под нагрузку
- [ ] Мониторинг ресурсов (CPU, RAM, GPU)

---

## База данных

### PostgreSQL (рекомендация для production)

```env
DATABASE_URL=postgresql://openwebui:<your-password>@db.example.com:5432/openwebui
DATABASE_POOL_SIZE=50
DATABASE_POOL_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
```

### Оптимизация PostgreSQL

```sql
-- postgresql.conf
shared_buffers = 256MB           -- 25% RAM
effective_cache_size = 768MB     -- 75% RAM
work_mem = 16MB
maintenance_work_mem = 128MB
max_connections = 200
```

### Connection Pooling

Для высокой нагрузки используй PgBouncer:

```ini
# pgbouncer.ini
[databases]
openwebui = host=localhost dbname=openwebui

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 50
```

### Миграции

Open WebUI использует Alembic для миграций. Они запускаются автоматически при старте приложения. При обновлении версии:

1. Сделай бэкап БД
2. Обнови контейнер/код
3. Миграции применятся при первом запуске

---

## Redis

### Standalone

```env
REDIS_URL=redis://redis.example.com:6379/0
REDIS_KEY_PREFIX=owui:
```

### Sentinel (High Availability)

```env
REDIS_SENTINEL_HOSTS=sentinel1:26379,sentinel2:26379,sentinel3:26379
REDIS_SENTINEL_PORT=26379
```

### Cluster

```env
REDIS_URL=redis://redis-cluster:6379
REDIS_CLUSTER=true
```

### Для чего нужен Redis

| Функция | Без Redis | С Redis |
|---------|-----------|---------|
| JWT-отзыв | Не работает | Работает |
| WebSocket кластер | Не работает | Работает |
| Кэширование | Локальное | Распределённое |
| Pub/Sub | Не работает | Работает |

**Вывод**: Redis обязателен для любого кластера из 2+ экземпляров Open WebUI.

---

## WebSocket кластер

Без правильной настройки WebSocket нельзя масштабировать Open WebUI горизонтально — сообщения в реальном времени будут теряться.

```env
ENABLE_WEBSOCKET_SUPPORT=true
WEBSOCKET_MANAGER=redis
WEBSOCKET_REDIS_URL=redis://redis:6379/1
```

Это заставляет Socket.IO использовать Redis как message broker, так что сообщения доставляются всем подключённым клиентам, независимо от того, к какому экземпляру они подключены.

### Sticky Sessions

Socket.IO требует sticky sessions при использовании long-polling fallback. Настрой load balancer:

**Nginx:**
```nginx
upstream openwebui {
    ip_hash;  # sticky sessions
    server webui1:8080;
    server webui2:8080;
}
```

**Traefik:**
```yaml
services:
  openwebui:
    loadBalancer:
      sticky:
        cookie:
          name: owui_session
```

---

## Горизонтальное масштабирование

### Что масштабируется

- **Open WebUI (stateless)** — горизонтально, N экземпляров за load balancer
- **PostgreSQL** — вертикально или read replicas
- **Redis** — Sentinel или Cluster
- **Ollama** — каждый инстанс = 1 GPU, масштабируется горизонтально
- **Pipeline-серверы** — независимо

### Что НЕ масштабируется автоматически

- **SQLite** — один файл, один writer. Заменяй на PostgreSQL
- **Локальный WebSocket-менеджер** — заменяй на Redis
- **Файловое хранилище** — нужно shared storage (NFS, S3 + прослойка)

### Файловое хранилище в кластере

Open WebUI хранит загруженные файлы в `DATA_DIR/uploads/`. При нескольких экземплярах все должны видеть одни и те же файлы:

- **NFS**: монтируй `DATA_DIR` по NFS
- **S3-совместимое**: требуется кастомная интеграция или volume plugin
- **Один Volume (Docker)**: если все контейнеры на одном хосте

---

## Docker Compose для production

```yaml
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
    environment:
      - WEBUI_SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://owui:${DB_PASS}@db:5432/openwebui
      - REDIS_URL=redis://redis:6379/0
      - WEBSOCKET_MANAGER=redis
      - WEBSOCKET_REDIS_URL=redis://redis:6379/1
      - OLLAMA_BASE_URL=http://ollama:11434
      - ENABLE_WEBSOCKET_SUPPORT=true
      - WEBUI_AUTH_COOKIE_SECURE=true
      - DEFAULT_USER_ROLE=pending
    volumes:
      - shared-data:/app/backend/data
    depends_on:
      - db
      - redis

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: openwebui
      POSTGRES_USER: owui
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data

  ollama:
    image: ollama/ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - ollama-models:/root/.ollama

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - openwebui

volumes:
  shared-data:
  pgdata:
  redisdata:
  ollama-models:
```

---

## Kubernetes

### Основные ресурсы

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui
spec:
  replicas: 3
  selector:
    matchLabels:
      app: open-webui
  template:
    spec:
      containers:
        - name: open-webui
          image: ghcr.io/open-webui/open-webui:main
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: owui-secrets
                  key: database-url
            - name: REDIS_URL
              value: redis://redis-svc:6379/0
            - name: WEBSOCKET_MANAGER
              value: redis
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
          volumeMounts:
            - name: data
              mountPath: /app/backend/data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: owui-data
```

### Health check

Open WebUI предоставляет эндпоинт `/health` для проверки состояния.

---

## Reverse proxy

### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name chat.example.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # WebSocket support
    location /ws {
        proxy_pass http://openwebui;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Socket.IO
    location /socket.io {
        proxy_pass http://openwebui;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://openwebui;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Для загрузки файлов
        client_max_body_size 100M;
    }

    upstream openwebui {
        ip_hash;
        server webui1:8080;
        server webui2:8080;
    }
}
```

Критические моменты:
- **WebSocket**: обязательно проксируй `/socket.io` с заголовками Upgrade
- **Timeout**: `proxy_read_timeout 86400` для долгих стриминговых ответов
- **Body size**: `client_max_body_size` для загрузки файлов

---

## Мониторинг

### OpenTelemetry

```env
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=open-webui
```

Экспортирует:
- **Traces** — запросы через все слои
- **Metrics** — счётчики, гистограммы
- **Logs** — структурированные логи

Подключается к Jaeger, Grafana Tempo, Datadog и т.д.

### Аудит-логи

```env
ENABLE_AUDIT_LOGS_FILE=true
ENABLE_AUDIT_STDOUT=true
AUDIT_LOG_LEVEL=REQUEST        # NONE | METADATA | REQUEST | REQUEST_RESPONSE
```

- `METADATA` — кто, когда, какой эндпоинт
- `REQUEST` — + тело запроса
- `REQUEST_RESPONSE` — + тело ответа (осторожно: большой объём!)

---

## Бэкапы

### PostgreSQL

```bash
# Ежедневный бэкап
pg_dump -U owui openwebui | gzip > backup_$(date +%Y%m%d).sql.gz

# Восстановление
gunzip < backup_20240101.sql.gz | psql -U owui openwebui
```

### SQLite

```bash
# Бэкап (безопасный, с WAL)
sqlite3 data/webui.db ".backup data/webui_backup.db"
```

### Файлы

Не забудь бэкапить:
- `DATA_DIR/uploads/` — загруженные файлы
- `DATA_DIR/vector_db/` — векторная БД (если Chroma)
- `.env` файл или секреты

---

## Типичные проблемы

### WebSocket не работает в кластере
**Причина**: локальный WebSocket-менеджер, сообщения не доходят до других инстансов.
**Решение**: `WEBSOCKET_MANAGER=redis` + `WEBSOCKET_REDIS_URL=...`

### Сессии «слетают» при перезапуске
**Причина**: `WEBUI_SECRET_KEY` не задан — генерируется случайный при каждом старте.
**Решение**: Задать фиксированный `WEBUI_SECRET_KEY`.

### Файлы не видны на другом инстансе
**Причина**: `DATA_DIR` не расшарен между контейнерами.
**Решение**: NFS, shared volume, или S3.

### Медленные эмбеддинги
**Причина**: CPU-инференс sentence-transformers.
**Решение**: `SENTENCE_TRANSFORMERS_BACKEND=cuda` + GPU, или внешний сервис эмбеддингов.

### OOM при загрузке больших файлов в RAG
**Причина**: документ слишком большой, чанкинг съедает память.
**Решение**: увеличить лимиты памяти контейнера, уменьшить `RAG_CHUNK_SIZE`.
