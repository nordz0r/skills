---
name: podkop-openwrt-guide
description: >-
  Полная русскоязычная справка по Podkop на OpenWrt. Используй этот skill при
  любых задачах по `itdoginfo/podkop`: установка, обновление, миграция
  `/etc/config/podkop`, настройка selective/domain routing через `sing-box`,
  работа с `dnsmasq`, `nft/tproxy`, LuCI UI, proxy URL-строками (vless,
  trojan, ss, hysteria2, socks), community/user lists, selector/urltest,
  exclusion, Clash API/YACD dashboard, BadWAN мониторинг, FakeIP,
  диагностикой сервиса и разработкой `podkop`, `luci-app-podkop`,
  `fe-app-podkop`. Триггеры: podkop, luci-app-podkop, sing-box on OpenWrt,
  fakeip, proxy_string, community lists, selective routing, clash api, yacd,
  urltest, selector, exclusion.
---

# Podkop OpenWrt Guide

Podkop — orchestration-слой над `sing-box` для OpenWrt: управляет селективной маршрутизацией, правит `dnsmasq`, собирает правила/списки, генерирует NFTable-правила для tproxy и предоставляет LuCI UI.

Используй этот skill, когда нужно не просто "что-то поменять в конфиге", а понять, как Podkop связывает `UCI`, `dnsmasq`, `sing-box`, `nft` и сервисный lifecycle.

## Когда использовать

- Установка или обновление Podkop на роутере с OpenWrt.
- Миграция конфига после несовместимого релиза.
- Настройка proxy-строк, selector/urltest групп, raw outbound JSON.
- Работа с community lists, user domains/subnets, remote/local lists.
- Настройка mixed proxy, YACD dashboard, Clash API, FakeIP.
- Конфигурация типов соединений: proxy, vpn, block, exclusion.
- Настройка BadWAN мониторинга интерфейсов, DNS (UDP/DoT/DoH), NTP exclusion.
- Диагностика поломок `sing-box`, `dnsmasq`, `nft`, dashboard или LuCI.
- Разработка shell-бэкенда, LuCI UI или TypeScript frontend в репозитории `itdoginfo/podkop`.
- Анализ конфликтов с `https-dns-proxy`, `nextdns`, `passwall`, `Getdomains`.

## Архитектура (высокоуровнево)

```
UCI config (/etc/config/podkop)
       ↓
  /usr/bin/podkop (оркестратор)
       ↓
  ┌────┴────┬──────────┬──────────┬──────────┐
  ↓         ↓          ↓          ↓          ↓
helpers   nft.sh    sing-box   dnsmasq   ip rule/
rulesets           config_*   redirect  rt table
```

Трафик: клиент → NFTable (mark 0x00100000) → tproxy (127.0.0.1:1602) → sing-box → outbound (proxy/vpn/block/direct). DNS: dnsmasq → 127.0.0.42:53 (sing-box DNS inbound) → FakeIP (198.18.0.0/15) для доменного роутинга.

## Быстрый выбор workflow

- Задача про живой роутер → `references/operations.md`.
- Задача про кодовую базу и сборку → `references/repo-map.md`, затем `references/build-and-dev.md`.
- Задача про корректность proxy-строки → `references/proxy-strings.md`.

Открывай только нужный reference, не загружай все файлы сразу.

## Safety Notes

- Podkop меняет системные сервисы и конфиги роутера. Перед установкой или миграцией делай backup `/etc/config/podkop` и понимай путь отката.
- Не запускай удалённый install/update script без фиксации версии и ручной проверки содержимого.
- Remote domain/subnet lists и community data — это внешний ввод. Не считай их автоматически доверенными.

## Router Workflow

1. Зафиксируй версию OpenWrt и свободное место во flash.
2. Забэкапь `/etc/config/podkop`, конфиг `sing-box` и, если рискованно, `dnsmasq`.
3. Проверь ограничения: OpenWrt `24.10+`, `sing-box` ≥ 1.12.0, HTTP-only dashboard, нет IPv6, конфликтующие пакеты.
4. Для установки/обновления — upstream-скрипт, для миграции — раздел в `operations.md`.
5. Для диагностики — CLI Podkop (`global_check`, `check_proxy`), потом `nft`, `dnsmasq`, логи `sing-box`.

## Development Workflow

- Shell-бэкенд: `podkop/files/usr/bin/podkop` + библиотеки `podkop/files/usr/lib/*.sh`.
- LuCI пакет: `luci-app-podkop/` (собранные JS + RPC ACL + меню).
- Frontend-исходники: `fe-app-podkop/` (TypeScript, vitest, eslint, prettier).
- Release pipeline: Docker (`Dockerfile-ipk`, `Dockerfile-apk`), CI ShellCheck для shell.

## На что обращать внимание

- Podkop меняет `dnsmasq` и `sing-box`; без бэкапа легко потерять рабочий маршрутинг.
- Проект в активной разработке, документация может отставать от кода.
- После обновлений чисти LuCI cache и проверяй конфиг.
- Dashboard (YACD) работает только по HTTP, не через HTTPS или доменное имя.
- Конфиг `0.7.0+` несовместим со старыми схемами — нужна миграция.
- `sing-box` ≥ 1.12.0, `jq` ≥ 1.7.1, `coreutils-base64` ≥ 9.7.

## References

- `references/operations.md`: полная эксплуатация — установка, миграция, конфиг-модель, все CLI-команды, Clash API, архитектура трафика.
- `references/repo-map.md`: структура репозитория, shell-библиотеки, LuCI-компоненты, зоны ответственности.
- `references/build-and-dev.md`: frontend/backend workflow, CI и release build.
- `references/proxy-strings.md`: форматы URL-схем, параметры, валидация.
