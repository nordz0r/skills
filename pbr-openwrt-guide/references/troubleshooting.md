# PBR: диагностика

## Первая безопасная последовательность

```sh
uci set pbr.config.verbosity='2'
uci commit pbr
/etc/init.d/pbr reload
/etc/init.d/pbr status
/etc/init.d/pbr status -d
logread -e pbr
uci export pbr
```

Для `1.2.3` команда `status` по умолчанию короткая, а `status -d` дает подробную диагностику.

## Если доменные правила не работают

Проверь по порядку:

1. Используется ли `dnsmasq.nftset`.
2. Не сидит ли клиент на закэшированном DNS.
3. Не включен ли browser DoH / 1.1.1.1 app / другой внешний resolver path.
4. Не выведен ли конкретный клиент в отдельную DNS policy.
5. Нужен ли `pbr.user.dnsprefetch`.

## Если интерфейс не перезагружается корректно

Часть пользователей upstream лечит это hotplug script-ом, который делает:

```sh
/etc/init.d/pbr reload_interface "$INTERFACE"
```

Это полезно, если PROCD subscriptions иногда не ловят обновление нужного интерфейса.

## Если после reload/start пропал forwarding

У `strict_enforcement` и restart window есть побочный эффект: forwarding может остаться выключенным после сбоя/обрыва питания.

В таком случае upstream рекомендует:

```sh
service pbr enable_forward
```

## Что помнить про default routing

- `pbr` не меняет default route сам.
- Если VPN client уводит default route в туннель, сначала исправляй конфиг OpenVPN/WireGuard, а не пытайся "додавить" это политиками.

Для WireGuard client проверь:

```text
option route_allowed_ips '0'
```

если цель именно split tunnel, а не full tunnel.
