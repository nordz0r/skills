# LiteLLM repo development

## Карта репозитория

- `litellm/`: core library.
- `litellm/llms/`: provider implementations and transformations.
- `litellm/proxy/`: Gateway server, auth, management endpoints, MCP/A2A, middleware.
- `litellm/router_utils/` и `litellm/router_strategy/`: routing/load balancing support.
- `litellm/types/`: typed request/response schemas.
- `tests/`: SDK, provider, proxy, enterprise, UI, e2e tests.
- `docs/my-website/docs/`: documentation source.
- `ui/litellm-dashboard/`: Admin UI.
- `model_prices_and_context_window.json`: model pricing/capabilities source.
- `provider_endpoints_support.json`: endpoint support source.

## Provider implementation rules

1. Найди ближайший existing provider в `litellm/llms/<provider>/`.
2. Следуй transformation/config class patterns, обычно через `BaseConfig`.
3. Поддержи sync и async, а streaming — если provider умеет streaming.
4. Сохрани OpenAI-format output и LiteLLM exception mapping.
5. Не добавляй model-specific hardcode для capability flags; используй pricing/model info helpers.
6. Добавь provider docs и tests.

## OpenAI-compatible provider

Если provider полностью или почти OpenAI-compatible, предпочитай JSON registration/config approach. Python-код оправдан для нестандартных параметров, auth, endpoint paths, response transformation, tool/stream quirks или error mapping.

## Proxy DB rule

В proxy DB коде не используй `execute_raw`/`query_raw`. Используй Prisma model methods:

```python
await prisma_client.db.litellm_tooltable.upsert(...)
await prisma_client.db.litellm_tooltable.find_many(...)
await prisma_client.db.litellm_tooltable.find_unique(...)
```

Это сохраняет совместимость со schema, mocks и type casting.

## HTTP/SDK client cache rule

Не закрывай HTTP/SDK clients на cache eviction paths (`LLMClientCache._remove_key()` и похожие). Evicted clients могут быть у in-flight requests; cleanup выполняется shutdown flow.

## UI rules

- Tremor deprecated; не используй новые Tremor компоненты, кроме Table и subcomponents.
- Предпочитай common components.
- Проверяй backend contract: single value vs array до выбора single-select/multi-select.
- Provider logos должны быть в source и prebuilt out paths; SVG через `<img>` не должен полагаться на `fill="currentColor"`.

## Test commands

- Unit tests: `poetry run pytest tests/test_litellm/ -x -vv -n 4`
- UI tests: `cd ui/litellm-dashboard && npx vitest run`
- Ruff fast lint: `cd litellm && poetry run ruff check .`
- Перед commit форматируй: `poetry run black .`
- Не передавай pytest `--timeout`: flag недоступен в этом окружении.
- Если OpenAPI tests требуют deps: `poetry run pip install openapi-core`; pytest-postgresql может требовать `psycopg-binary`.

## Documentation updates

При изменении public behavior обновляй docs рядом с feature domain. Для provider changes обновляй provider docs и pricing/capability metadata.
