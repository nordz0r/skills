# Xray: установка, сервер, клиент

Сверено 2026-10-15: Xray-core v26.10.10 (`infra/conf/*.go`, `main/commands/all/*`),
docs `XTLS/Xray-docs-next` (`config/transports/reality.md`, коммит 2026-10-11),
`XTLS/REALITY` README, `XTLS/Xray-examples` (`VLESS-TCP-XTLS-Vision-REALITY`, `VLESS-XHTTP-Reality`, 2026-09-16),
`XTLS/Xray-install`.

## Установка (Linux VPS)

Официальный скрипт `XTLS/Xray-install` (systemd unit `xray`, конфиг
`/usr/local/etc/xray/config.json`). Скачай и прочитай скрипт перед запуском:

```bash
curl -fsSLo install-release.sh https://github.com/XTLS/Xray-install/raw/main/install-release.sh
less install-release.sh
sudo bash install-release.sh install
xray version
```

Альтернативы: Docker-образ `ghcr.io/xtls/xray-core`, панели (3x-ui и т.п.) —
панель тоже пишет такой же JSON, правила ниже действуют.

## Секреты

```bash
xray uuid                 # id клиента
xray x25519               # PrivateKey -> сервер; Password/PublicKey -> клиент (pbk)
openssl rand -hex 8       # shortId
xray mldsa65              # опционально: Seed -> сервер, Verify -> клиент (pqv)
xray vlessenc             # опционально: пары decryption/encryption для VLESS Encryption
```

## Сервер: VLESS + REALITY + Vision (RAW)

```json
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "listen": "0.0.0.0",
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{ "id": "<uuid>", "flow": "xtls-rprx-vision", "email": "user1" }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "raw",
      "security": "reality",
      "realitySettings": {
        "target": "www.example-donor.com:443",
        "serverNames": ["www.example-donor.com"],
        "privateKey": "<x25519-private>",
        "shortIds": ["", "<hex8>"]
      }
    },
    "sniffing": { "enabled": true, "destOverride": ["http", "tls", "quic"], "routeOnly": true }
  }],
  "outbounds": [
    { "protocol": "freedom", "tag": "direct" },
    { "protocol": "blackhole", "tag": "block" }
  ],
  "routing": {
    "rules": [
      { "ip": ["geoip:private"], "outboundTag": "block" },
      { "protocol": ["bittorrent"], "outboundTag": "block" }
    ]
  }
}
```

`"network": "raw"` — новое имя `tcp`; старые ядра понимают только `tcp`.

## Сервер: VLESS + REALITY + XHTTP

```json
"streamSettings": {
  "network": "xhttp",
  "security": "reality",
  "realitySettings": { "target": "www.example-donor.com:443", "serverNames": ["www.example-donor.com"], "privateKey": "<x25519-private>", "shortIds": ["<hex8>"] },
  "xhttpSettings": { "path": "/<random-path>", "mode": "auto" }
}
```

Клиенты для XHTTP — **без** `flow`.

## Клиент (Xray JSON, outbound)

```json
{
  "protocol": "vless",
  "tag": "proxy",
  "settings": { "vnext": [{ "address": "<server-ip-or-host>", "port": 443,
    "users": [{ "id": "<uuid>", "flow": "xtls-rprx-vision", "encryption": "none" }] }] },
  "streamSettings": {
    "network": "raw",
    "security": "reality",
    "realitySettings": {
      "serverName": "www.example-donor.com",
      "fingerprint": "chrome",
      "password": "<x25519-public>",
      "shortId": "<hex8>",
      "spiderX": "/"
    }
  }
}
```

На старых клиентах ключ называется `publicKey` (в новых — `password`, старое имя принимается).

## Ссылка `vless://`

```
vless://<uuid>@<host>:443?type=tcp&security=reality&pbk=<x25519-public>&fp=chrome&sni=www.example-donor.com&sid=<hex8>&flow=xtls-rprx-vision&spx=%2F#name
```

XHTTP: `type=xhttp&path=%2F<path>&mode=auto`, без `flow`. ML-DSA: `pqv=<verify>`.
Ссылка — секрет (несёт UUID): не публиковать.

## systemd

```bash
xray run -test -c /usr/local/etc/xray/config.json
sudo systemctl restart xray && systemctl status xray --no-pager
journalctl -u xray -n 50 --no-pager
ss -tlnp | grep ':443'
```

## Выбор донора (`target`)

Официальные требования (`XTLS/REALITY` README, docs `reality.md`):
- минимум: зарубежный сайт, **TLSv1.3 + H2**, домен без редиректа (основной домен часто редиректит на `www`);
- плюсы: IP рядом с сервером, шифрование сообщений после Server Hello (пример — `dl.google.com`), OCSP Stapling;
- `serverNames` — имена, которые принимает target (обычно тот же домен / SAN его сертификата);
- для `mldsa65Seed` цепочка сертификатов target должна быть > 3500 байт;
- неаутентифицированный трафик проксируется на target: при CDN-доноре сервер становится открытым форвардом — ограничь `limitFallbackUpload/Download`.
- Ядро предупреждает (v26.10.10, `transport_security.go`), если `serverNames` оканчивается на `.ru/.ir/.cn` или содержит `apple`, `icloud`, `microsoft`: «increase the likelihood of your server's IP being blocked by the GFW». Предупреждение ориентировано на GFW; для РФ решай по своей сети.

Проверка с VPS и клиента: `xray tls ping <donor>` (показывает TLS-версию, поддержку X25519MLKEM768 и длину сертификата).

## Важные ограничения ядра (v26.10.10)

- REALITY только поверх RAW, XHTTP, gRPC.
- VLESS/Trojan без TLS/REALITY/VLESS Encryption на публичный адрес запрещены (с v26.7.11).
- `allowInsecure` удалён → `pinnedPeerCertSha256` / `verifyPeerCertByName`.
- `xray x25519` печатает `PrivateKey`, `Password (PublicKey)`, `Hash32`; клиент принимает `password` (алиас `publicKey`).
- `fingerprint` `unsafe`/`hellogolang` отклоняются REALITY.
