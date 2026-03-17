# Архитектура кодовой базы Open Terminal

## Security Posture

Open Terminal даёт легитимный, но высокорисковый набор возможностей: удалённое выполнение команд, PTY over WebSocket, запись файлов, notebooks и локальный reverse proxy. Его нужно воспринимать как чувствительный admin-plane сервис.

- Разворачивай в изолированном контейнере или на отдельном хосте.
- Держи доступ за строгой аутентификацией и сетевым периметром.
- Пинь Docker image по digest или release tag, а не на плавающий `latest`.
- Проверяй `verify_api_key`, entrypoint и правила сетевого доступа перед публичным использованием.

## Структура проекта

```
open-terminal/
├── open_terminal/               # Python-пакет
│   ├── __init__.py              # Docstring
│   ├── __main__.py              # Entry: вызывает cli.main()
│   ├── cli.py                   # Click CLI: команды run и mcp
│   ├── config.py                # Загрузка и мерж TOML-конфигов
│   ├── env.py                   # Все переменные окружения → модульные константы
│   ├── main.py                  # FastAPI app, ВСЕ эндпоинты (~1500 строк)
│   ├── runner.py                # Абстракция запуска процессов (PTY/WinPTY/Pipes)
│   ├── mcp_server.py            # MCP: FastMCP.from_fastapi(app)
│   ├── notebooks.py             # Jupyter notebook сессии (APIRouter)
│   └── utils/
│       ├── __init__.py
│       └── port.py              # Детекция портов и процесс-tree утилиты
├── Dockerfile                   # Python 3.12 + Node.js 22 + инструменты
├── entrypoint.sh                # Docker entrypoint: secrets, packages, permissions
├── dev.sh                       # Dev: uv run uvicorn ... --reload
├── pyproject.toml               # Метаданные, зависимости (hatchling)
├── uv.lock                      # Lock-файл зависимостей
├── CHANGELOG.md                 # Changelog по версиям
└── .github/workflows/
    ├── docker.yml               # Build & push multi-arch Docker image
    └── release.yml              # Автоматическое создание GitHub Release
```

## Ключевые модули

### main.py — ядро приложения

Это монолитный файл (~1500 строк), содержащий:

- **FastAPI app** с CORS middleware
- **Модели Pydantic**: ExecRequest, WriteRequest, ReplaceRequest, ReplacementChunk, MoveRequest, InputRequest, MkdirRequest
- **Аутентификация**: `verify_api_key()` — Bearer-схема через HTTPBearer
- **Middleware**: `normalize_null_query_params` — удаляет query params со значением `"null"`
- **Эндпоинты файлов** (`/files/*`): list, read, write, replace, grep, glob, upload, mkdir, delete, move, display, view, cwd
- **Эндпоинты выполнения** (`/execute`): run, status, input, kill, list
- **Port detection & reverse proxy** (`/ports`, `/proxy/{port}/{path}`)
- **Интерактивные терминалы** (`/api/terminals/*`): создание PTY-сессий, WebSocket, resize

Терминалы регистрируются только если `ENABLE_TERMINAL=true` — весь блок находится внутри `if ENABLE_TERMINAL:`.

Notebook-роутер подключается аналогично: `if ENABLE_NOTEBOOKS:` → `app.include_router(create_notebooks_router(verify_api_key))`.

### runner.py — абстракция запуска процессов

Три реализации `ProcessRunner` (ABC):

| Класс | Платформа | Механизм |
|-------|-----------|----------|
| `PtyRunner` | Unix | `pty.openpty()` + `subprocess.Popen` через slave fd |
| `WinPtyRunner` | Windows | `pywinpty.PtyProcess.spawn()` через ConPTY |
| `PipeRunner` | Любая (fallback) | `asyncio.create_subprocess_shell` с PIPE |

