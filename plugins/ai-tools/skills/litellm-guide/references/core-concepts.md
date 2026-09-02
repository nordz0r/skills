# LiteLLM core concepts

## Что такое LiteLLM

LiteLLM дает unified OpenAI-format интерфейс к 100+ LLM providers. Две основные поверхности:

- **Python SDK**: библиотека для прямых вызовов из приложения (`completion`, `responses`, `embedding`, `image_generation`, audio, moderation, Router).
- **AI Gateway / Proxy**: self-hosted OpenAI-compatible gateway с virtual keys, budgets/rate limits, model routing, logging, guardrails, caching, Admin UI, MCP/A2A.

## Когда выбирать SDK

Выбирай SDK, если код приложения сам владеет provider credentials, routing и observability. SDK подходит для:

- unified calls к разным providers без gateway;
- retry/fallback через `Router` внутри приложения;
- локальных callback integrations;
- provider transformation/debug при разработке LiteLLM.

## Когда выбирать Proxy/Gateway

Выбирай proxy, если нужна централизованная платформа для команды/организации:

- OpenAI-compatible endpoint для любых клиентов;
- centralized credentials и model aliases;
- virtual keys, team/user budgets, rate limits;
- spend tracking, audit/logging, guardrails, caching;
- Admin UI, MCP Gateway, A2A Agent Gateway.

## Источники истины

- **Документация**: `docs/my-website/docs/` в репозитории и https://docs.litellm.ai/docs/.
- **Provider/model capabilities**: `model_prices_and_context_window.json`, `provider_endpoints_support.json`, helpers вокруг `get_model_info`.
- **Proxy static config**: `config.yaml` (`model_list`, `litellm_settings`, `router_settings`, `general_settings`).
- **Proxy live state**: `/model/info`, `/models`, `/health`, `/key/*`, `/team/*`, `/organization/*`, spend/log endpoints. Если включено хранение моделей в БД, live endpoints важнее YAML.
- **Repo behavior**: текущий код в `litellm/`, `enterprise/`, `tests/`, `ui/litellm-dashboard/`.

## Частые домены возможностей

- Unified LLM calls: chat completions, Responses API, text completions, embeddings, images, audio, moderation, rerank, OCR, vector stores, batches, files.
- Reliability: retries, fallbacks, cooldowns, load balancing, least-busy/latency/cost strategies, traffic mirroring.
- Access: master key, virtual keys, users, teams, organizations, model access groups, JWT/SSO/SCIM in enterprise contexts.
- Spend/observability: token usage, cost tracking, callbacks, Langfuse/OpenTelemetry/Prometheus/Datadog/etc.
- Safety: guardrails, PII masking, secret detection, policy engine.
- Agents/tools: MCP Gateway, MCP access control, A2A agents, OpenAPI-to-MCP conversion.
