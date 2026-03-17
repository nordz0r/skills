---
name: open-terminal-guide
description: >-
  Полная русскоязычная справка по Open Terminal: self-hosted REST API
  терминала для AI-агентов. Используй этот скилл при любых вопросах об Open
  Terminal: API-эндпоинты, развёртывание (Docker, bare-metal), конфигурация,
  интеграция с Open WebUI, архитектура, отладка, написание клиентского кода
  для взаимодействия с Open Terminal. Также используй при работе с кодовой
  базой open-terminal: структура проекта, runner.py, main.py, MCP-сервер,
  Jupyter-ноутбуки. Триггеры: open-terminal, open terminal, remote terminal
  API, /execute, /files, sandbox API, terminal sessions, Open WebUI terminal.
---

# Open Terminal — Полная справка

Open Terminal — это легковесный self-hosted REST API, который предоставляет AI-агентам и инструментам автоматизации выделенную среду для выполнения команд, управления файлами и запуска кода. Является частью экосистемы [Open WebUI](https://github.com/open-webui/open-webui).

## Два режима работы

| Режим | Описание | Безопасность |
|-------|----------|-------------|
| **Docker** | Изолированный контейнер с предустановленными Python, Node.js, git, ffmpeg, LaTeX, data science библиотеками и др. | Песочница, безопасно для AI-агентов |
| **Bare metal** | `pip install open-terminal` и запуск напрямую на машине | Команды выполняются с правами пользователя — без изоляции |

## Быстрый старт

```bash
# Задай ключ заранее через secret manager или env-file
export OPEN_TERMINAL_API_KEY='<random-secret-from-secret-store>'
export OPEN_TERMINAL_IMAGE='ghcr.io/open-webui/open-terminal@sha256:<verified-digest>'

# Docker (рекомендуется)
docker pull "$OPEN_TERMINAL_IMAGE"
docker run -d --name open-terminal --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -v open-terminal:/home/user \
  -e OPEN_TERMINAL_API_KEY="$OPEN_TERMINAL_API_KEY" \
  "$OPEN_TERMINAL_IMAGE"

# Bare metal через uvx (без установки)
uvx open-terminal run --host 127.0.0.1 --port 8000 --api-key "$OPEN_TERMINAL_API_KEY"

# Bare metal через pip
pip install open-terminal
open-terminal run --host 127.0.0.1 --port 8000 --api-key "$OPEN_TERMINAL_API_KEY"
```

Автогенерация API-ключа в логах годится только для локального одноразового теста. Для постоянного окружения задай ключ явно через env var или `_FILE` secret.

## Аутентификация

Все эндпоинты кроме `/health` требуют Bearer-токен:

```
Authorization: Bearer $OPEN_TERMINAL_API_KEY
```

WebSocket-терминалы используют **first-message auth** — первое сообщение после подключения должно быть JSON:
```json
{"type": "auth", "token": "$OPEN_TERMINAL_API_KEY"}
```

## Security Guardrails

- Разворачивай Open Terminal только за VPN, reverse proxy или allowlist ACL. Не публикуй его напрямую в интернет без отдельного изоляционного контура.
- Для production предпочитай Docker/VM/отдельного пользователя без привилегий. Bare metal допустим только в доверенной среде.
- `/files/upload` с полем `url`, notebook `source` и `/proxy/{port}/{path}` используй только для доверенных источников. Не скачивай URL и не выполняй полученный контент без ручной проверки.
- Если не нужны PTY, notebooks или proxy, отключай их конфигом/доступом на периметре.
- Не вставляй реальные ключи в команды, логи, issue-трекер, примеры JSON и сообщения агенту.

## Основные группы API

| Группа | Назначение |
|--------|-----------|
| `POST /execute` | Запуск команд как фоновых процессов |
| `GET /execute/{id}/status` | Поллинг вывода и статуса |
| `POST /execute/{id}/input` | Отправка stdin в процесс |
| `DELETE /execute/{id}` | Завершение (kill) процесса |
| `GET /files/list` | Листинг директории |
| `GET /files/read` | Чтение файла (текст/PDF/бинарные) |
| `POST /files/write` | Запись файла |
| `POST /files/replace` | Find-and-replace в файле |
| `GET /files/grep` | Поиск по содержимому файлов |
| `GET /files/glob` | Поиск файлов по имени (glob-паттерны) |
| `GET /files/display` | Открытие файла в UI пользователя |
| `POST /files/upload` | Загрузка файла (multipart или URL) |
| `POST /api/terminals` | Создание интерактивной PTY-сессии |
| `WS /api/terminals/{id}` | WebSocket для терминала |
| `GET /ports` | Детекция слушающих TCP-портов |
| `/proxy/{port}/{path}` | Reverse-proxy к localhost:{port} |
| `GET /health` | Health check (без аутентификации) |

Подробная информация по каждому эндпоинту — в `references/api.md`.

## Модель выполнения команд

Команды запускаются через `POST /execute` как **фоновые процессы**:

1. Команда спавнится в PTY (Unix) / WinPTY (Windows) / пайпы (fallback)
2. Получает UUID-идентификатор, вывод пишется в JSONL-лог в `LOG_DIR`
3. Статус: `running` → `done` (или `killed`)
4. Вывод читается через поллинг `GET /execute/{id}/status` с `offset` и `tail`
5. Готовые процессы автоматически удаляются через 5 минут после завершения

Параметр `wait` (0–300 сек.) позволяет дождаться завершения команды inline — удобно для коротких команд.

## Интерактивные терминалы

PTY-сессии управляются через REST + WebSocket:

1. `POST /api/terminals` — создать сессию (лимит: `MAX_TERMINAL_SESSIONS`, по умолчанию 16)
2. `WS /api/terminals/{id}` — подключиться (first-message auth → бинарные фреймы ввода/вывода)
3. Resize: текстовый JSON-фрейм `{"type": "resize", "cols": 120, "rows": 40}`
4. Мёртвые сессии автоматически очищаются при листинге

## Конфигурация

Приоритет (от высшего к низшему):
1. CLI-флаги (`--host`, `--port`, `--api-key`)
2. Переменные окружения (`OPEN_TERMINAL_*`)
3. User config: `~/.config/open-terminal/config.toml`
4. System config: `/etc/open-terminal/config.toml`
5. Встроенные значения по умолчанию

Подробная таблица всех переменных окружения и параметров — в `references/configuration.md`.

### Docker-специфичные переменные

| Переменная | Описание |
|-----------|----------|
| `OPEN_TERMINAL_PACKAGES` | Пробелоразделённый список apt-пакетов для установки при старте |
| `OPEN_TERMINAL_PIP_PACKAGES` | Пробелоразделённый список pip-пакетов для установки при старте |

Обрабатываются в `entrypoint.sh` при каждом запуске контейнера.

### Docker secrets

Поддерживается конвенция `_FILE` (как у PostgreSQL):
- `OPEN_TERMINAL_API_KEY_FILE=/run/secrets/api_key` — значение читается из файла
- Нельзя задавать одновременно `VAR` и `VAR_FILE`

### Docker socket

Для доступа к Docker CLI из контейнера (сборка образов, запуск контейнеров):
```bash
docker run -d -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v open-terminal:/home/user \
  "$OPEN_TERMINAL_IMAGE"
```
`entrypoint.sh` автоматически добавляет пользователя в группу сокета.

## Интеграция с Open WebUI

Open Terminal интегрируется с Open WebUI двумя способами:

### Direct Connection (из браузера)
Пользователь подключает свой инстанс через **User Settings → Integrations → Open Terminal**. Запросы идут напрямую из браузера.

### System-Level (через бэкенд)
Админ настраивает через **Admin Settings → Integrations → Open Terminal**. Запросы проксируются через бэкенд Open WebUI. Можно настроить несколько терминалов с контролем доступа по пользователям/группам.

В обоих случаях подключение добавляется в секции **Open Terminal** (не как tool server) — это даёт файловый сайдбар для навигации, загрузки и редактирования файлов.

## Архитектура кодовой базы

Для работы с исходным кодом open-terminal — см. `references/architecture.md`.

## MCP-сервер

Open Terminal может работать как MCP (Model Context Protocol) сервер:

```bash
# Требует установки: pip install open-terminal[mcp]
open-terminal mcp --transport stdio
open-terminal mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

Все FastAPI-эндпоинты автоматически экспонируются как MCP-инструменты через `FastMCP.from_fastapi()`.

## Jupyter Notebooks

Скрытые эндпоинты (не в OpenAPI-схеме) для per-cell выполнения ноутбуков:

1. `POST /notebooks` — создать сессию (привязка к `.ipynb` файлу, запуск ядра)
2. `POST /notebooks/{session_id}/execute` — выполнить ячейку (по индексу, с возможностью override source)
3. `GET /notebooks/{session_id}` — статус сессии
4. `DELETE /notebooks/{session_id}` — остановить ядро

Сессии автоматически удаляются после 30 минут простоя. Ноутбук сохраняется на диск после каждого выполнения.
