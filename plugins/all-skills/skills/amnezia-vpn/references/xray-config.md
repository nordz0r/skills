# Xray: оптимальная конфигурация сервера и клиента

Источник: `XTLS/Xray-core` v26.10.10 (`infra/conf/vless.go`, `transport_security.go`, `transport_internet.go`,
`transport/internet/tls/tls.go`), docs xtls.github.io (`reality.md`), `XTLS/REALITY` README, `Xray-examples`.
Сверено 2026-10-15. Метки: **[код]**, **[docs]**, **[рекомендация]** (вывод из них).

## Порядок выбора

1. **Транспорт + безопасность**
   | Условие | Выбор |
   |---|---|
   | Прямой доступ к IP сервера, TCP/443 открыт | **RAW + REALITY + Vision** (лучшая скорость, дефолт) |
   | Нужен CDN / только HTTP-путь / RAW режется по поведению | **XHTTP + REALITY** (без CDN) или **XHTTP + TLS** со своим доменом за CDN |
   | UDP проходит, нужна скорость на плохих каналах | Hysteria 2 (v26.1.23+, `xray-xhttp-finalmask.md`) |
   | Нужна постквантовая защита payload | + VLESS Encryption (ниже) |
   | gRPC / ws / httpupgrade | только для старых клиентов — deprecated **[код]** |
2. **flow**: `xtls-rprx-vision` — только RAW + TLS/REALITY; для XHTTP — пусто **[код: «XTLS only supports TLS and REALITY directly»]**.
   На сервере допустимы только `""` и `xtls-rprx-vision`; `xtls-rprx-vision-udp443` — только у клиента (пропускает UDP/443, иначе он блокируется ради перехода браузера на TCP) **[код]**.
3. **Донор REALITY** (ниже).
4. **fingerprint**: `chrome` (самый массовый) **[рекомендация]**; допустимо `firefox, safari, ios, android, edge, 360, qq, random, randomized` **[код tls.go]**; `unsafe`/`hellogolang` REALITY отклоняет **[код]**.
5. **Sniffing/routing** (ниже).
6. Прогнать `config-checklist.md`; версии клиентов — `versions-compat.md`.

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

Shared-поля сервера и клиента: `id` (UUID), `flow`, публичный ключ ↔ `privateKey`, `shortId` ∈ `shortIds`, `serverName` ∈ `serverNames`, `path`/`mode` XHTTP.
Пустой `""` в `shortIds` разрешает клиентов без shortId — оставляй только если нужно.
Новое в v26.x: дефолтный `flow` можно задать на уровне `settings.flow` inbound'а **[код vless.go]**.

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

Формат ссылки `vless://` — `key-formats.md`.

## Выбор донора (`target`)

Официальные требования (`XTLS/REALITY` README, docs `reality.md`):
- минимум: зарубежный сайт, **TLSv1.3 + H2**, домен без редиректа (основной домен часто редиректит на `www`);
- плюсы: IP рядом с сервером, шифрование сообщений после Server Hello (пример — `dl.google.com`), OCSP Stapling;
- `serverNames` — имена, которые принимает target (обычно тот же домен / SAN его сертификата);
- для `mldsa65Seed` цепочка сертификатов target должна быть > 3500 байт;
- неаутентифицированный трафик проксируется на target: при CDN-доноре сервер становится открытым форвардом — ограничь `limitFallbackUpload/Download`.
- Ядро предупреждает (v26.10.10, `transport_security.go`), если `serverNames` оканчивается на `.ru/.ir/.cn` или содержит `apple`, `icloud`, `microsoft`: «increase the likelihood of your server's IP being blocked by the GFW». Предупреждение ориентировано на GFW; для РФ решай по своей сети.

Проверка с сервера и из сети клиента: `xray tls ping <donor>` (показывает TLS-версию, поддержку X25519MLKEM768 и длину сертификата).

## Важные ограничения ядра (v26.10.10)

- REALITY только поверх RAW, XHTTP, gRPC.
- VLESS/Trojan без TLS/REALITY/VLESS Encryption на публичный адрес запрещены (с v26.7.11).
- `xray x25519` печатает `PrivateKey`, `Password (PublicKey)`, `Hash32`; клиент принимает `password` (алиас `publicKey`).
- `fingerprint` `unsafe`/`hellogolang` отклоняются REALITY.
- `minClientVer` / `maxClientVer` / `maxTimeDiff` на сервере — жёсткий отсев старых клиентов; явно задавай, только если все клиенты свежие.
- `allowInsecure` удалён → для TLS со своим сертификатом `pinnedPeerCertSha256` / `verifyPeerCertByName` **[код]**.
- Незнакомые поля JSON молча игнорируются **[код]** — опечатка в ключе не даёт ошибки, проверяй имена.

## VLESS Encryption (v25.8.29+)

Постквантовый слой VLESS поверх любого транспорта (можно и без TLS) **[release notes, код vless.go]**.
Пары генерирует `xray vlessenc`: печатает два варианта — **X25519** и **ML-KEM-768** (PQ) аутентификации; не смешивать.

```
server  "decryption": "mlkem768x25519plus.native.600s.<server-key>"
client  "encryption": "mlkem768x25519plus.native.0rtt.<client-key>"
```

- 2-е поле: `native` | `xorpub` | `random` (внешний вид: `random` — полностью случайные байты) **[код]**.
- 3-е поле: на сервере — время жизни тикета 0-RTT (`600s` или диапазон `from-tos`); на клиенте — `1rtt` | `0rtt`.
- Между ним и ключом можно вставить блоки паддинга (формат — release notes v25.9.5).
- Без Encryption: `"decryption": "none"` / `"encryption": "none"` (как в шаблонах).
- **[рекомендация]** С REALITY не обязательна; полезна для XHTTP через CDN (CDN видит только шифротекст) и когда нужна PQ-защита.

## Sniffing и routing

- Сервер: `sniffing` с `destOverride: ["http","tls","quic"]` + `"routeOnly": true` — домены доступны правилам, но соединение идёт на исходный IP (не ломает DNS-разрешение клиента) **[docs]**.
- Блокируй `geoip:private` (иначе сервер открывает локальную сеть VPS) и, по желанию, `bittorrent`.
- Клиент (split-tunnel): `"domainStrategy": "IPIfNonMatch"`, правила `geosite:<страна>`/`geoip:<страна>` → `direct`, остальное → `proxy`; DNS-запросы к своим резолверам направляй тем же правилом.
- `geosite`/`geoip`-файлы должны быть в каталоге ресурсов ядра (`geosite.dat`, `geoip.dat`); имена категорий — по используемой сборке.
