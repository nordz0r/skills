# Маршрутизация и Auto-Combo

## Combo Routing

Combo — именованная конфигурация цепочки provider+model+connection с выбранной стратегией.

### 17 стратегий

`priority`, `weighted`, `fill-first`, `round-robin`, `P2C`, `random`, `least-used`, `cost-optimized`, `reset-aware`, `reset-window`, `headroom`, `strict-random`, `auto`, `lkgp`, `context-optimized`, `context-relay`, `fusion`.

Source: `ROUTING_STRATEGY_VALUES` in `src/shared/constants/routingStrategies.ts`.

### Flow

```
handleComboChat()
  → resolveComboTargets() → ResolvedComboTarget[]
  → for each target: handleSingleModel()
    → circuit breaker check
    → handleChatCore() with per-target error handling
  → first success wins (except fusion)
```

### Fusion strategy

Параллельный fan-out к панели моделей → judge model синтезирует финальный ответ (`open-sse/services/fusion.ts`).

## Auto-Combo (model: auto)

### Variants

| Model | Приоритет | Use case |
|-------|-----------|----------|
| `auto` | Balanced | General chat |
| `auto/coding` | taskFit=37% | Code, debugging |
| `auto/fast` | latency=32% | Low latency |
| `auto/cheap` | cost=37% | Min cost |
| `auto/smart` | taskFit + exploration | Complex tasks |
| `auto/offline` | quota=37% | Max capacity |

### 12-factor scoring (weights vary by variant)

| Factor | Default weight | Meaning |
|--------|---------------|---------|
| Health | 20% | Circuit breaker state |
| Quota | 15% | Remaining capacity |
| Cost | 15% | Price per token |
| Speed | 12% | p50 latency |
| Task Fit | 8% | Task-type affinity |
| Stability | 5% | Error rate |
| Tier | 5% | Account tier |
| Other | 20% | Context affinity, density, ... |

Score 0–1 per provider; highest wins.

### Примеры

```bash
# Balanced
curl ... -d '{"model":"auto","messages":[...]}'

# Code
curl ... -d '{"model":"auto/coding","messages":[...]}'

# Force provider
curl ... -d '{"model":"anthropic/claude-sonnet-4","messages":[...]}'

# Named combo as model
curl ... -d '{"model":"my-fast-combo","messages":[...]}'
```

## Combo Management

### Dashboard

`/dashboard/combos` — builder, strategies, templates, model routing rules.

`/dashboard/auto-combo` — scoring weights, mode packs, virtual factory presets, telemetry.

### MCP

```
omniroute_list_combos
omniroute_switch_combo        # activate/deactivate
omniroute_set_routing_strategy
omniroute_best_combo_for_task
omniroute_simulate_route      # dry-run
omniroute_explain_route       # why this provider
omniroute_test_combo          # live test all targets
```

### API

`POST /api/combos/`, `GET /api/combos/`, combo metrics endpoints.
См. `docs/reference/API_REFERENCE.md` → Combo Management.

## Model Aliases

30+ cross-proxy dialect normalizations auto-seeded at startup. Позволяют использовать привычные имена моделей независимо от upstream.

## Context Relay

Session handoff summaries при account rotation — continuity между ключами одного провайдера.

## Compression + Routing

Per-request override: header `x-omniroute-compression` (highest precedence).

Priority: request header > routing-combo override > active profile > auto-trigger > default > off.

## Wildcard Router

`open-sse/services/wildcardRouter.ts` — pattern matching для model names.

## Emergency Fallback

`open-sse/services/emergencyFallback.ts` — last-resort routing при total combo failure.