---
name: podkop-openwrt-guide
description: "Полная русскоязычная справка по Podkop на OpenWrt. Используй этот skill при любых задачах по `itdoginfo/podkop`: установка, обновление, миграция `/etc/config/podkop`, настройка selective/domain routing через `sing-box`, работа с `dnsmasq`, `nft/tproxy`, LuCI UI, proxy URL-строками, community/user lists, диагностикой сервиса и разработкой `podkop`, `luci-app-podkop`, `fe-app-podkop`. Триггеры: podkop, luci-app-podkop, sing-box on OpenWrt, fakeip, proxy_string, community lists, selective routing."
---

# Podkop OpenWrt Guide

Podkop это orchestration-слой над `sing-box` для OpenWrt: он управляет селективной маршрутизацией, правит `dnsmasq`, собирает правила/списки и поднимает LuCI UI.

Используй этот skill, когда нужно не просто "что-то поменять в конфиге", а понять, как Podkop связывает `UCI`, `dnsmasq`, `sing-box`, `nft` и сервисный lifecycle.

## Когда использовать

- Установка или обновление Podkop на роутере с OpenWrt.
- Миграция конфига после несовместимого релиза.
- Настройка `proxy_string`, community lists, user domains/subnets, mixed proxy, Yacd, FakeIP.
- Диагностика поломок `sing-box`, `dnsmasq`, `nft`, dashboard или LuCI.
- Разработка shell-бэкенда, LuCI UI или TypeScript frontend в репозитории `itdoginfo/podkop`.
- Анализ конфликтов с `https-dns-proxy`, `nextdns`, `passwall`, `Getdomains`.

## Быстрый выбор workflow

- Если задача про живой роутер: сначала открой `references/operations.md`.
- Если задача про кодовую базу и сборку: сначала открой `references/repo-map.md`, затем `references/build-and-dev.md`.
- Если задача про корректность входной proxy-строки: открой `references/proxy-strings.md`.

Открывай только нужный reference. Не загружай все файлы сразу без необходимости.

## Router Workflow

1. Зафиксируй версию OpenWrt и свободное место во flash.
2. Перед изменениями забэкапь `/etc/config/podkop`, рабочий конфиг `sing-box` и, если задача рискованная, текущий `dnsmasq`.
3. Проверь, не упирается ли задача в известные ограничения: OpenWrt `24.10`, HTTP-only dashboard, отсутствие IPv6, конфликтующие пакеты.
4. Для установки/обновления используй upstream-скрипт и сверяйся с миграциями конфига.
5. Для диагностики начинай с CLI Podkop и логов, а уже потом лезь в `nft`, `dnsmasq` и временные файлы `sing-box`.

## Development Workflow

- Shell-бэкенд живет в пакете `podkop/` и его библиотеках из `usr/lib/podkop`.
- LuCI пакет находится отдельно в `luci-app-podkop/`.
- Frontend-исходники лежат в `fe-app-podkop/` и проверяются `format`, `lint`, `test`, `build`.
- Release pipeline строит `ipk` и `apk` через Docker, а shell-часть проверяется `ShellCheck`.

## На что обращать внимание

- Podkop меняет `dnsmasq` и `sing-box`; без бэкапа легко потерять рабочий маршрутинг.
- Проект в активной разработке, README прямо предупреждает о дрейфе документации.
- После обновлений нужно чистить LuCI cache и перепроверять конфиг.
- Dashboard не работает при доступе через HTTPS или доменное имя.
- Конфиг `0.7.0+` несовместим со старыми схемами и требует отдельной миграции.

## References

- `references/operations.md`: эксплуатация, установка, миграция, CLI и важные пути.
- `references/repo-map.md`: структура upstream-репозитория и зоны ответственности.
- `references/build-and-dev.md`: frontend/backend workflow, CI и release build.
- `references/proxy-strings.md`: какие URL-схемы принимает Podkop и где искать формат.
