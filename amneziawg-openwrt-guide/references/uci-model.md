# AmneziaWG OpenWrt: UCI модель

## Базовая идея

Используется интерфейс OpenWrt с:

- `option proto 'amneziawg'`

И peer sections типа:

- `config amneziawg_<iface>`

Где `<iface>` это имя интерфейса.

## Ключевые поля интерфейса

Поддерживаемые helper-ом поля:

- `private_key`
- `listen_port`
- `addresses`
- `mtu`
- `fwmark`
- `nohostroute`
- `tunlink`
- `awg_jc`
- `awg_jmin`
- `awg_jmax`
- `awg_s1`
- `awg_s2`
- `awg_h1`
- `awg_h2`
- `awg_h3`
- `awg_h4`

Особенность:

- `private_key=generate` поддерживается, ключ генерируется при первом setup.

## Ключевые поля peer sections

- `description`
- `public_key`
- `preshared_key`
- `allowed_ips`
- `route_allowed_ips`
- `endpoint_host`
- `endpoint_port`
- `persistent_keepalive`
- `disabled`

## Практический шаблон

```text
config interface 'awg0'
  option proto 'amneziawg'
  option private_key 'generate'
  list addresses '10.8.0.2/32'
  option listen_port '51820'
  option mtu '1420'
  option nohostroute '1'
  option awg_jc '4'
  option awg_jmin '40'
  option awg_jmax '70'

config amneziawg_awg0
  option description 'main-peer'
  option public_key 'BASE64_PUBLIC_KEY'
  option endpoint_host 'vpn.example.com'
  option endpoint_port '51820'
  option route_allowed_ips '1'
  option persistent_keepalive '25'
  list allowed_ips '0.0.0.0/0'
  list allowed_ips '::/0'
```

## Что делает helper

- создает интерфейс kernel mode через `ip link add dev <iface> type amneziawg`;
- либо запускает `amneziawg-go <iface>`;
- генерирует временный wireguard-style конфиг;
- добавляет маршруты из `allowed_ips`, если включен `route_allowed_ips`.

## LuCI возможности

LuCI plugin умеет:

- генерировать key pair;
- генерировать preshared key;
- вычислять public key из private key;
- показывать status page с peers/handshakes;
- генерировать QR при наличии `qrencode`.
