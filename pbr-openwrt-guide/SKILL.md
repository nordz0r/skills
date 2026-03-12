---
name: pbr-openwrt-guide
description: "Полная русскоязычная справка по `pbr` для OpenWrt. Используй этот skill при любых задачах по policy-based routing: установка `pbr` и `luci-app-pbr`, настройка `/etc/config/pbr`, split tunneling по устройствам/доменам/портам, работа с `dnsmasq.nftset`, `mwan4`, `WireGuard`, `OpenVPN`, custom user files, DNS policies и диагностикой сервиса. Триггеры: pbr, policy based routing, policy routing, openwrt pbr, split tunneling, dnsmasq nftset, luci-app-pbr, wireguard routing policy, openvpn routing policy."
---

# PBR OpenWrt Guide

`pbr` это OpenWrt framework для rule-based routing через WAN, VPN и туннели по IP, MAC, портам, протоколам и доменам. В актуальных версиях он завязан на `fw4` и `nft`.

Используй этот skill, когда нужно не просто "сделать split tunnel", а выбрать правильный режим `resolver_set`, учесть ограничения default routing, не сломать WireGuard/OpenVPN и быстро собрать нормальную диагностику.

## Когда использовать

- Установка `pbr` и `luci-app-pbr`.
- Настройка `policy-based routing` по устройствам, доменам, IP, портам или DSCP.
- Интеграция с `dnsmasq-full`, `mwan4`, `WireGuard`, `OpenVPN`, `Tailscale`, `Tor`.
- Разбор `/etc/config/pbr`, custom user files и DNS policies.
- Диагностика broken domain policies, interface hotplug, default route conflicts.

## Быстрый выбор workflow

- Если задача про первичную настройку: открой `references/install-and-config.md`.
- Если задача про сложные сценарии и ограничения: открой `references/scenarios-and-limits.md`.
- Если задача про поломку сервиса или domain routing: открой `references/troubleshooting.md`.

Не загружай все references сразу: актуальная документация по `pbr` большая и намного полезнее, если читать целевыми кусками.

## Workflow

1. Уточни версию OpenWrt и тип пакетного менеджера: `opkg` или `apk`.
2. Определи цель маршрутизации: устройство, порт, домен, DNS policy, DSCP, multi-WAN.
3. Уточни, кто делает DNS: `dnsmasq`, `dnsmasq-full`, browser DoH, сторонний resolver.
4. Если в задаче участвуют WireGuard/OpenVPN серверы, сразу проверяй special cases из references.
5. Для domain policies по возможности используй `dnsmasq.nftset` и помни про DNS cache на клиентах.

## На что обращать внимание

- `pbr` не меняет default route сам по себе; он влияет только на трафик, который совпал с политиками.
- `pbr` не поддерживает "killswitch router mode" с разрушенной стандартной схемой `lan -> wan`.
- Если VPN-туннель стал default route, часть сценариев WireGuard/OpenVPN требует специальных исключений.
- Для больших списков доменов/IP лучше использовать custom user files, а не раздувать UCI вручную.
- Сам upstream-репозиторий `stangri/pbr` тонкий; основная operational truth живет в отдельном docs-репозитории автора.

## References

- `references/install-and-config.md`: установка, requirements и ключевые настройки `/etc/config/pbr`.
- `references/scenarios-and-limits.md`: common scenarios, DNS/domain policies, WireGuard/OpenVPN caveats, custom user files.
- `references/troubleshooting.md`: команды диагностики, broken domain policies, hotplug, forwarding recovery.
