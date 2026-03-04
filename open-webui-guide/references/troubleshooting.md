# Отладка и решение проблем

## Содержание
1. [Диагностика](#диагностика)
2. [Проблемы при запуске](#проблемы-при-запуске)
3. [Проблемы авторизации](#проблемы-авторизации)
4. [Проблемы с моделями](#проблемы-с-моделями)
5. [Проблемы с RAG/Knowledge](#проблемы-с-rag)
6. [Проблемы WebSocket](#проблемы-websocket)
7. [Проблемы производительности](#проблемы-производительности)
8. [Проблемы Docker](#проблемы-docker)
9. [Логирование](#логирование)

---

## Диагностика

### Первые шаги при любой проблеме

1. **Проверь логи**:
   ```bash
   docker logs open-webui --tail 100
   docker compose logs -f openwebui
   ```

2. **Проверь health**:
   ```bash
   curl http://localhost:8080/health
   ```

3. **Включи DEBUG-логирование**:
   ```env
   GLOBAL_LOG_LEVEL=DEBUG
   ```

4. **Проверь переменные окружения**:
   ```bash
   docker exec open-webui env | sort
   ```

---

## Проблемы при запуске

### Контейнер падает сразу после старта

**Порт занят**:
```bash
lsof -i :8080
# или
netstat -tlnp | grep 8080
```

**Нет прав на директорию данных**:
```bash
ls -la /path/to/data
chmod -R 777 /path/to/data  # только для отладки!
```

**Ошибка миграции БД**:
```bash
docker logs open-webui 2>&1 | grep -i "migration\|alembic\|error"
```
Решение: бэкап БД, затем пересоздание, или ручной запуск `alembic upgrade head`.

---

## Проблемы авторизации

### «Invalid credentials»

1. Пароль: bcrypt обрезает всё после 72 байт — длинные пароли могут не работать
2. Забыл пароль админа — задай нового через env:
   ```env
   WEBUI_ADMIN_EMAIL=new@email.com
   WEBUI_ADMIN_PASSWORD=newpassword
   ```

### Сессии слетают после перезапуска

`WEBUI_SECRET_KEY` не задан — при каждом старте генерируется случайный, и старые JWT становятся невалидными:
```env
WEBUI_SECRET_KEY=my-permanent-secret-key
```

### OAuth — redirect_uri mismatch

1. URL в env должен точно совпадать с настройкой в провайдере
2. Проверь протокол (`https` vs `http`) и trailing slash
3. За reverse proxy: URL должен быть внешним, не внутренним

### OAuth — аккаунт не создаётся

- `ENABLE_OAUTH_SIGNUP=true` — разрешить регистрацию через OAuth
- `DEFAULT_USER_ROLE=pending` — пользователь создан, но ждёт одобрения

### API-ключ не работает

- Формат: `Authorization: Bearer sk-xxxxx`
- Проверь `expires_at` — ключ может быть истёкшим
- Проверь роль пользователя-владельца ключа

---

## Проблемы с моделями

### Не видны модели Ollama

1. Проверь URL из контейнера:
   ```bash
   docker exec open-webui curl http://ollama:11434/api/tags
   ```
2. Если Ollama на хосте: `OLLAMA_BASE_URL=http://host.docker.internal:11434`
3. Ollama слушает только localhost? Запусти: `OLLAMA_HOST=0.0.0.0 ollama serve`

### Стриминг обрывается

1. Reverse proxy — увеличь таймауты:
   ```nginx
   proxy_read_timeout 300;
   proxy_send_timeout 300;
   proxy_buffering off;
   ```
2. Cloudflare: включи WebSocket support
3. AWS ALB: увеличь idle timeout

### Медленная генерация

- `ollama ps` — проверь, что модель на GPU
- `nvidia-smi` — есть ли свободная VRAM
- Мало VRAM — используй quantized-модель (Q4_K_M)

---

## Проблемы с RAG

### Файл не индексируется

1. Проверь формат: PDF, DOCX, TXT, MD, CSV — поддерживаются
2. PDF со сканами: нужен OCR
3. Проверь логи: `docker logs open-webui 2>&1 | grep -i "embed\|chunk\|rag"`

### Нерелевантные результаты

1. Модель эмбеддингов: для русского текста — `multilingual-e5-large` или `intfloat/multilingual-e5-base`
2. Уменьши `RAG_CHUNK_SIZE` (800–1000) и увеличь `RAG_CHUNK_OVERLAP` (200)
3. Включи реранкинг: `RAG_RERANKING_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2`

### OOM при индексации

- Увеличь RAM контейнера
- Используй лёгкую модель эмбеддингов (`all-MiniLM-L6-v2`)

---

## Проблемы WebSocket

### Чат не обновляется в реальном времени

1. `ENABLE_WEBSOCKET_SUPPORT=true`
2. Reverse proxy — нужны заголовки:
   ```nginx
   proxy_http_version 1.1;
   proxy_set_header Upgrade $http_upgrade;
   proxy_set_header Connection "upgrade";
   ```
3. DevTools → Network → WS — проверь handshake

### Частые реконнекты

- Увеличь `WEBSOCKET_SERVER_PING_TIMEOUT=60`
- Nginx: `proxy_read_timeout 86400;`

### Кластер: события не доходят

- `WEBSOCKET_MANAGER=redis` настроен?
- Redis доступен со всех инстансов?
- Sticky sessions на LB?

---

## Проблемы производительности

### Высокий CPU

- Эмбеддинги грузят CPU → переключи на GPU или внешний сервис
- SQLite под нагрузкой → мигрируй на PostgreSQL

### Высокая память

- Модель эмбеддингов в RAM → используй меньшую или выгрузи
- Утечка памяти → Docker restart policy (`unless-stopped`)

### Медленный UI

- Много чатов → архивируй старые
- Большие чаты → разбивай на новые

---

## Проблемы Docker

### Нет GPU

```bash
# Проверь runtime
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
# Нет? → установи nvidia-container-toolkit
```

### Данные потеряны после пересоздания

Обязательно монтируй volume:
```bash
docker run -v open-webui-data:/app/backend/data ...
```

### Не подключается к localhost

Из контейнера `localhost` = сам контейнер. Используй:
- `host.docker.internal` (Docker Desktop)
- `172.17.0.1` (Linux bridge)
- Docker network + имя сервиса

---

## Логирование

```env
GLOBAL_LOG_LEVEL=DEBUG     # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json            # для ELK/Loki

# Аудит-логи
ENABLE_AUDIT_LOGS_FILE=true
ENABLE_AUDIT_STDOUT=true
AUDIT_LOG_LEVEL=REQUEST    # NONE | METADATA | REQUEST | REQUEST_RESPONSE
```

### Полезные grep-паттерны

```bash
docker logs open-webui 2>&1 | grep -i "error\|exception\|traceback"
docker logs open-webui 2>&1 | grep -i "auth\|login\|token"
docker logs open-webui 2>&1 | grep -i "ollama\|openai\|model"
docker logs open-webui 2>&1 | grep -i "socket\|websocket"
```
