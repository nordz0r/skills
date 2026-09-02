# Скрытые возможности и неочевидные фичи

## Содержание
1. [Easter Eggs](#easter-eggs)
2. [Продвинутые admin-настройки](#продвинутые-admin-настройки)
3. [Неочевидные переменные окружения](#неочевидные-переменные-окружения)
4. [Скрытые API-эндпоинты](#скрытые-api-эндпоинты)
5. [Продвинутые паттерны функций](#продвинутые-паттерны-функций)
6. [Полезные трюки](#полезные-трюки)
7. [Корпоративные фичи](#корпоративные-фичи)
8. [Подводные камни](#подводные-камни)

---

## Easter Eggs

```env
ENABLE_EASTER_EGGS=true   # включено по умолчанию
```

Open WebUI содержит скрытые UI-элементы, активируемые этой переменной. Отключи в корпоративных деплоях, если хочешь строгий интерфейс.

---

## Продвинутые admin-настройки

### Автосоздание админа при первом запуске

```env
WEBUI_ADMIN_EMAIL=admin@company.com
WEBUI_ADMIN_NAME=System Admin
ENABLE_INITIAL_ADMIN_SIGNUP=true
# После bootstrap удалите эти переменные и выключите регистрацию: ENABLE_SIGNUP=false
```

После первого старта эти переменные можно убрать — аккаунт уже создан.

### Программный контроль регистрации

```env
ENABLE_SIGNUP=false              # закрыть регистрацию полностью
DEFAULT_USER_ROLE=pending        # или: регистрация открыта, но требует одобрения
```

### OAuth Token Exchange

```env
ENABLE_OAUTH_TOKEN_EXCHANGE=true
```

Позволяет обменивать OAuth-токены провайдера на внутренние JWT Open WebUI. Полезно для интеграций, где внешний сервис уже аутентифицировал пользователя.

### Forwarding User Info

```env
ENABLE_FORWARD_USER_INFO_HEADERS=false
# Включать только для доверенных внутренних провайдеров и при утверждённой PII-политике.
```

Передаёт информацию о пользователе (email, имя, роль) в заголовках запросов к LLM-провайдерам. Полезно для:
- Аудит-логирования на стороне провайдера
- Per-user rate limiting
- Персонализации ответов

Заголовки: `X-OpenWebUI-User-Email`, `X-OpenWebUI-User-Name`, `X-OpenWebUI-User-Id`.

---

## Неочевидные переменные окружения

### OFFLINE_MODE

```env
OFFLINE_MODE=true
```

Полностью отключает все исходящие HTTP-запросы. Open WebUI не будет:
- Проверять обновления
- Скачивать модели
- Обращаться к внешним API

Идеально для air-gapped окружений (закрытые сети, военные/правительственные системы).

### Лицензирование

```env
LICENSE_KEY=<your-license-key>
LICENSE_BLOB_PATH=/path/to/license.blob
```

Enterprise-лицензия. Открывает дополнительные возможности (SSO, расширенный аудит и т.д.).

### TRUSTED_SIGNATURE_KEY

```env
TRUSTED_SIGNATURE_KEY=<your-hmac-key>
```

HMAC-ключ для подписи webhook'ов. Позволяет получателю верифицировать, что webhook действительно отправлен Open WebUI.

### Множественные провайдеры

```env
OLLAMA_BASE_URLS="http://ollama1:11434;http://ollama2:11434"
OPENAI_API_BASE_URLS="https://api.openai.com/v1;http://vllm:8000/v1;http://litellm:4000"
OPENAI_API_KEYS="<key-1>;none;<key-2>"
```

Можно подключить несколько Ollama-серверов и OpenAI-совместимых API одновременно. Ключи и URL сопоставляются по позиции, разделитель — `;`.

### Database Session Sharing

```env
DATABASE_ENABLE_SESSION_SHARING=true
```

Переиспользование DB-сессий между запросами. Может улучшить производительность, но требует осторожности с async-операциями.

---

## Скрытые API-эндпоинты

### /health

```bash
curl http://localhost:8080/health
```

Health-check. Возвращает `{"status": true}` если сервис жив. Используй для readiness/liveness probes.

### /api/config

```bash
curl http://localhost:8080/api/config
```

Публичная конфигурация (без секретов). Показывает, какие фичи включены, версию и т.д.

### /api/v1/auths/api-key — с expiry

```bash
curl -X POST http://localhost:8080/api/v1/auths/api-key \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"expires_in": "30d"}'
```

Можно задать время жизни API-ключа.

### Sync functions

```bash
curl -X POST http://localhost:8080/api/v1/functions/sync \
  -H "Authorization: Bearer $TOKEN" \
  -d '[{...}, {...}]'
```

Массовая синхронизация функций — полезно для CI/CD.

### Secure function deployment

Загружай функции только из проверенного локального кода и деплой через доверенный CI/CD:

```text
POST /api/v1/functions/create
POST /api/v1/functions/sync
```

Не разворачивай исполняемый код функций из произвольных публичных URL.

---

## Продвинутые паттерны функций

### Цепочка фильтров с приоритетами

```python
# Фильтр 1: priority=0 (первый) — модерация
# Фильтр 2: priority=10 — обогащение контекста
# Фильтр 3: priority=99 (последний) — логирование

class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=0)
```

### Функция как middleware для аутентификации

```python
class Filter:
    async def inlet(self, body, __user__=None):
        if __user__ and __user__.get("role") != "admin":
            # Ограничить доступ к определённой модели
            if body.get("model") == "gpt-4":
                raise Exception("У вас нет доступа к GPT-4")
        return body
```

### Pipe с стримингом

```python
import httpx

class Pipe:
    async def pipe(self, body, __user__=None):
        async def stream():
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.valves.api_url, json=body) as resp:
                    async for chunk in resp.aiter_text():
                        yield chunk
        return stream()
```

### Event emitter для прогресса

```python
class Action:
    async def action(self, body, __user__=None, __event_emitter__=None):
        total = 10
        for i in range(total):
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": f"Обработка {i+1}/{total}...",
                    "done": False
                }
            })
            # ... work ...

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Готово!", "done": True}
        })
```

---

## Полезные трюки

### 1. Кастомные модели (Model Cards)

Через админ-панель можно создать «виртуальную модель» — обёртку над реальной с:
- Кастомным системным промптом
- Предустановленными параметрами (temperature, top_p)
- Привязанными knowledge bases
- Кастомным именем и описанием

Пользователи видят только эту «модель», не зная деталей реализации.

### 2. Промпт-шаблоны

Сохранённые промпты вызываются через `/command` в поле ввода чата. Создай через:
- UI: Workspace → Prompts → Create
- API: `POST /api/v1/prompts/create`

### 3. Каналы для командной работы

Каналы — аналог Slack-каналов, но с AI. Несколько пользователей видят один чат и могут общаться с моделью совместно.

### 4. User Presence

```
Настройки профиля → Status
```

Пользователи могут установить статус (онлайн/оффлайн/занят) и текстовое сообщение со смайликом. Видно другим пользователям.

### 5. Markdown + LaTeX в чате

Open WebUI рендерит Markdown и LaTeX ($...$, $$...$$) в сообщениях. Модели могут использовать это для форматирования ответов.

### 6. Горячие клавиши

- `Enter` — отправить сообщение
- `Shift+Enter` — новая строка
- `Ctrl+Shift+;` — голосовой ввод
- `/` — команды/промпты

### 7. Экспорт/импорт чатов

Чаты можно экспортировать в JSON через UI или API. Это позволяет:
- Переносить чаты между инстансами
- Делать бэкапы отдельных чатов
- Шарить чаты с коллегами

### 8. Файлы в чате

Перетаскивание файлов в чат автоматически использует их как контекст. Поддерживаются:
- Текстовые файлы
- PDF
- Изображения (если модель мультимодальная)

---

## Корпоративные фичи

### SCIM Provisioning

Автоматическая синхронизация пользователей из Azure AD / Okta:
```env
ENABLE_SCIM=true
SCIM_AUTH_TOKEN=<your-token>
```

### Аудит-логи

```env
ENABLE_AUDIT_LOGS_FILE=true
AUDIT_LOG_LEVEL=REQUEST_RESPONSE
```

Полный журнал: кто, когда, что запросил и что получил. Для compliance (SOC2, ISO 27001).

### OpenTelemetry

```env
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
```

Distributed tracing, metrics, logs — подключается к Grafana, Datadog, Jaeger.

### Webhook Signing

```env
TRUSTED_SIGNATURE_KEY=<your-hmac-key>
```

Все исходящие webhook'и подписываются HMAC — получатель может верифицировать подлинность.

---

## Подводные камни

### 1. WEBUI_SECRET_KEY — самая частая ошибка

Без этой переменной JWT-секрет генерируется случайно при каждом запуске. Последствия:
- Все сессии инвалидируются при перезапуске
- В кластере каждый инстанс генерирует свой секрет — токены не валидны между инстансами

**Решение**: всегда задавай `WEBUI_SECRET_KEY` в production.

### 2. SQLite не для кластера

SQLite поддерживает только одного writer'а. Два инстанса Open WebUI с общим SQLite-файлом — гарантированная коррупция данных.

### 3. bcrypt и длинные пароли

bcrypt обрезает пароль до 72 байт. С юникодом (русские символы = 2 байта) это ещё меньше символов. Пароль из 40 русских символов = 80 байт → обрезается.

### 4. Фильтры-функции и бесконечные циклы

Если outlet-фильтр вызывает другую модель, запрос снова пройдёт через все фильтры. Используй флаг в body для предотвращения:

```python
async def outlet(self, body, __user__=None):
    if body.get("_processed_by_my_filter"):
        return body
    body["_processed_by_my_filter"] = True
    # ... обработка ...
    return body
```

### 5. Порядок OPENAI_API_BASE_URLS

URL и ключи сопоставляются по позиции:
```env
OPENAI_API_BASE_URLS="http://a:8000;http://b:8000"
OPENAI_API_KEYS="key-a;key-b"
```

Если URL три, а ключей два — третий URL останется без ключа. Всегда проверяй количество.

### 6. Docker и host.docker.internal

- **Docker Desktop** (Windows/macOS): `host.docker.internal` работает из коробки
- **Linux**: нужно добавить `--add-host=host.docker.internal:host-gateway` или использовать IP хоста

### 7. Модель эмбеддингов и язык

Дефолтная `all-MiniLM-L6-v2` оптимизирована для английского. Для русского текста RAG будет работать плохо. Замени на `intfloat/multilingual-e5-large` или аналог.

### 8. WebSocket за Cloudflare

Cloudflare по умолчанию может закрывать WebSocket-соединения через 100 секунд. Настрой:
- Cloudflare Dashboard → Network → WebSockets → Enable
- Увеличь timeout в настройках Origin Rules

### 9. Потеря данных при обновлении Docker

Если данные не в volume — они живут только в контейнере:
```bash
# ПРАВИЛЬНО: named volume
docker run -v open-webui-data:/app/backend/data ...

# НЕПРАВИЛЬНО: данные внутри контейнера
docker run ...  # после docker rm — данные потеряны
```

### 10. CORS в production

```env
CORS_ALLOW_ORIGIN=*   # ← НЕ ДЕЛАЙ ТАК в production!
CORS_ALLOW_ORIGIN=https://chat.example.com  # ← правильно
```
