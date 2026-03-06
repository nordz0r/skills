# Конфигурация в OpenClaw

## Содержание

- [Включение скилла](#включение-скилла)
- [Переменные окружения](#переменные-окружения)
- [Проверка работоспособности](#проверка-работоспособности)
- [Диагностика проблем](#диагностика-проблем)

---

## Включение скилла

### Установка скилла

Скилл должен находиться в одном из каталогов:
- `~/.openclaw/workspace/skills/ollama-search/` — workspace-уровень
- Или в репозитории `skills/ollama-search/` — при сборке Docker-образа

### Конфигурация в openclaw.json

Добавь секцию скилла в `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "ollama_search": {
        "enabled": true,
        "env": {
          "OLLAMA_API_KEY": "your-ollama-api-key",
          "OLLAMA_WEB_SEARCH_URL": "https://ollama.com/api/web_search",
          "OLLAMA_WEB_FETCH_URL": "https://ollama.com/api/web_fetch"
        }
      }
    }
  }
}
```

### Безопасное редактирование конфига

```bash
# Бэкап
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Редактирование через jq
jq '.skills.entries.ollama_search = {
  "enabled": true,
  "env": {
    "OLLAMA_API_KEY": "your-key",
    "OLLAMA_WEB_SEARCH_URL": "https://ollama.com/api/web_search",
    "OLLAMA_WEB_FETCH_URL": "https://ollama.com/api/web_fetch"
  }
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json \
  && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# Рестарт gateway для применения
docker compose restart openclaw-gateway
```

---

## Переменные окружения

| Переменная | Обязательная | По умолчанию | Описание |
|-----------|-------------|-------------|----------|
| `OLLAMA_API_KEY` | да | — | API-ключ с ollama.com/settings/keys |
| `OLLAMA_WEB_SEARCH_URL` | нет | `https://ollama.com/api/web_search` | URL эндпоинта поиска |
| `OLLAMA_WEB_FETCH_URL` | нет | `https://ollama.com/api/web_fetch` | URL эндпоинта получения контента |

Переменные задаются через:
1. **openclaw.json** → `.skills.entries.ollama_search.env` (рекомендуется)
2. **docker-compose.yml** → секция `environment`
3. **Системные переменные** окружения хоста

---

## Проверка работоспособности

### Шаг 1: проверь, что скилл виден

```bash
docker compose run --rm openclaw-cli skills list --eligible
```

В списке должен быть `ollama_search`.

### Шаг 2: проверь API-ключ

```bash
curl -s -o /dev/null -w "%{http_code}" https://ollama.com/api/web_search \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

- `200` — всё работает
- `401` — неверный ключ
- `000` или timeout — нет доступа к ollama.com

### Шаг 3: тестовый поиск через скрипт

```bash
bash ~/.openclaw/workspace/skills/ollama-search/scripts/ollama-search.sh \
  --query "test query" --max-results 1
```

---

## Диагностика проблем

### Скилл не появляется в списке

1. Проверь, что файл `SKILL.md` на месте:
   ```bash
   ls -la ~/.openclaw/workspace/skills/ollama-search/SKILL.md
   ```
2. Проверь, что скилл включён в конфиге:
   ```bash
   jq '.skills.entries.ollama_search' ~/.openclaw/openclaw.json
   ```
3. Перезапусти gateway:
   ```bash
   docker compose restart openclaw-gateway
   ```

### Ошибка "OLLAMA_API_KEY is not set"

Ключ не попадает в окружение скрипта. Проверь:

```bash
jq '.skills.entries.ollama_search.env.OLLAMA_API_KEY' ~/.openclaw/openclaw.json
```

Если значение `null` — добавь ключ через jq (см. выше).

### Ошибка 401 (Unauthorized)

- Ключ невалидный или истёк
- Создай новый на `https://ollama.com/settings/keys`
- Обнови в `openclaw.json` и перезапусти gateway

### Таймаут или нет ответа

- Проверь сетевой доступ из контейнера:
  ```bash
  docker compose exec openclaw-gateway curl -s https://ollama.com/api/web_search \
    -H "Authorization: Bearer $OLLAMA_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"query":"ping"}'
  ```
- Если нет доступа — проверь DNS и firewall контейнера

### Скрипт не исполняется

```bash
# Проверь права
ls -la ~/.openclaw/workspace/skills/ollama-search/scripts/

# Сделай исполняемым
chmod +x ~/.openclaw/workspace/skills/ollama-search/scripts/*.sh
```

### Exec mode отключён

Скрипты требуют exec mode. Проверь:

```bash
jq '.tools.exec' ~/.openclaw/openclaw.json
```

Должно быть `"security": "full"` или `"sandbox"`. Если `"none"` — скрипты не запустятся.
