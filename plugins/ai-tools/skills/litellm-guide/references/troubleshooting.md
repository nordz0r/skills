# LiteLLM troubleshooting

## Быстрый triage flow

1. Зафиксируй поверхность: SDK direct call или Proxy/Gateway.
2. Проверь auth: provider key vs LiteLLM virtual/master key.
3. Проверь model route: requested `model`, proxy `model_name`, `litellm_params.model`, provider prefix.
4. Проверь provider reachability и endpoint support.
5. Сравни provider error vs gateway error.
6. Проверь logs/spend/audit callbacks только после успешной route/auth диагностики.

## Proxy health/readiness

- `GET /health` — proxy health.
- `GET /models` — visible models for the caller.
- `GET /model/info` — detailed runtime model metadata; используй для DB-backed model state.
- Admin UI может показывать DB-backed state, который отсутствует в YAML.

## Debug transformed request

Используй `/utils/transform_request`, чтобы увидеть payload, который LiteLLM отправит provider: полезно для prompt formatting, headers, provider-specific params, tool/function schema issues.

## Частые ошибки

### `LLM Provider NOT provided`

Проверь:

- есть ли provider prefix (`openai/`, `azure/`, `bedrock/`, etc.);
- не перепутан ли proxy logical `model_name` с provider model id;
- указан ли `custom_llm_provider` для нестандартного provider;
- есть ли provider registration и endpoint support.

### 401/403

Раздели:

- LiteLLM auth failure: virtual key/master key/JWT/team access/model access group.
- Provider auth failure: upstream API key, Azure base/version, AWS region/credentials, Vertex ADC/service account.
- Network/proxy failure: корпоративный proxy, NO_PROXY для internal services, TLS/CA.

### 404 model not found

Проверь `/model/info`, model alias, model access group, team restrictions и provider deployment name. Для Azure `model` обычно deployment name, не public model id.

### Cost/spend неверный или пустой

Проверь:

- virtual key/team/user attached;
- model pricing entry;
- `model` in response matches tracked model;
- callbacks/spend log settings;
- custom pricing для self-hosted/OpenAI-compatible models.

### Logs отсутствуют или ломают ingest

Проверь callback config, redaction, payload shape и receiver errors. Не удаляй audit-relevant tool/result data без замены summary fields. Для schema explosion нормализуй payload раньше в callback path, а downstream pipeline держи safety net.

## Provider vs Gateway диагностика

- Если direct provider call работает, а proxy нет: смотри auth, route, model access, transformation, proxy network/env.
- Если proxy route строится, но provider возвращает ошибку: смотри provider credentials/params/version/api_base.
- Если request успешен, но нет logs/spend: смотри callbacks, DB, spend settings, model pricing.

## Live-state правило

Для deployments с `store_model_in_db` или Admin UI model management не делай выводы только по `config.yaml`. Запроси `/model/info` и, при необходимости, team/org/key endpoints.
