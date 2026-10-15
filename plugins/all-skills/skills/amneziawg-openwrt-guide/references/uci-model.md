# AmneziaWG OpenWrt: UCI-модель

Источник: `Slava-Shchipunov/awg-openwrt` @ 03b6226 (`amneziawg-tools/files/amneziawg.sh`, `luci-proto-amneziawg/.../protocol/amneziawg.js`), сверено 2026-10-15.
**Смысл параметров обфускации, допустимые значения и рецепты — скилл `amnezia-vpn`** (`awg-protocol.md`, `awg-config.md`); здесь только UCI-имена и специфика OpenWrt.

## Интерфейс `config interface '<iface>'`, `option proto 'amneziawg'`

| UCI-опция | Ключ `.conf` | Тип в helper | Версия AWG |
|---|---|---|---|
| `private_key` (`generate` — сгенерировать при первом подъёме) | `PrivateKey` | string | — |
| `listen_port`, `mtu`, `fwmark` | `ListenPort`, —, `FwMark` | int/string | — |
| `addresses` (list), `nohostroute`, `tunlink` | — (netifd) | — | — |
| `awg_jc`, `awg_jmin`, `awg_jmax` | `Jc`, `Jmin`, `Jmax` | int | 1.0+ |
| `awg_s1`, `awg_s2` | `S1`, `S2` | int | 1.0+ |
| `awg_s3`, `awg_s4` | `S3`, `S4` | int | 2.0+ |
| `awg_h1` … `awg_h4` | `H1` … `H4` | **string** (диапазон `a-b`) | 1.0+ (диапазоны 2.0+) |
| `awg_i1` … `awg_i5` | `I1` … `I5` | string | 1.5+ |
| `awg_header_protection_key` | `HeaderProtectionKey` | string (секрет) | 3.0+ |
| `awg_content_padding_addition` | `ContentPaddingAddition` | string (диапазон) | 3.0+ |
| `awg_rekey_after_time`, `awg_rekey_timeout`, `awg_reject_after_time`, `awg_keepalive_timeout`, `awg_max_handshake_attempts` | `RekeyAfterTime`, `RekeyTimeout`, `RejectAfterTime`, `KeepaliveTimeout`, `MaxHandshakeAttempts` | string (диапазон) | 3.0+ |
| `awg_random_trailers` | `RandomTrailers` (пишется `on`) | boolean `0/1` | 3.1 |
| `awg_disable_cookies` | `DisableCookies` (пишется `on`) | boolean `0/1` | 3.1 |

- Пустые опции в `.conf` не попадают; boolean `0` = ключ не пишется.
- Ключ 3.x при модуле/`awg` старее 3.x → `awg setconf` падает (`Invalid argument`) и интерфейс не поднимается. Версия пакетов должна быть ≥ версии параметров.
- LuCI-импорт `.conf` заполняет все эти поля, включая `RandomTrailers`/`DisableCookies`.

## Peer `config amneziawg_<iface>`

`description`, `public_key`, `preshared_key`, `allowed_ips` (list), `route_allowed_ips` (bool), `endpoint_host`, `endpoint_port`, `persistent_keepalive`, `disabled`.

## Шаблон (значения — плейсхолдеры; набор параметров бери из `amnezia-vpn/references/awg-config.md`)

```text
config interface 'awg0'
  option proto 'amneziawg'
  option private_key '<client-private>'
  list addresses '10.8.1.2/32'
  option mtu '1280'
  option awg_jc '5'
  option awg_jmin '40'
  option awg_jmax '70'
  option awg_s1 '24'
  option awg_s2 '24'
  option awg_s3 '24'
  option awg_s4 '24'
  option awg_h1 '1'
  option awg_h2 '2'
  option awg_h3 '3'
  option awg_h4 '4'
  option awg_i1 '<cps-chain>'
  option awg_header_protection_key '<hpk>'
  option awg_content_padding_addition '10-100'
  option awg_random_trailers '1'
  option awg_disable_cookies '1'

config amneziawg_awg0
  option description 'main'
  option public_key '<server-public>'
  option preshared_key '<psk>'
  option endpoint_host 'vpn.example.com'
  option endpoint_port '443'
  option route_allowed_ips '1'
  option persistent_keepalive '25'
  list allowed_ips '0.0.0.0/0'
  list allowed_ips '::/0'           # иначе IPv6 идёт мимо туннеля (утечка)
```

Чтение без секретов: `uci show network | grep -vE 'private_key|preshared_key|header_protection_key'`.
