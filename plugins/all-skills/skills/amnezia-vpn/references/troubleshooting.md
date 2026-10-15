# Траблшутинг конфигурации (AWG и Xray)

Сверено 2026-10-15: amneziawg-go v3.1.20260828 (`uapi.go`, `receive.go`), kmod v3.1.20260906 (`netlink.c`, `junk.c`),
Xray-core v26.10.10 (`infra/conf/*.go`, `proxy/vless/*`). Только ошибки конфига; сеть/хостинг — вне скилла.

Проверка синтаксиса без запуска туннеля: `xray run -test -c config.json`; для AWG — `config-checklist.md`.

## AWG

| Симптом | Причина в конфиге |
|---|---|
| `Invalid argument` при подъёме | ключ версии новее движка; S1–S4 < 12 при `HeaderProtectionKey`; пересечение H; незнакомый тег I **[код]** |
| нет handshake | не совпали H1–H4 / S1–S4 / `HeaderProtectionKey` / `RandomTrailers`; `Endpoint` ≠ `ListenPort`; ключи пиров перепутаны |
| handshake есть, трафика нет | `AllowedIPs` (клиент/сервер), `Address` вне подсети, DNS |
| тяжёлые сайты висят | MTU: 1280 (мобильные) / 1376 (десктоп) |
| долгое подключение | меньше `Jc`, `Jmax`, короче I1–I5 |
| `Message too long` на kmod | длинная цепочка I1–I5 (`-EMSGSIZE`) **[код]** |
| периодические обрывы на 3.x | диапазоны таймеров (`RejectAfterTime` > `RekeyAfterTime`) |
| сменили сервер — отвалились все | shared-параметры: сначала раздать новые клиентские конфиги |
| работало и перестало | блок сигнатуры → сменить I1/H/S; блок IP — конфигом не лечится |

## Xray

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


Логи — временно `"loglevel": "debug"`; в тикеты только с замаскированными UUID/ключами/IP.
