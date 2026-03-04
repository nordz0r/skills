# База данных

## Содержание
1. [Технологии](#технологии)
2. [Таблицы и модели](#таблицы-и-модели)
3. [Миграции](#миграции)
4. [Работа с БД напрямую](#работа-с-бд-напрямую)

---

## Технологии

- **ORM**: SQLAlchemy 2.x (async)
- **Миграции**: Alembic (автоматические при старте)
- **Поддерживаемые СУБД**: SQLite, PostgreSQL, MySQL

Ключевые файлы:
- `backend/open_webui/internal/db.py` — подключение, сессии, engine
- `backend/open_webui/models/` — ORM-модели (23+ файлов)
- `backend/open_webui/migrations/` — Alembic-миграции

---

## Таблицы и модели

### Пользователи и аутентификация

**user** — основная таблица пользователей
```
id              UUID, PK
email           VARCHAR, уникальный
username        VARCHAR
name            VARCHAR
role            VARCHAR (admin | user | pending)
profile_image_url  VARCHAR
bio             TEXT
gender          VARCHAR
DOB             DATE
timezone        VARCHAR
presence_state  VARCHAR (online | offline | away)
status_emoji    VARCHAR
status_message  VARCHAR
settings        JSON — пользовательские настройки
oauth           JSON — OAuth-метаданные
scim            JSON — SCIM-метаданные
last_active_at  TIMESTAMP
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**auth** — парольная аутентификация
```
id              UUID, PK (FK → user.id)
email           VARCHAR
password        VARCHAR (bcrypt hash)
active          BOOLEAN
```

**api_key** — API-ключи
```
id              UUID, PK
user_id         UUID, FK → user.id
key             VARCHAR (sk-xxx)
data            JSON (метаданные)
expires_at      TIMESTAMP
last_used_at    TIMESTAMP
created_at      TIMESTAMP
```

**oauth_session** — OAuth-сессии
```
id              UUID, PK
user_id         UUID, FK → user.id
provider        VARCHAR
access_token    TEXT
refresh_token   TEXT
expires_at      TIMESTAMP
created_at      TIMESTAMP
```

### Чаты и сообщения

**chat** — чат-сессии
```
id              UUID, PK
user_id         UUID, FK → user.id
title           VARCHAR
chat_template   JSON
documents       JSON (привязанные документы)
models          JSON (используемые модели)
messages        JSON (legacy — массив сообщений)
pinned          BOOLEAN
archived        BOOLEAN
folder_id       UUID, FK → folder.id
share_id        VARCHAR (для shared-ссылок)
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**chat_message** — отдельные сообщения (новая модель)
```
id              UUID, PK
chat_id         UUID, FK → chat.id
message_id      VARCHAR
user_id         UUID
content         TEXT
role            VARCHAR (user | assistant | system)
files           JSON
citations       JSON
created_at      TIMESTAMP
```

### Контент и знания

**knowledge** — базы знаний
```
id              UUID, PK
user_id         UUID, FK → user.id
name            VARCHAR
description     TEXT
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**knowledge_file** — связь файлов с knowledge base
```
id              UUID, PK
knowledge_id    UUID, FK → knowledge.id
file_id         UUID, FK → file.id
user_id         UUID
```

**file** — загруженные файлы
```
id              UUID, PK
user_id         UUID, FK → user.id
filename        VARCHAR
data            JSON (путь к файлу, размер, MIME-тип)
meta            JSON (дополнительные метаданные)
created_at      TIMESTAMP
```

**prompt** — сохранённые промпты
```
id              UUID, PK (= command)
user_id         UUID, FK → user.id
command         VARCHAR (уникальный)
title           VARCHAR
content         TEXT
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**note** — заметки
```
id              UUID, PK
user_id         UUID, FK → user.id
title           VARCHAR
content         TEXT
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**memory** — пользовательские воспоминания
```
id              UUID, PK
user_id         UUID, FK → user.id
content         TEXT
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Функции и инструменты

**function** — пользовательские функции
```
id              VARCHAR, PK (lowercase + underscore)
user_id         UUID, FK → user.id
name            VARCHAR
type            VARCHAR (filter | pipe | action)
content         TEXT (Python-код)
meta            JSON (описание, manifest)
valves          JSON (admin-настройки)
is_active       BOOLEAN
is_global       BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**tool** — инструменты для function calling
```
id              VARCHAR, PK
user_id         UUID, FK → user.id
name            VARCHAR
content         TEXT (Python-код)
specs           JSON (OpenAPI-спецификация)
meta            JSON
valves          JSON
is_active       BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Модели

**model** — определения моделей
```
id              VARCHAR, PK (model ID)
user_id         UUID, FK → user.id
base_model_id   VARCHAR (ID базовой модели)
name            VARCHAR
params          JSON (temperature, top_p, и т.д.)
meta            JSON (описание, capabilities)
access_control  JSON (кому доступна)
is_active       BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Организация и доступ

**folder** — папки
```
id              UUID, PK
user_id         UUID, FK → user.id
name            VARCHAR
parent_id       UUID, FK → folder.id (вложенность)
is_expanded     BOOLEAN
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**group** — группы пользователей
```
id              UUID, PK
name            VARCHAR
description     TEXT
permissions     JSON
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**access_grant** — гранулярные права доступа
```
id              UUID, PK
resource_type   VARCHAR (knowledge | model | chat | ...)
resource_id     UUID
target_type     VARCHAR (user | group)
target_id       UUID
access_level    VARCHAR (read | write | admin)
created_at      TIMESTAMP
```

**tag** — теги
```
id              UUID, PK
user_id         UUID
name            VARCHAR
data            JSON
meta            JSON
```

### Коллаборация

**channel** — каналы
```
id              UUID, PK
name            VARCHAR
description     TEXT
access_control  JSON
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**message** — сообщения в каналах
```
id              UUID, PK
channel_id      UUID, FK → channel.id
user_id         UUID, FK → user.id
content         TEXT
data            JSON
meta            JSON
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### Аналитика

**feedback** — обратная связь по ответам
```
id              UUID, PK
user_id         UUID
type            VARCHAR (thumbs_up | thumbs_down)
data            JSON
meta            JSON
created_at      TIMESTAMP
```

---

## Миграции

### Автоматические миграции

Open WebUI запускает Alembic-миграции автоматически при каждом старте. Файлы миграций находятся в `backend/open_webui/migrations/versions/`.

### Создание миграции (для разработчиков)

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Откат миграции

```bash
cd backend
alembic downgrade -1    # откатить последнюю
alembic downgrade <rev> # откатить до конкретной ревизии
```

---

## Работа с БД напрямую

### SQLite

```bash
sqlite3 data/webui.db
.tables          # список таблиц
.schema user     # структура таблицы
SELECT * FROM user LIMIT 5;
```

### PostgreSQL

```bash
psql -U owui openwebui
\dt              # список таблиц
\d user          # структура таблицы
SELECT id, email, role FROM "user" LIMIT 5;
```

Обрати внимание: в PostgreSQL `user` — зарезервированное слово, нужны кавычки `"user"`.
