# Конфигурация и переменные окружения

## Содержание
1. [Как работает конфигурация](#как-работает-конфигурация)
2. [Критические переменные](#критические-переменные)
3. [Аутентификация](#аутентификация)
4. [База данных](#база-данных)
5. [Redis](#redis)
6. [LLM-провайдеры](#llm-провайдеры)
7. [RAG и эмбеддинги](#rag-и-эмбеддинги)
8. [WebSocket](#websocket)
9. [Аудио (TTS/STT)](#аудио)
10. [Изображения](#изображения)
11. [Логирование и мониторинг](#логирование-и-мониторинг)
12. [Безопасность](#безопасность)
13. [Прочие настройки](#прочие-настройки)

---

## Как работает конфигурация

Open WebUI читает конфигурацию из двух источников:
1. **Переменные окружения** (`env.py`) — читаются при старте, не меняются без перезапуска
2. **БД-конфигурация** (`config.py`) — динамическая, меняется через админ-панель или API

Приоритет: переменные окружения > БД. Некоторые настройки доступны только через env, другие — через оба механизма.

Ключевые файлы:
- `backend/open_webui/env.py` — переменные окружения
- `backend/open_webui/config.py` — логика конфигурации

---

## Критические переменные

Эти переменные **обязательно** установить в production:

```env
# Секрет для JWT — без него сессии сбрасываются при перезапуске!
WEBUI_SECRET_KEY=your-secure-random-string-here

# База данных — по умолчанию SQLite, для production используй PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/openwebui

# URL Ollama (если используешь локальные модели)
OLLAMA_BASE_URL=http://localhost:11434

# Redis (для масштабирования и отзыва токенов)
REDIS_URL=redis://localhost:6379/0
```

---

## Аутентификация

```env
# Основные
WEBUI_AUTH=true                          # включить аутентификацию
WEBUI_SECRET_KEY=                        # JWT-секрет (ОБЯЗАТЕЛЬНО для production!)
JWT_EXPIRES_IN=24h                       # время жизни токена

# Регистрация
ENABLE_SIGNUP=true                       # разрешить регистрацию
ENABLE_PASSWORD_AUTH=true                # разрешить вход по паролю
ENABLE_INITIAL_ADMIN_SIGNUP=true         # первый пользователь = admin
DEFAULT_USER_ROLE=pending                # роль новых пользователей

# Авто-создание админа
WEBUI_ADMIN_EMAIL=admin@example.com
WEBUI_ADMIN_PASSWORD=
WEBUI_ADMIN_NAME=Admin

# Пароли
ENABLE_PASSWORD_VALIDATION=false
PASSWORD_VALIDATION_REGEX_PATTERN=

# Cookie
WEBUI_SESSION_COOKIE_SAME_SITE=lax       # lax | strict | none
WEBUI_AUTH_COOKIE_SECURE=false            # true для HTTPS
WEBUI_AUTH_COOKIE_HTTP_ONLY=true

# OAuth
ENABLE_OAUTH_SIGNUP=false
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=false
OAUTH_MAX_SESSIONS_PER_USER=10
ENABLE_OAUTH_TOKEN_EXCHANGE=false
ENABLE_OAUTH_ID_TOKEN_COOKIE=false

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_OAUTH_SCOPE=openid email profile
GOOGLE_REDIRECT_URI=

# Microsoft OAuth
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_CLIENT_TENANT_ID=

# GitHub OAuth
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Generic OIDC
OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
OAUTH_PROVIDER_NAME=
OAUTH_OPENID_CONFIG_URL=
OAUTH_SCOPES=openid email profile
OAUTH_REDIRECT_URI=

# LDAP
ENABLE_LDAP=false
LDAP_SERVER_HOST=
LDAP_SERVER_PORT=389
LDAP_USE_TLS=true
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
LDAP_SEARCH_BASE=
LDAP_SEARCH_FILTERS=
LDAP_ATTRIBUTE_FOR_MAIL=mail
LDAP_ATTRIBUTE_FOR_USERNAME=uid

# Trusted Headers
WEBUI_AUTH_TRUSTED_EMAIL_HEADER=
WEBUI_AUTH_TRUSTED_NAME_HEADER=
WEBUI_AUTH_TRUSTED_GROUPS_HEADER=

# SCIM
ENABLE_SCIM=false
SCIM_AUTH_TOKEN=
```

---

## База данных

```env
# Подключение (выбери один формат)
DATABASE_URL=sqlite:///data/webui.db          # SQLite (по умолчанию)
DATABASE_URL=postgresql://user:pass@host/db   # PostgreSQL
DATABASE_URL=mysql://user:pass@host/db        # MySQL

# Или по частям
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=openwebui
DATABASE_USER=user
DATABASE_PASSWORD=pass

# Пул соединений
DATABASE_POOL_SIZE=50                    # размер пула (default: зависит от БД)
DATABASE_POOL_MAX_OVERFLOW=20            # доп. соединения сверх пула
DATABASE_POOL_TIMEOUT=30                 # таймаут ожидания соединения (сек)

# SQLite-специфичные
DATABASE_ENABLE_SQLITE_WAL=true          # Write-Ahead Logging (рекомендуется)

# Общие
DATABASE_ENABLE_SESSION_SHARING=false    # переиспользование сессий
```

### Рекомендации

- **Разработка**: SQLite с WAL — просто и достаточно
- **Production < 50 пользователей**: SQLite с WAL, файл на SSD
- **Production 50+ пользователей**: PostgreSQL
- **Высокая нагрузка**: PostgreSQL + connection pooler (PgBouncer)

---

## Redis

```env
# Основное подключение
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=open-webui:            # префикс ключей (для shared Redis)

# Кластер
REDIS_CLUSTER=false

# Sentinel (HA)
REDIS_SENTINEL_HOSTS=host1:26379,host2:26379
REDIS_SENTINEL_PORT=26379
```

Redis используется для:
- Отзыва JWT-токенов (JTI blacklist)
- WebSocket-менеджера (для кластера)
- Кэширования
- Pub/Sub (реалтайм-уведомления)

---

## LLM-провайдеры

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434       # URL Ollama-сервера
OLLAMA_BASE_URLS=url1;url2                   # несколько серверов Ollama

# OpenAI-совместимые API
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_BASE_URLS=url1;url2;url3          # несколько провайдеров
OPENAI_API_KEY=sk-xxx
OPENAI_API_KEYS=key1;key2;key3               # ключи для каждого URL

# Модели по умолчанию
DEFAULT_MODELS=llama3.1                      # модель по умолчанию для новых чатов

# Управление доступом
BYPASS_MODEL_ACCESS_CONTROL=false            # обходить контроль доступа к моделям
ENABLE_FORWARD_USER_INFO_HEADERS=false       # передавать инфо о пользователе в заголовках
```

---

## RAG и эмбеддинги

```env
# Эмбеддинг-модель
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SENTENCE_TRANSFORMERS_BACKEND=torch          # torch | cuda | onnx

# Векторная БД
VECTOR_DB=chroma                             # chroma | milvus | weaviate | qdrant | opensearch | pgvector
CHROMA_DATA_DIR=./data/vector_db
# Или для внешних:
MILVUS_URI=http://localhost:19530
WEAVIATE_URL=http://localhost:8083
QDRANT_URI=http://localhost:6333

# Параметры чанкинга
RAG_CHUNK_SIZE=1500                          # размер чанка (символы)
RAG_CHUNK_OVERLAP=100                        # перекрытие чанков

# Реранкинг
RAG_RERANKING_MODEL=                         # модель реранкинга (опционально)

# Таймауты
RAG_EMBEDDING_TIMEOUT=60                     # таймаут генерации эмбеддингов (сек)
```

---

## WebSocket

```env
ENABLE_WEBSOCKET_SUPPORT=true               # включить WebSocket
WEBSOCKET_MANAGER=                           # пусто = локальный, "redis" = Redis-адаптер
WEBSOCKET_REDIS_URL=redis://localhost:6379/1
WEBSOCKET_REDIS_CLUSTER=false
WEBSOCKET_SERVER_PING_TIMEOUT=20             # таймаут пинга (сек)
WEBSOCKET_SERVER_PING_INTERVAL=25            # интервал пинга (сек)
```

---

## Аудио

```env
# Text-to-Speech
TTS_ENGINE=                                  # openai | elevenlabs | azure
TTS_MODEL=tts-1
TTS_VOICE=alloy
OPENAI_API_KEY=                              # если TTS через OpenAI

# Speech-to-Text
STT_ENGINE=                                  # openai | whisper
WHISPER_MODEL=base                           # tiny | base | small | medium | large
```

---

## Изображения

```env
IMAGE_GENERATION_ENGINE=                     # openai | comfyui | automatic1111
IMAGES_OPENAI_API_BASE_URL=https://api.openai.com/v1
IMAGES_OPENAI_API_KEY=
IMAGE_GENERATION_MODEL=dall-e-3
IMAGE_SIZE=1024x1024
```

---

## Логирование и мониторинг

```env
# Логирование
GLOBAL_LOG_LEVEL=INFO                        # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=                                  # пусто = текст, "json" = JSON

# Аудит
ENABLE_AUDIT_LOGS_FILE=false                 # запись аудит-логов в файл
ENABLE_AUDIT_STDOUT=false                    # вывод аудита в stdout
AUDIT_LOG_LEVEL=METADATA                     # NONE | METADATA | REQUEST | REQUEST_RESPONSE

# OpenTelemetry
ENABLE_OTEL=false                            # включить OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=open-webui
```

---

## Безопасность

```env
# Webhook-подпись
TRUSTED_SIGNATURE_KEY=                       # HMAC-ключ для подписи вебхуков

# Лицензирование (Enterprise)
LICENSE_KEY=
LICENSE_BLOB_PATH=

# CORS
CORS_ALLOW_ORIGIN=*                          # разрешённые origins (production: ограничь!)
```

---

## Прочие настройки

```env
# Общие
PORT=8080                                    # порт сервера
HOST=0.0.0.0                                 # адрес привязки
OFFLINE_MODE=false                           # отключить внешние запросы
DATA_DIR=./data                              # директория данных

# Фичи
ENABLE_EASTER_EGGS=true                      # Easter eggs в UI
ENABLE_VERSION_UPDATE_CHECK=true             # проверка обновлений
ENABLE_REALTIME_CHAT_SAVE=true               # автосохранение чатов
ENABLE_CHAT_RESPONSE_BASE64_IMAGE_URL_CONVERSION=false  # конвертация base64-изображений
```
