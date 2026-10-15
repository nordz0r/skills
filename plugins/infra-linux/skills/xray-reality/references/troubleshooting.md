# Xray: проверка и траблшутинг

Сверено 2026-10-15 по Xray-core v26.10.10 (тексты ошибок — из `infra/conf/*.go`, `proxy/vless/*`).

## Сервер

```bash
xray run -test -c /usr/local/etc/xray/config.json   # синтаксис/семантика
systemctl status xray --no-pager; journalctl -u xray -n 100 --no-pager
ss -tlnp | grep :443                                # слушает ли
curl -sI --http2 --tlsv1.3 https://<donor>          # донор живой с VPS
```

## Клиент

```bash
xray run -c client.json        # локальный socks/http inbound, напр. 127.0.0.1:10808
curl -x socks5h://127.0.0.1:10808 -s https://ifconfig.me    # должен быть IP VPS
```

## Типовые ошибки

| Симптом | Причина |
|---|---|
| ядро не стартует: `invalid "privateKey"` | ключ не base64 RawURL 32 байта (взят Password вместо PrivateKey) |
| `empty "serverNames"` / `shortIds` | пустые списки на сервере |
| клиент «подключён», но трафика нет (сервер отдаёт сайт-донор) | неверный `password/publicKey`, `shortId`, `serverName` не из `serverNames`, расхождение часов (>`maxTimeDiff`) |
| `flow` ошибка / клиент отклонён | flow не совпадает; `-udp443` на сервере; Vision поверх XHTTP или без TLS |
| `Config: unknown transport protocol` | ядро старее транспорта (hysteria, xhttp, masque, xdrive) |
| `REALITY only supports RAW, XHTTP and gRPC for now.` | REALITY поверх ws/httpupgrade/kcp |
| `vless without TLS or other encryption is prohibited…` | v26.7.11+: VLESS без TLS/REALITY/Encryption на публичный адрес |
| `XTLS only supports TLS and REALITY directly for now.` | `flow` при XHTTP/без TLS |
| `unsupported mode` / `"headers" can't contain "host"` / `Can not use "downloadSettings" in "stream-one" mode.` | ошибки XHTTP-конфига |
| `allowInsecure` — removed feature | заменить на `pinnedPeerCertSha256` / `verifyPeerCertByName` |
| клиент старый, сервер v26.7.11–v26.7.28 отказывает | дефолт `minClientVer 26.3.27` в этих версиях; обнови клиент или сервер |
| XHTTP 404 | не совпали `path`/`host` или режим/размещения паддинга |
| работает, потом IP заблокирован | популярный/«палевный» донор, высокий трафик на один IP, свой домен в SNI; смени донора/IP, рассмотри XHTTP через CDN |

Логи: `"log": {"loglevel": "debug"}` временно; не публикуй логи с UUID/IP клиентов.
