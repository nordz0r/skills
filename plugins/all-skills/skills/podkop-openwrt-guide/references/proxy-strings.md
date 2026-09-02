# Podkop: proxy URL-строки

Podkop принимает строковые proxy-конфиги и генерирует из них outbound в `sing-box`. Парсинг происходит в shell (`sing_box_config_facade.sh` → `helpers.sh`) и валидируется в frontend (`fe-app-podkop/src/validators/`).

Upstream reference: `String-example.md`.

## Поддерживаемые схемы

### SOCKS

```
socks4://host:port
socks4a://host:port
socks5://host:port
socks5://user:password@host:port
```

- SOCKS5 поддерживает аутентификацию user/password.
- `enable_udp_over_tcp=1` в секции включает UDP-over-TCP (v2) для SOCKS.

### Shadowsocks (ss)

```
ss://method:password@host:port
ss://base64_encoded@host:port
ss://base64_encoded@host:port?type=tcp|udp
```

- Поддерживается base64-encoded userinfo.
- Методы шифрования: `aes-256-gcm`, `chacha20-ietf-poly1305`, `2022-blake3-aes-128-gcm`, `2022-blake3-aes-256-gcm`, `2022-blake3-chacha20-poly1305`.
- `enable_udp_over_tcp=1` включает UDP-over-TCP.

### VLESS

```
vless://uuid@host:port?type=tcp&encryption=none&security=none
vless://uuid@host:port?type=ws&security=tls&sni=example.com&fp=chrome&path=/ws
vless://uuid@host:port?type=grpc&security=reality&pbk=...&sid=...&sni=...&fp=chrome&serviceName=grpc
```

Query-параметры:

| Параметр | Значения | Описание |
|----------|----------|----------|
| `type` | `tcp`, `kcp`, `ws`, `grpc`, `httpupgrade`, `xhttp` | Транспорт |
| `encryption` | `none` | Шифрование (всегда none для VLESS) |
| `security` | `none`, `tls`, `reality` | Тип безопасности |
| `sni` | домен | Server Name Indication |
| `fp` | `chrome`, `firefox`, `safari`, `edge`, `random` и др. | uTLS fingerprint |
| `alpn` | `h2`, `http/1.1`, `h2,http/1.1` | Протоколы ALPN |
| `pbk` | base64 | REALITY public key |
| `sid` | hex | REALITY short ID |
| `spx` | path | REALITY spider X |
| `flow` | `xtls-rprx-vision` | XTLS flow control |
| `allowInsecure` | `0`/`1` | Пропуск проверки сертификата |
| `ech` | `1` | Encrypted Client Hello |
| `path` | `/path` | Путь для ws/httpupgrade/xhttp |
| `host` | домен | Host header для ws/httpupgrade |
| `headerType` | `none`, `http` | Тип заголовка для kcp |
| `seed` | string | Seed для kcp obfuscation |
| `serviceName` | string | gRPC service name |
| `mode` | string | Режим xhttp |

### Trojan

```
trojan://password@host:port?security=tls&sni=example.com&fp=chrome
trojan://password@host:port?type=ws&security=tls&sni=...&path=/ws
trojan://password@host:port?security=reality&pbk=...&sid=...&sni=...&fp=chrome
```

Поддерживает те же транспорты и параметры безопасности, что и VLESS (кроме `flow` и `encryption`).

### Hysteria2 / Hy2

```
hysteria2://password@host:port
hysteria2://password@host:port?sni=example.com&obfs=salamander&obfs-password=secret
hy2://password@host:port?insecure=1
```

| Параметр | Описание |
|----------|----------|
| `sni` | Server Name Indication |
| `obfs` | Обфускация: `salamander` |
| `obfs-password` | Пароль обфускации |
| `insecure` | `0`/`1` — пропуск проверки сертификата |

## Где используются proxy-строки

- **Тип `url`**: одна proxy-строка в `proxy_string`.
- **Тип `selector`**: множество строк в `selector_proxy_links` — ручной выбор через Clash API.
- **Тип `urltest`**: множество строк в `urltest_proxy_links` — автоматический выбор по latency.
- **Тип `outbound`**: raw JSON, а не URL-строка.

## Практическое правило

Если задача про "почему Podkop не принимает строку", сверяй одновременно:

1. `String-example.md` — upstream reference формата.
2. Frontend validators (`fe-app-podkop/src/validators/`) — что проверяет UI.
3. Shell/backend обработку outbound (`sing_box_config_facade.sh`, `helpers.sh`) — как парсится.

Не предполагай, что любая Xray/V2Ray-строка автоматически совместима с Podkop. Формат пересекается, но не идентичен.
