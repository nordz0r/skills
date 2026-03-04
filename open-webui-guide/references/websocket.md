# WebSocket и реалтайм

## Содержание
1. [Архитектура](#архитектура)
2. [Настройка](#настройка)
3. [События](#события)
4. [Кластерный режим](#кластерный-режим)
5. [Collaborative editing (Y.js)](#collaborative-editing)
6. [Отладка](#отладка)

---

## Архитектура

Open WebUI использует **Socket.IO** поверх WebSocket для реалтайм-функций:
- Обновления чатов в реальном времени
- Стриминг ответов моделей
- Пользовательский presence (онлайн/оффлайн)
- Коллаборативное редактирование (Y.js CRDT)
- Уведомления

Ключевой файл: `backend/open_webui/socket/main.py`

### Stack

```
Клиент (SvelteKit) ←→ Socket.IO ←→ FastAPI (asyncio)
                                        ↕
                                    [Redis adapter] (для кластера)
```

---

## Настройка

### Базовая (один инстанс)

```env
ENABLE_WEBSOCKET_SUPPORT=true
# WEBSOCKET_MANAGER=           # пусто = локальный менеджер
```

### Кластерная (несколько инстансов)

```env
ENABLE_WEBSOCKET_SUPPORT=true
WEBSOCKET_MANAGER=redis
WEBSOCKET_REDIS_URL=redis://redis:6379/1
WEBSOCKET_REDIS_CLUSTER=false
```

### Таймауты

```env
WEBSOCKET_SERVER_PING_TIMEOUT=20     # секунд до разрыва при отсутствии pong
WEBSOCKET_SERVER_PING_INTERVAL=25    # секунд между ping-ами
```

---

## События

### Подключение/отключение

При подключении клиент отправляет JWT-токен. Сервер:
1. Валидирует токен
2. Регистрирует пользователя в комнате (room) по user_id
3. Обновляет presence-статус

### Основные события

| Событие | Направление | Описание |
|---------|-------------|----------|
| `connect` | Client → Server | Подключение с JWT |
| `disconnect` | Client → Server | Отключение |
| `chat-update` | Server → Client | Обновление чата |
| `message` | Both | Сообщение в канале |
| `presence` | Server → Client | Статус пользователя |
| `typing` | Client → Server | Индикатор набора |

### Room-based broadcast

Каждый пользователь помещается в «комнату» по своему user_id. Это позволяет отправлять события конкретному пользователю:

```python
# Серверная сторона
await sio.emit("chat-update", data, room=user_id)
```

---

## Кластерный режим

При нескольких инстансах Open WebUI за load balancer'ом:

1. **Redis adapter**: Socket.IO использует Redis Pub/Sub для синхронизации событий между инстансами
2. **Sticky sessions**: Socket.IO long-polling fallback требует, чтобы клиент всегда попадал на один и тот же инстанс

Без Redis adapter'а: клиенты, подключённые к инстансу A, не получат события, отправленные с инстанса B.

---

## Collaborative editing

Open WebUI поддерживает совместное редактирование через **Y.js** — библиотеку CRDT (Conflict-free Replicated Data Types).

Это позволяет нескольким пользователям одновременно редактировать:
- Заметки
- Промпты
- Другие текстовые данные

Y.js синхронизируется через тот же Socket.IO канал.

---

## Отладка

### WebSocket не подключается

1. Проверь, что `ENABLE_WEBSOCKET_SUPPORT=true`
2. Проверь reverse proxy — нужны заголовки `Upgrade` и `Connection`
3. В браузере: DevTools → Network → WS — посмотри статус handshake

### Сообщения не доходят в кластере

1. Проверь `WEBSOCKET_MANAGER=redis`
2. Проверь доступность Redis: `redis-cli ping`
3. Проверь, что все инстансы используют один Redis

### Частые реконнекты

1. Увеличь `WEBSOCKET_SERVER_PING_TIMEOUT`
2. Проверь, что reverse proxy не убивает idle-соединения (nginx: `proxy_read_timeout 86400`)
3. Проверь сетевую стабильность
