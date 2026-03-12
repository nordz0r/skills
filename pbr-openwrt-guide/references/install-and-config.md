# PBR: установка и базовая конфигурация

## Установка

### OpenWrt 25.12 и новее

```sh
apk update
apk add pbr luci-app-pbr
```

### OpenWrt 24.10 и старее

```sh
opkg update
opkg install pbr luci-app-pbr
```

## Requirements

Для стандартных сборок OpenWrt `23.05+` дополнительный пакетный набор обычно не нужен.

Для нестандартных сборок upstream рекомендует проверить:

- `resolveip`
- `ip-full`

## dnsmasq-full

Если нужны быстрые и корректные domain policies, предпочитай `resolver_set 'dnsmasq.nftset'`.

Для этого нужен `dnsmasq-full` с поддержкой nft sets.

## Важные параметры `pbr.config`

Минимальный набор, который чаще всего нужно понимать:

- `enabled`
- `verbosity`
- `strict_enforcement`
- `resolver_set`
- `ipv6_enabled`
- `supported_interface`
- `ignored_interface`
- `icmp_interface`
- `uplink_interface`
- `uplink_interface6`
- `lan_device`
- `netifd_enabled`

## Практические правила

- Сервис по умолчанию отключен.
- Включение через UCI:

```sh
uci set pbr.config.enabled='1'
uci commit pbr
```

- Если задача про домены, сначала думай о DNS path, потом о самих политиках.
- Если интерфейс не появляется в LuCI dropdown, он может требовать `supported_interface`.

## Что такое хорошие первые настройки

- `resolver_set='dnsmasq.nftset'` при наличии `dnsmasq-full`;
- `verbosity='2'` на время диагностики;
- `strict_enforcement='1'`, если важна минимизация утечек через default gateway;
- `supported_interface` для нестандартных интерфейсов и туннелей.
