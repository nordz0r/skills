# AmneziaWG на Linux (awg / awg-quick)

Сверено 2026-10-15: `amneziawg-tools` v3.1.20260812 (`wg-quick/linux.bash`), `amneziawg-go` v3.1.20260828, kmod v3.1.20260906. Параметры обфускации — единственный дом: `awg-protocol.md`.

## Kernel vs userspace

```bash
uname -r
modinfo amneziawg 2>/dev/null | head
lsmod | grep amnezia
which awg awg-quick
awg show
```

Если модуля нет — либо собрать `amnezia-vpn/amneziawg-linux-kernel-module`
под текущий kernel, либо userspace `amneziawg-go`. После обновления ядра
module DKMS/dkms-эквивалент нужно пересобрать, иначе интерфейс не поднимется.

Не путай `wg` и `awg`. Обычный `wg-quick` не читает Jc/H1 и поднимет
несовместимый интерфейс.

## Конфиг awg-quick

`awg-quick up awg0` ищет `/etc/amnezia/amneziawg/awg0.conf` (короткое имя → этот путь, `linux.bash`).
Ключи в git не класть.

```ini
[Interface]
Address = 10.8.1.1/24
ListenPort = 55424            # дефолт AWG в amnezia-client; клиент: Endpoint = <vps>:55424
PrivateKey = <server-private>
# Пример для AWG 3.1 на обеих сторонах. Shared-параметры совпадают 1:1
# с разделом «Шаблон» в awg-protocol.md (клиент AWG 3.1):
S1 = 24
S2 = 37
S3 = 18
S4 = 12
H1 = 100000000-100100000
H2 = 200000000-200100000
H3 = 300000000-300100000
H4 = 400000000-480000000
HeaderProtectionKey = <awg genkey>   # AWG 3.0+, тот же ключ, что у клиента
RandomTrailers = on                  # AWG 3.1, включить на обеих сторонах
# Для AWG 2.0: удалить HeaderProtectionKey и RandomTrailers на обеих сторонах.
# Только у клиента (sender-only / client-side / локальные), на сервере не нужны:
# Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition, DisableCookies, PersistentKeepalive.

[Peer]
PublicKey = <client-public>
PresharedKey = <psk>
AllowedIPs = 10.8.1.2/32
```

Клиент — шаблон из раздела «Шаблон» в `awg-protocol.md`: свой ключ, `Endpoint = <vps>:55424`,
`AllowedIPs` по политике (полный туннель `0.0.0.0/0, ::/0` или split).

Совместимость версий: неизвестный устройству ключ (например, `RandomTrailers` на 2.0)
ломает подъём интерфейса; расхождение `H1–H4`/`S1–S4`/`HeaderProtectionKey`/`RandomTrailers`
даёт «нет handshake». `Jc`/`I1–I5` на разных сторонах могут отличаться. Подробно — `awg-protocol.md`.

## Подъём

```bash
awg-quick up awg0
awg show awg0
ip -br addr show awg0
ss -ulnp | grep 55424
```

systemd unit:

```ini
[Unit]
Description=AmneziaWG awg0
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/awg-quick up awg0
ExecStop=/usr/bin/awg-quick down awg0

[Install]
WantedBy=multi-user.target
```

NAT на VPS, если клиентам нужен выход в интернет:

```bash
sysctl -w net.ipv4.ip_forward=1
nft add table inet nat
nft add chain inet nat postrouting '{ type nat hook postrouting priority 100; }'
nft add rule inet nat postrouting oifname "eth0" ip saddr 10.8.1.0/24 masquerade
```

Таблица/имя WAN-интерфейса проверь на хосте. Постоянные nft-правила —
через `linux-routing`.

## Диагностика handshake

```bash
awg show awg0
awg show awg0 dump
journalctl -k | grep -i amnezia
tcpdump -ni eth0 udp port 55424
ping -c 2 10.8.1.2
```

| Симптом | Что проверить |
|---------|----------------|
| Latest handshake пустой | ключи, H1–H4/S1–S4/HeaderProtectionKey/RandomTrailers, UDP ACL, NAT keepalive |
| Handshake есть, ping нет | AllowedIPs, ip forward, nft, rp_filter |
| Работает с телефона, не с ПК | версия клиента не тянет AWG 2.0/3.x (мин. версии — `awg-protocol.md`), разные shared-params |
| После reboot тихо | unit не enabled, module не собрался под новое ядро |

`PersistentKeepalive = 25` нужен на стороне за NAT (дефолт amnezia-client — 25, в 3.x диапазон `25-35`).

Не вставляй реальные PrivateKey/H-параметры в чат, README, wiki.
