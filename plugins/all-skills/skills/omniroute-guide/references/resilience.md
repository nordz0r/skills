# Resilience — 3 слоя (не путать!)

Три **разных** механизма временных отказов. Scope и debugging — отдельно.

## 1. Provider Circuit Breaker

**Scope:** весь провайдер (`glm`, `openai`, `anthropic`).

**Purpose:** остановить трафик к repeatedly failing provider.

**Implementation:**
- `src/shared/utils/circuitBreaker.ts`
- Gate: `src/sse/handlers/chatHelpers.ts`, `chat.ts`
- Status: `GET /api/monitoring/health`
- Reset: `POST /api/resilience/reset`
- DB: `domain_circuit_breakers`

**States:**
- `CLOSED` — normal
- `DEGRADED` — elevated failures tracked, traffic allowed
- `OPEN` — blocked, combo skips
- `HALF_OPEN` — probe after reset timeout

**Defaults:**

| Class | Degraded | Opens | Reset |
|-------|----------|-------|-------|
| OAuth | 5 failures | 8 | 60s |
| API-key | 7 | 12 | 30s |
| Local | derived | 2 | 15s |

**Trip codes:** только `408, 500, 502, 503, 504`. НЕ trip для 401/403/429 (это cooldown/lockout).

**Lazy recovery:** expired OPEN → HALF_OPEN on read (`getStatus()`, `canExecute()`).

## 2. Connection Cooldown

**Scope:** один connection/account/key.

**Purpose:** skip bad key, другие keys того же провайдера работают.

**Fields:**
- `rateLimitedUntil` — timestamp
- `testStatus: "unavailable"`
- `lastError`, `errorCode`, `backoffLevel`

**Skipped when:** `new Date(rateLimitedUntil).getTime() > Date.now()`

**Defaults:**
- OAuth base cooldown: 5s
- API-key base: 3s
- 429: prefer `Retry-After` / reset headers
- Backoff: `baseCooldownMs * 2 ** failureIndex`

**Terminal states (НЕ cooldown):** `banned`, `expired`, `credits_exhausted` — until manual reset.

**Anti-thundering-herd:** mutex prevents concurrent failures from over-extending cooldown.

## 3. Model Lockout

**Scope:** provider + connection + model.

**Purpose:** disable только одну модель, connection serves other models.

**Examples:** per-model 429, local 404 for missing model, Grok mode permission failures.

**Implementation:** `open-sse/services/accountFallback.ts`

## Debugging Guide

| Symptом | Проверить |
|---------|-----------|
| Весь провайдер excluded | Circuit breaker + all connections `rateLimitedUntil` |
| Provider "permanently" excluded | Code reads raw `state` vs `getStatus()` |
| Один key fails, others OK | Connection cooldown (not breaker) |
| Одна модель fails | Model lockout |
| Should self-recover | Future timestamp + lazy read path |

## MCP Tools

```
omniroute_get_health
omniroute_get_provider_metrics    # p50/p95/p99, breaker state
omniroute_set_resilience_profile  # aggressive/balanced/conservative
omniroute_db_health_check
```

## Dashboard

`/dashboard/health` — uptime, circuit breakers, rate limits, quota sessions.

Settings → Resilience tab — thresholds, presets.

## Presets

| Preset | Behavior |
|--------|----------|
| `aggressive` | Fast trip, short reset |
| `balanced` | Default |
| `conservative` | High threshold, long reset |