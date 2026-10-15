# Xray: проверка и траблшутинг

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
| клиент «подключён», но трафика нет, в логе сервера `REALITY: processed invalid connection` | неверный `password/publicKey`, `shortId`, `serverName` не из `serverNames`, расхождение часов (>`maxTimeDiff`) |
| `flow` ошибка / клиент отклонён | flow не совпадает; `-udp443` на сервере; Vision поверх XHTTP или без TLS |
| `unknown transport protocol` | ядро старее транспорта (hysteria, xhttp) |
| XHTTP 404 | не совпали `path`/`host` или режим/размещения паддинга |
| работает, потом IP заблокирован | популярный/«палевный» донор, высокий трафик на один IP, свой домен в SNI; смени донора/IP, рассмотри XHTTP через CDN |
| медленно/рвётся на мобильном | MTU/фрагментация не при чём (TCP) — проверь `fingerprint`, попробуй XHTTP `packet-up` |

Логи: `"log": {"loglevel": "debug"}` временно; не публикуй логи с UUID/IP клиентов.
