# Форматы ключей: `vpn://` (Amnezia) и `vless://`

Сверено 2026-10-15: `amnezia-client` 5.0.3.0 (`exportController.cpp`, `apiUtils.cpp`), Xray-core discussion #716, release notes v25.7.26 / v26.3.27.

## `vpn://` ✅

- `vpn://` + base64url( `qCompress`( JSON ) ); `qCompress` = 4 байта длины (big-endian) + zlib. Не шифрование — любой распакует.
- Декодирование для проверки (локально, без сети):
  ```python
  import base64, zlib, json
  s = key.removeprefix("vpn://"); b = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
  print(json.dumps(json.loads(zlib.decompress(b[4:])), indent=2))
  ```
- Внутри: `hostName`, `dns1/dns2`, `description`, `defaultContainer`, `containers[]` (по контейнеру на протокол: `amnezia-awg`, `amnezia-xray`, …), в контейнере — параметры протокола и `last_config` (строка-JSON с готовым клиентским конфигом).
- Правка: изменить параметры **и** в контейнере, **и** в `last_config`, затем упаковать обратно тем же способом.
- Менять без сервера можно только sender-параметры AWG (Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition) — остальное синхронно с сервером.
- Подписочные ключи сервиса Amnezia (Premium/API) туннеля не содержат ❔ (формат не разбирался).

## `vless://` ✅

```
vless://<uuid>@<host>:443?type=tcp&security=reality&pbk=<x25519-public>&fp=chrome&sni=www.example-donor.com&sid=<hex8>&flow=xtls-rprx-vision&spx=%2F#name
```

| Параметр | Поле JSON клиента |
|---|---|
| `type` (`tcp`=raw, `xhttp`, `grpc`, …) | `streamSettings.network` |
| `security` (`reality`/`tls`/`none`) | `streamSettings.security` |
| `pbk` | `realitySettings.password` (алиас `publicKey`) |
| `sni`, `fp`, `sid`, `spx` | `serverName`, `fingerprint`, `shortId`, `spiderX` |
| `flow` | `users[].flow` |
| `encryption` | `users[].encryption` (VLESS Encryption или `none`) |
| `path`, `host`, `mode`, `extra` | `xhttpSettings` (`extra` — JSON-объект, url-encoded) |
| `pqv` | `mldsa65Verify` (v25.7.26+) |
| `fm` | FinalMask (v26.3.27+) |

- IPv6 — в `[...]`; значения url-encoded.
- XHTTP: `type=xhttp&path=%2F<path>&mode=auto`, без `flow`.
- Ссылка — секрет (несёт UUID). `pbk` публичный.
