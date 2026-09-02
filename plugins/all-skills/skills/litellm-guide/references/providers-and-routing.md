# Providers, models, routing

## Provider naming

Обычно модель указывается как `<provider>/<model>` или `<provider>/<deployment>`:

- `openai/gpt-4o`
- `anthropic/claude-...`
- `azure/<deployment-name>`
- `vertex_ai/<model>`
- `bedrock/<model-id>`
- `ollama/<local-model>`
- OpenAI-compatible endpoints: provider-specific prefix или `openai/<model>` с `api_base`.

Если возникает `LLM Provider NOT provided`, проверь prefix, `custom_llm_provider`, proxy `model_name` -> `litellm_params.model`, и provider registration.

## Capabilities и pricing

- Не хардкодь capability checks в provider code, если флаг model-specific.
- Добавляй/обновляй `model_prices_and_context_window.json` и используй `get_model_info` или существующие helpers вроде `supports_reasoning`.
- `provider_endpoints_support.json` помогает проверить endpoint support по providers.
- Для новых моделей проверь context window, input/output cost, mode/endpoints, tool/function calling, vision/audio/reasoning flags.

## Router concepts

Router выбирает deployment для logical model. Используй, когда есть несколько deployments с одинаковым `model_name` или нужны fallbacks.

Основные настройки:

- strategy: simple shuffle, least busy, lowest latency, lowest cost, lowest TPM/RPM и др.;
- retries/fallbacks/context-window fallbacks;
- cooldowns и health checks;
- max parallel requests;
- Redis-backed state для multi-replica proxy;
- traffic mirroring/silent experiments.

## Proxy routing

В proxy routing задается через `model_list` и `router_settings`. Пример:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt4o-prod-a
      api_base: os.environ/AZURE_API_BASE_A
      api_key: os.environ/AZURE_API_KEY_A
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY

router_settings:
  routing_strategy: least-busy
  num_retries: 2
```

## Добавление OpenAI-compatible provider без Python-кода

Если endpoint совместим с OpenAI, сначала проверь JSON/provider registration path из docs: часто достаточно указать API base, env key, supported endpoints и parameter mapping. Переходи к Python implementation только если нужна нестандартная трансформация request/response, auth, streaming или error mapping.

## Добавление provider через код

См. `repo-development.md`: следуй existing provider patterns, config class от `BaseConfig`, transformations, sync/async/streaming tests, error mapping.
