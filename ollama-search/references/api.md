# Ollama Web API — полная справка

## Содержание

- [Аутентификация](#аутентификация)
- [Web Search](#web-search)
- [Web Fetch](#web-fetch)
- [Коды ошибок](#коды-ошибок)
- [Лимиты и ограничения](#лимиты-и-ограничения)

---

## Аутентификация

Все запросы требуют Bearer-токен:

```
Authorization: Bearer $OLLAMA_API_KEY
```

Ключ создаётся на `https://ollama.com/settings/keys`. Один аккаунт может иметь несколько ключей.

---

## Web Search

**Эндпоинт:** `POST https://ollama.com/api/web_search`

### Параметры запроса

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|----------|-----|-------------|-------------|----------|
| `query` | string | да | — | Поисковый запрос |
| `max_results` | integer | нет | 5 | Количество результатов (1–10) |

### Пример запроса

```bash
curl -s https://ollama.com/api/web_search \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "ollama web search", "max_results": 3}'
```

### Формат ответа

```json
{
  "results": [
    {
      "title": "Заголовок страницы",
      "url": "https://example.com/page",
      "content": "Сниппет — краткий фрагмент текста со страницы, релевантный запросу"
    }
  ]
}
```

### Поля результата

| Поле | Тип | Описание |
|------|-----|----------|
| `title` | string | Заголовок страницы |
| `url` | string | URL страницы |
| `content` | string | Сниппет — краткое содержание, релевантное запросу |

Если результатов нет, `results` — пустой массив `[]`.

---

## Web Fetch

**Эндпоинт:** `POST https://ollama.com/api/web_fetch`

### Параметры запроса

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `url` | string | да | URL страницы для извлечения контента |

### Пример запроса

```bash
curl -s https://ollama.com/api/web_fetch \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.ollama.com/capabilities/web-search"}'
```

### Формат ответа

```json
{
  "title": "Web Search - Ollama",
  "content": "Полный текстовый контент страницы, извлечённый из HTML...",
  "links": [
    "https://ollama.com/settings/keys",
    "https://github.com/ollama/ollama-python",
    "https://github.com/ollama/ollama-js"
  ]
}
```

### Поля ответа

| Поле | Тип | Описание |
|------|-----|----------|
| `title` | string | Заголовок страницы (`<title>`) |
| `content` | string | Основной текстовый контент, извлечённый из HTML |
| `links` | string[] | Массив URL-ссылок, найденных на странице |

Контент может быть большим (1000+ токенов). Для агентов рекомендуется контекстное окно минимум 32 000 токенов.

---

## Коды ошибок

| HTTP-код | Причина | Что делать |
|----------|---------|-----------|
| 401 | Неверный или отсутствующий API-ключ | Проверь `OLLAMA_API_KEY`, создай новый ключ |
| 400 | Невалидные параметры | Проверь JSON-тело запроса, `query` не пустой, `max_results` 1–10 |
| 429 | Rate limit | Подожди и повтори, уменьши частоту запросов |
| 500 | Ошибка сервера | Повтори через несколько секунд |

### Пример обработки ошибок в bash

```bash
response=$(curl -s -w "\n%{http_code}" https://ollama.com/api/web_search \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}')

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

case "$http_code" in
  200) echo "$body" | jq . ;;
  401) echo "Ошибка авторизации: проверь OLLAMA_API_KEY" >&2; exit 1 ;;
  429) echo "Слишком много запросов, подождите" >&2; exit 1 ;;
  *)   echo "Ошибка $http_code: $body" >&2; exit 1 ;;
esac
```

---

## Лимиты и ограничения

- `max_results`: от 1 до 10
- Контент из `web_fetch` может быть очень длинным — учитывай при формировании промпта
- API работает через облако Ollama — нужен интернет
- Скорость зависит от загрузки серверов Ollama
- Нет batch-эндпоинта — каждый запрос отдельный
