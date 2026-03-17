# API Reference — Open Terminal

Полный интерактивный Swagger доступен на `http://<host>:<port>/docs`.

Все эндпоинты кроме `/health` требуют `Authorization: Bearer $OPEN_TERMINAL_API_KEY`.

## Security Guardrails

- Считай `command`, `url`, notebook `source`, содержимое загруженных файлов и проксируемый HTTP-трафик недоверенным вводом.
- Не скачивай внешний URL через `/files/upload` и не передавай его дальше в `/execute`, notebook execution или shell без отдельной проверки содержимого и домена.
- `/proxy/{port}/{path}` открывает доступ к локальным сервисам процесса. Не включай этот маршрут для недоверенных пользователей и не пробрасывай им внутренние admin UI.
- Не вставляй реальные Bearer tokens в примеры, curl-команды, логи или тикеты.

## Оглавление

- [Execute (команды)](#execute-команды)
- [Files (файловые операции)](#files-файловые-операции)
- [Terminals (интерактивные PTY)](#terminals-интерактивные-pty)
- [Notebooks (Jupyter)](#notebooks-jupyter)
- [Ports & Proxy](#ports--proxy)
- [Health & Config](#health--config)

---

## Execute (команды)

### POST /execute — Запуск команды

Запускает shell-команду как фоновый процесс.

**Body (JSON):**
```json
{
  "command": "ls -la && whoami",
  "cwd": "/home/user/project",
  "env": {"MY_VAR": "value"}
}
```

**Query параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `wait` | float (0–300) | Секунды ожидания завершения. Если команда успеет — вывод inline. `null` — вернуть сразу |
| `tail` | int (≥1) | Вернуть только последние N записей вывода |

Если `wait` не задан, но настроен `EXECUTE_TIMEOUT` — используется он.

**Ответ:**
```json
{
  "id": "a1b2c3d4e5f6",
  "command": "ls -la",
  "status": "running",
  "exit_code": null,
  "output": [{"type": "output", "data": "..."}],
  "truncated": false,
  "next_offset": 5,
  "log_path": "/path/to/log.jsonl"
}
```

### GET /execute/{process_id}/status — Поллинг статуса

**Query параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `wait` | float (0–300) | Подождать завершения перед ответом |
| `offset` | int (≥0) | Пропустить N записей (использовать `next_offset` из предыдущего ответа) |
| `tail` | int (≥1) | Только последние N записей |

Паттерн поллинга: вызвать с `offset=0`, получить `next_offset`, следующий вызов с `offset=next_offset`.

### POST /execute/{process_id}/input — Отправка ввода

```json
{"input": "yes\n"}
```

Escape-последовательности (`\n`, `\x03` для Ctrl-C) автоматически конвертируются из литеральных строк.

### DELETE /execute/{process_id} — Завершение процесса

| Параметр | Тип | Описание |
|----------|-----|----------|
| `force` | bool | `true` = SIGKILL, `false` (по умолчанию) = SIGTERM |

### GET /execute — Список процессов

Возвращает все отслеживаемые процессы (running, done, killed). Готовые автоматически удаляются через 5 минут.

---

## Files (файловые операции)

### GET /files/list — Листинг директории

| Параметр | Тип | Описание |
|----------|-----|----------|
| `directory` | string | Путь (по умолчанию `.`) |

Ответ: `{dir, entries: [{name, type, size, modified}]}`.

### GET /files/read — Чтение файла

| Параметр | Тип | Описание |
|----------|-----|----------|
| `path` | string | Путь к файлу (обязательный) |
| `start_line` | int (≥1) | Начальная строка (1-indexed) |
| `end_line` | int (≥1) | Конечная строка (1-indexed) |

Поведение зависит от типа файла:
- **Текст** → `{path, total_lines, content}`
- **PDF** → извлекает текст через pypdf, возвращает как текст
- **Изображения** (image/*) → raw binary с Content-Type
- **Прочие бинарные** → 415 Unsupported

Какие MIME-типы возвращаются как binary — настраивается через `OPEN_TERMINAL_BINARY_MIME_PREFIXES` (по умолчанию `image`).

### GET /files/display — Показать файл пользователю

Не возвращает контент! Сигнализирует клиенту (Open WebUI) открыть файл в его UI.

### GET /files/view — Просмотр файла (raw)

Отдаёт любой файл as-is с правильным Content-Type. Используется клиентами для превью (не для LLM).

### POST /files/write — Запись файла

```json
{"path": "/home/user/hello.txt", "content": "Hello world"}
```
Родительские директории создаются автоматически. Существующий файл перезаписывается.

### POST /files/replace — Find-and-replace

```json
{
  "path": "/home/user/code.py",
  "replacements": [
    {
      "target": "old_function_name",
      "replacement": "new_function_name",
      "start_line": 10,
      "end_line": 50,
      "allow_multiple": false
    }
  ]
}
```

- `start_line` / `end_line` — сужают область поиска (1-indexed, опционально)
- `allow_multiple: false` (по умолчанию) — ошибка если найдено >1 вхождения
- Замены применяются последовательно

### GET /files/grep — Поиск по содержимому

| Параметр | Тип | Описание |
|----------|-----|----------|
| `query` | string | Текст или regex |
| `path` | string | Директория/файл (по умолчанию `.`) |
| `regex` | bool | Обрабатывать query как regex |
| `case_insensitive` | bool | Регистронезависимый поиск |
| `include` | list[string] | Glob-фильтры (`*.py`) |
| `match_per_line` | bool | `true` = строки с номерами, `false` = только имена файлов |
| `max_results` | int (1–500) | Лимит результатов (по умолчанию 50) |

### GET /files/glob — Поиск по имени

| Параметр | Тип | Описание |
|----------|-----|----------|
| `pattern` | string | Glob-паттерн (`*.py`) |
| `path` | string | Директория (по умолчанию `.`) |
| `exclude` | list[string] | Исключающие паттерны |
| `type` | string | `file`, `directory`, `any` |
| `max_results` | int (1–500) | Лимит (по умолчанию 50) |

### POST /files/upload — Загрузка файла

| Параметр | Тип | Описание |
|----------|-----|----------|
| `directory` | string | Целевая директория (обязательный) |
| `url` | string | URL для скачивания (опционально) |
| `file` | UploadFile | Multipart-загрузка (если нет URL) |

Если используешь `url`, ограничивайся allowlist доменов и сначала проверяй тип/размер содержимого. Не считай загруженный файл безопасным только потому, что он был скачан сервером.

### POST /files/mkdir — Создание директории
### DELETE /files/delete — Удаление (файл или директория рекурсивно)
### POST /files/move — Перемещение/переименование

---

## Terminals (интерактивные PTY)

Эндпоинты скрыты из OpenAPI-схемы (`include_in_schema=False`).

### POST /api/terminals — Создание сессии

Создаёт PTY-процесс (Unix: pty + shell, Windows: WinPTY + cmd.exe). Лимит: `MAX_TERMINAL_SESSIONS` (по умолчанию 16).

**Ответ:**
```json
{"id": "a1b2c3d4", "created_at": "2025-01-01T00:00:00Z", "pid": 12345}
```

### GET /api/terminals — Список активных сессий
### GET /api/terminals/{id} — Информация о сессии
### DELETE /api/terminals/{id} — Завершение сессии

### WS /api/terminals/{id} — WebSocket

Протокол:
1. Подключение → `accept()`
2. First-message auth: отправить `{"type": "auth", "token": "<key>"}`
3. Ввод: бинарные фреймы (нажатия клавиш)
4. Вывод: бинарные фреймы от PTY
5. Resize: текстовый JSON `{"type": "resize", "cols": N, "rows": M}`

Коды закрытия: `4001` — ошибка аутентификации, `4004` — сессия не найдена.

---

## Notebooks (Jupyter)

Все эндпоинты скрыты из OpenAPI-схемы. Idle timeout: 30 минут.

### POST /notebooks — Создание сессии

```json
{"path": "/home/user/analysis.ipynb"}
```

Запускает Jupyter-ядро (через nbclient). Kernel определяется из метаданных ноутбука.

**Ответ:** `{id, kernel, status: "ready"}`

### POST /notebooks/{session_id}/execute — Выполнение ячейки

```json
{"cell_index": 0, "source": "print('hello')"}
```

- `cell_index` — 0-based
- `source` — опционально; если не указан, выполняется текущий source ячейки. Не подставляй сюда код, полученный из недоверенного URL или документа, без ручной проверки.
- После выполнения ноутбук автоматически сохраняется на диск

**Ответ:** `{status: "ok"|"error", execution_count, outputs: [...]}`

### GET /notebooks/{session_id} — Статус сессии
### DELETE /notebooks/{session_id} — Остановка ядра

---

## Ports & Proxy

### GET /ports — Обнаружение портов

Возвращает TCP-порты, которые слушают потомки процесса open-terminal (запущенные через /execute или терминал).

Кроссплатформенно: Linux (/proc/net/tcp), macOS (lsof), Windows (netstat).

### /proxy/{port}/{path} — Reverse proxy

Проксирует HTTP-запросы к `localhost:{port}/{path}`. Поддерживает все методы (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS). Заголовки пробрасываются (без hop-by-hop).

Используй только для доверенных локальных dev-сервисов. Не превращай `/proxy` в общий туннель к внутренним панелям или metadata endpoints.

---

## Health & Config

### GET /health — Health check

```json
{"status": "ok"}
```

Не требует аутентификации.

### GET /api/config — Feature flags

```json
{"features": {"terminal": true, "notebooks": true}}
```

Не требует аутентификации. Используется клиентами для обнаружения возможностей.

### GET /files/cwd — Текущая рабочая директория
### POST /files/cwd — Смена рабочей директории