Фабрика `create_runner()` выбирает подходящий вариант:
1. Если доступен `pty` (Unix) → `PtyRunner`
2. Если доступен `winpty` (Windows) → `WinPtyRunner`
3. Иначе → `PipeRunner`

Общий интерфейс: `read_output()`, `write_input()`, `kill()`, `wait()`, `close()`, `pid`.

### config.py — конфигурация

- `load_config(explicit_path)` — загружает и мержит system + user TOML-конфиги
- `init()` — вызывается один раз при старте из CLI, кеширует результат
- `get(key, default)` — lookup из кешированного конфига

### env.py — переменные окружения

Модуль-уровневые константы, вычисляемые при импорте:
`API_KEY`, `CORS_ALLOWED_ORIGINS`, `LOG_DIR`, `BINARY_FILE_MIME_PREFIXES`, `MAX_TERMINAL_SESSIONS`, `ENABLE_TERMINAL`, `TERMINAL_TERM`, `EXECUTE_TIMEOUT`, `EXECUTE_DESCRIPTION`, `ENABLE_NOTEBOOKS`.

Каждая константа проходит цепочку: env var → config.get() → default. Docker secrets поддерживаются через `_resolve_file_env()`.

### notebooks.py — Jupyter-сессии

- `create_notebooks_router(verify_api_key)` — фабрика APIRouter с prefix `/notebooks`
- Сессии хранятся в `_sessions: dict[str, _Session]`
- Каждая сессия: NotebookClient + kernel + notebook object
- Idle cleanup: фоновая задача каждую минуту удаляет сессии старше 30 минут
- При выполнении ячейки ноутбук сохраняется на диск

### utils/port.py — утилиты портов

- `detect_listening_ports()` — кроссплатформенный детектор TCP LISTEN-портов
  - Linux: `/proc/net/tcp` + `/proc/net/tcp6` + inode→PID через `/proc/*/fd/`
  - macOS: `lsof -iTCP -sTCP:LISTEN`
  - Windows: `netstat -ano -p tcp`
- `get_descendant_pids(root_pid)` — дерево дочерних процессов
  - Linux: `/proc/*/stat`
  - Fallback: `ps -eo pid,ppid`

## Разработка

```bash
# Запуск dev-сервера с auto-reload
./dev.sh  # = uv run uvicorn open_terminal.main:app --reload

# Установка зависимостей
uv sync

# Python 3.11 (.python-version)
# Build system: hatchling
```

Тестов в репозитории нет. API-документация автоматически генерируется из FastAPI-описаний (Swagger UI на `/docs`).

## CI/CD

- **docker.yml**: push в main → build linux/amd64 + linux/arm64 → push `ghcr.io/open-webui/open-terminal` с тегами `latest`, `<version>`, `<major.minor>`, `sha-*`
- **release.yml**: изменение `pyproject.toml` в main → извлечение changelog → создание git tag + GitHub Release

Версия читается из `pyproject.toml` → `project.version`.

## Зависимости

**Runtime** (pyproject.toml):
- fastapi, uvicorn[standard] — HTTP-сервер
- click — CLI
- httpx — HTTP-клиент (для upload URL и port proxy)
- python-multipart — загрузка файлов
- aiofiles — асинхронный файловый I/O
- pypdf — извлечение текста из PDF
- nbclient, ipykernel — Jupyter notebook execution
- pywinpty (Windows only) — ConPTY

**Optional**: `fastmcp>=2.0.0` (extra `mcp`)

**Docker image дополнительно включает**:
- Node.js 22 LTS, Docker CLI + Compose + Buildx
- numpy, pandas, scipy, scikit-learn, matplotlib, seaborn, plotly
- jupyter, ipython, requests, beautifulsoup4, sqlalchemy
- openpyxl, weasyprint, python-docx, python-pptx, pypdf, csvkit
- ffmpeg, pandoc, imagemagick, texlive-latex-base
- vim, nano, git, curl, wget, jq, sqlite3, и др.
