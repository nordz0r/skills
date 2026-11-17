# LiteLLM Proxy / AI Gateway

## Минимальный запуск

CLI quickstart:

```bash
uv tool install 'litellm[proxy]'
litellm --model huggingface/bigcode/starcoder --detailed_debug
```

Production-like запуск обычно использует config:

```bash
litellm --config config.yaml --port 4000
```

## Минимальный `config.yaml`

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

litellm_settings:
  set_verbose: false

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

Для Azure/OpenAI-compatible providers обычно нужны `api_base`, `api_version` или custom headers. Секреты держи в env/secret manager, не в plain YAML.

## Вызов через OpenAI client

```python
import openai

client = openai.OpenAI(
    api_key="sk-litellm-virtual-key-or-master-key",
    base_url="http://localhost:4000",
)

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
```

## Основные config секции

- `model_list`: logical model names и provider-specific `litellm_params`.
- `litellm_settings`: callbacks, redaction, drop params, request behavior.
- `router_settings`: routing strategy, retries, fallbacks, Redis, cooldowns.
- `general_settings`: DB, master key, UI/auth settings, proxy-wide behavior.
- `guardrails`: guardrail providers and modes.

## Auth, keys, teams

- Master key нужен для admin endpoints и bootstrap.
- Virtual keys дают per-key/team/user access, budgets, rate limits и spend tracking.
- Teams/organizations/model access groups ограничивают, какие logical models доступны.
- Для live проверки используй `/key/info`, `/team/info`, `/organization/list`, `/model/info` при наличии прав.

## Model management

- Static: добавь запись в `model_list`.
- Dynamic DB-backed: используй Admin UI или `/model/new`, затем проверяй `/model/info`.
- `/models` показывает доступные model ids; `/model/info` полезнее для api_base, access groups, mode и metadata.

## Spend/logging/observability

- Spend tracking работает через virtual keys/users/teams и model pricing.
- Для корректной стоимости проверь pricing/capability entry модели.
- Logging callbacks настраиваются централизованно: Langfuse, OpenTelemetry, Prometheus, Datadog, generic API, S3/GCS, etc.
- Redaction/message logging — отдельное решение: для security-sensitive deployment включай redaction и проверяй, какие поля реально уходят в callback.

## Guardrails

Guardrails можно включать в `config.yaml`, на request, per-key/team/model/tag и через policies. Перед изменением guardrail поведения уточни mode: pre-call, post-call, during-call/streaming, logging-only.

## MCP/A2A

LiteLLM Gateway может быть единым endpoint для LLM, MCP tools и A2A agents. Для MCP задач проверь server registration, auth headers, access control и `/v1/responses` path.
