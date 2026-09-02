# Ollama MCP-сервер

## Содержание

- [Что такое MCP](#что-такое-mcp)
- [Установка](#установка)
- [Настройка для разных клиентов](#настройка-для-разных-клиентов)
- [Доступные инструменты](#доступные-инструменты)

---

## Что такое MCP

MCP (Model Context Protocol) — стандарт для подключения внешних инструментов к LLM-агентам. Ollama предоставляет Python MCP-сервер, который даёт агентам доступ к `web_search` и `web_fetch` через единый протокол.

Это позволяет использовать поиск Ollama в любом MCP-совместимом клиенте без написания кода.

---

## Установка

MCP-сервер Ollama распространяется как Python-пакет:

```bash
pip install ollama-mcp
```

Или через uvx (без установки):

```bash
uvx ollama-mcp
```

Требуется переменная окружения:

```bash
export OLLAMA_SEARCH_API_KEY="your-key-here"
```

---

## Настройка для разных клиентов

### Cline (VS Code)

1. Открой VS Code → Cline → **Manage MCP Servers**
2. Добавь конфигурацию:

```json
{
  "mcpServers": {
    "ollama": {
      "command": "uvx",
      "args": ["ollama-mcp"],
      "env": {
        "OLLAMA_SEARCH_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Codex (CLI)

Добавь в `~/.codex/config.toml`:

```toml
[mcp_servers.ollama]
command = "uvx"
args = ["ollama-mcp"]

[mcp_servers.ollama.env]
OLLAMA_SEARCH_API_KEY = "your-key-here"
```

### Goose

Настройка через интерфейс MCP в Goose:

```json
{
  "name": "ollama",
  "command": "uvx",
  "args": ["ollama-mcp"],
  "env": {
    "OLLAMA_SEARCH_API_KEY": "your-key-here"
  }
}
```

### Claude Code

Добавь в `.claude/settings.json` или через `claude mcp add`:

```bash
claude mcp add ollama -- uvx ollama-mcp
```

Или вручную в `.claude/settings.json`:

```json
{
  "mcpServers": {
    "ollama": {
      "command": "uvx",
      "args": ["ollama-mcp"],
      "env": {
        "OLLAMA_SEARCH_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Общий паттерн (любой MCP-клиент)

Любой клиент, поддерживающий MCP, может подключить Ollama Search. Нужны три вещи:

1. **Команда запуска:** `uvx ollama-mcp` (или `python -m ollama_mcp`)
2. **Переменная окружения:** `OLLAMA_SEARCH_API_KEY`
3. **Транспорт:** stdio (по умолчанию)

---

## Доступные инструменты

MCP-сервер предоставляет два инструмента:

### web_search

Поиск по интернету. Параметры:

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `query` | string | да | Поисковый запрос |
| `max_results` | integer | нет | Количество результатов (1–10) |

### web_fetch

Получение контента страницы. Параметры:

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `url` | string | да | URL страницы |

Оба инструмента возвращают те же структуры, что и REST API (см. `references/api.md`).
