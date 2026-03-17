# Конфигурация Open Terminal

## Приоритет настроек

1. **CLI-флаги** — `--host`, `--port`, `--api-key`, `--cors-allowed-origins`, `--config`, `--cwd`
2. **Переменные окружения** — `OPEN_TERMINAL_*`
3. **User config** — `$XDG_CONFIG_HOME/open-terminal/config.toml` (по умолчанию `~/.config/open-terminal/config.toml`)
4. **System config** — `/etc/open-terminal/config.toml`
5. **Встроенные значения по умолчанию**

## Переменные окружения

| Переменная | TOML-ключ | Умолчание | Описание |
|-----------|-----------|-----------|----------|
| `OPEN_TERMINAL_API_KEY` | `api_key` | *(автогенерация)* | Bearer-токен для аутентификации |
| `OPEN_TERMINAL_CORS_ALLOWED_ORIGINS` | `cors_allowed_origins` | `*` | Разрешённые CORS-origins (через запятую) |
| `OPEN_TERMINAL_LOG_DIR` | `log_dir` | `~/.local/state/open-terminal/logs` | Директория для JSONL-логов процессов |
| `OPEN_TERMINAL_BINARY_MIME_PREFIXES` | `binary_mime_prefixes` | `image` | MIME-префиксы для бинарных файлов в /files/read (через запятую) |
| `OPEN_TERMINAL_MAX_SESSIONS` | `max_terminal_sessions` | `16` | Максимум одновременных PTY-сессий |
| `OPEN_TERMINAL_ENABLE_TERMINAL` | `enable_terminal` | `true` | Включить интерактивные терминалы |
| `OPEN_TERMINAL_TERM` | `term` | `xterm-256color` | Значение $TERM для PTY-сессий |
| `OPEN_TERMINAL_EXECUTE_TIMEOUT` | `execute_timeout` | *(не задан)* | Таймаут по умолчанию для `wait` в /execute (секунды) |
| `OPEN_TERMINAL_EXECUTE_DESCRIPTION` | `execute_description` | *(пусто)* | Дополнительный текст для описания /execute в OpenAPI |
| `OPEN_TERMINAL_ENABLE_NOTEBOOKS` | `enable_notebooks` | `true` | Включить Jupyter notebook сессии |

### Docker-only переменные

| Переменная | Описание |
|-----------|----------|
| `OPEN_TERMINAL_PACKAGES` | Пробелоразделённый список apt-пакетов для установки при старте контейнера |
| `OPEN_TERMINAL_PIP_PACKAGES` | Пробелоразделённый список pip-пакетов для установки при старте |

Эти переменные обрабатываются в `entrypoint.sh`, а не в Python-коде.

## Docker secrets (конвенция `_FILE`)

Для безопасной передачи секретов Open Terminal поддерживает суффикс `_FILE`:

```yaml
# docker-compose.yml
services:
  terminal:
    image: ghcr.io/open-webui/open-terminal@sha256:<verified-digest>
    secrets:
      - api_key
    environment:
      OPEN_TERMINAL_API_KEY_FILE: /run/secrets/api_key

secrets:
  api_key:
    file: ./api_key.txt
```

Реализовано в двух местах:
- `entrypoint.sh` — функция `file_env` для shell-уровня
- `open_terminal/env.py` — функция `_resolve_file_env()` для Python-уровня

Нельзя задать одновременно `VAR` и `VAR_FILE` — это ошибка.

## Пример TOML-конфига

```toml
host = "127.0.0.1"
port = 8000
api_key = "<read-from-secret-store>"
cors_allowed_origins = "*"
log_dir = "/var/log/open-terminal"
binary_mime_prefixes = "image,audio"
execute_timeout = 5
max_terminal_sessions = 32
enable_terminal = true
enable_notebooks = true
term = "xterm-256color"
```

## CLI-команды

### `open-terminal run`

Запуск REST API сервера (uvicorn).

```bash
open-terminal run [OPTIONS]
  --host TEXT          Bind host (по умолчанию 0.0.0.0)
  --port INT           Bind port (по умолчанию 8000)
  --config PATH        Путь к TOML-конфигу
  --cwd PATH           Рабочая директория
  --api-key TEXT       Bearer API key
  --cors-allowed-origins TEXT  CORS origins через запятую
```

### `open-terminal mcp`

Запуск MCP-сервера (требует `pip install open-terminal[mcp]`).

```bash
open-terminal mcp [OPTIONS]
  --transport [stdio|streamable-http]  Транспорт (по умолчанию stdio)
  --host TEXT          Bind host (только для streamable-http)
  --port INT           Bind port (только для streamable-http)
  --config PATH        Путь к TOML-конфигу
  --cwd PATH           Рабочая директория
```
