# AmneziaWG на Linux

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

`/etc/amnezia/amneziawg/awg0.conf` (путь может отличаться; главное —
не класть ключи в git):

```ini
[Interface]
Address = 10.8.1.1/24
ListenPort = 443
PrivateKey = <server-private>
# Obfuscation. Должны совпасть с клиентом 1:1.
Jc = 4
Jmin = 40
Jmax = 70
S1 = 0
S2 = 0
H1 = 1
H2 = 2
H3 = 3
H4 = 4

[Peer]
PublicKey = <client-public>
AllowedIPs = 10.8.1.2/32
PersistentKeepalive = 25
```

Клиент — зеркало: свой ключ, `Endpoint = vps:443`, `AllowedIPs` по политике
(полный туннель `0.0.0.0/0` или split).

Поколения AWG добавляют поля (I1–I5 и др.). Если клиент новее сервера и
шлёт extra junk — handshake не встанет. Выравнивай версии протокола.

## Подъём

```bash
awg-quick up awg0
awg show awg0
ip -br addr show awg0
ss -ulnp | grep 443
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
tcpdump -ni eth0 udp port 443
ping -c 2 10.8.1.2
```

| Симптом | Что проверить |
|---------|----------------|
| Latest handshake пустой | ключи, H1–H4/Jc, UDP ACL, NAT keepalive |
| Handshake есть, ping нет | AllowedIPs, ip forward, nft, rp_filter |
| Работает с телефона, не с ПК | разные AWG generations / разные params |
| После reboot тихо | unit не enabled, module не собрался под новое ядро |

`PersistentKeepalive = 25` на стороне за NAT обязателен.

Не вставляй реальные PrivateKey/H-параметры в чат, README, wiki.
