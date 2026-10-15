# Xray: установка, сервер, клиент

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

- TLS 1.3 + HTTP/2 (`curl -sI --http2 --tlsv1.3 https://donor` с VPS), сертификат публичного CA.
- `serverNames` покрываются сертификатом донора (тот же домен или SAN).
- Не свой домен, не за Cloudflare-«редиректами», не гигант, которым пользуются все (microsoft.com/apple.com) — и не экзотика в другом полушарии.
- Проверка с клиента: `xray tls ping www.example-donor.com`.
