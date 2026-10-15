# Xray-core: фичи по версиям

Сверено с release notes `XTLS/Xray-core` (последний релиз на 2026-10-15 — **v26.10.10**).
Сервер обновляй не реже клиента: новые клиенты могут не подключаться к старым серверам.

| Версия | Изменение |
|---|---|
| v24.10.31 | REALITY `dest` → `target` (старое имя принимается) |
| v24.11.11 | XHTTP `stream-up` |
| v24.11.30 | XHTTP `stream-one`; клиент REALITY по умолчанию `stream-one` |
| v25.4.30 | XHTTP + TLS по умолчанию `packet-up`, + REALITY — `stream-one` |
| v25.5.16 | REALITY: X25519MLKEM768 автоматически, если target поддерживает |
| v25.7.26 | REALITY: **опциональная** ML-DSA-65 (`mldsa65Seed` / `mldsa65Verify`, `pqv` в ссылке); target с цепочкой сертификатов 3500+ байт |
| v25.8.29 (notes в v25.9.5) | VLESS Encryption: ML-KEM-768 PFS 1-RTT/0-RTT (`mlkem768x25519plus…`, `xray vlessenc`); v25.9.11 — VLESS Reverse Proxy |
| v25.12.8 | удалена устаревшая опция роутинга `UseIP` |
| v26.1.23 | TUN inbound (Win/Linux/Android), Hysteria 2 outbound+транспорт, Salamander |
| v26.2.6 | XHTTP: новые опции против детекта через CDN; FinalMask: XICMP, XDNS, header-*, mkcp-* |
| v26.3.27 | FinalMask: header-custom, sudoku, fragment/noise; Hysteria/XHTTP/REALITY правки |
| v26.6.22+ | переименования `session*` → `sessionID*` в XHTTP (по разбору исходников) |

`minClientVer` (REALITY): в текущем `main` дефолт `26.3.27` **закомментирован** —
без явного значения ограничения нет. Не выставляй без нужды: по комментарию в ядре это повышает риск блокировки IP.

Проверка версии: `xray version`; перед апгрейдом читай release notes — breaking-изменения там помечаются явно.
