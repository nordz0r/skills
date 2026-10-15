# Xray-core: фичи по версиям

Сверено 2026-10-15: релизы `XTLS/Xray-core` (последний **v26.10.10**, 2026-10-10),
`git log` ветки `main` (HEAD 0888beb, 2026-10-14), `core/core.go` = 26.10.10.
Где release notes ссылаются на следующий релиз, версия определена по дате коммита — помечено «(по коммиту)».

| Версия | Изменение | Источник |
|---|---|---|
| v24.10.31 | REALITY `dest` → `target` (алиасы) | release notes; docs `reality.md` |
| v24.11.11 | XHTTP `stream-up` | release notes |
| v24.11.30 | XHTTP `stream-one`; REALITY-клиент по умолчанию `stream-one` | release notes |
| v25.4.30 | XHTTP+TLS по умолчанию `packet-up`, +REALITY — `stream-one` | release notes |
| v25.5.16 | REALITY: X25519MLKEM768 автоматически, если target умеет | release notes |
| v25.7.26 | REALITY: **опциональная** подпись ML-DSA-65 (`mldsa65Seed`/`mldsa65Verify`, `pqv`); сертификат target > 3500 байт | release notes; docs |
| v25.8.29 (notes в v25.9.5) | VLESS Encryption (ML-KEM-768, `xray vlessenc`, `decryption`/`encryption`) | release notes |
| v25.9.11 | VLESS Reverse Proxy | release notes |
| v26.1.23 | TUN inbound; Hysteria 2 outbound + транспорт (`udphop`), Salamander | release notes |
| v26.2.6 | XHTTP: опции против детекта через CDN; FinalMask: XICMP, XDNS, header-\*, mkcp-\* | release notes |
| v26.3.27 | FinalMask: header-custom, sudoku, fragment, noise | release notes |
| v26.6.22 (по коммиту 2026-06-02) | удалены устаревшие поля TLS; `allowInsecure` → ошибка, замена `pinnedPeerCertSha256`/`verifyPeerCertByName` | `infra/conf/transport_security.go` |
| v26.7.11 (по коммиту 2026-07-07) | VLESS/Trojan без TLS/шифрования на публичный адрес **запрещены**; VMess/SS `none` удалены | коммит d7fa207 |
| v26.7.11 | REALITY-сервер: дефолт `minClientVer = 26.3.27` | коммит af7eb68 |
| v26.9.8+ (по коммиту 2026-09-08) | этот дефолт **закомментирован** — без явного значения ограничения нет | `transport_security.go` |
| v26.9.30 (по коммиту) | транспорт XDRIVE; MASQUE (CONNECT-IP) outbound/inbound/транспорт | `git log` |

Устаревшее/удалённое в ядре (`infra/conf/transport_internet.go`, v26.10.10):
- удалены: HTTP/h2/h3-транспорт → XHTTP stream-one; QUIC-транспорт → XHTTP H3; legacy XTLS → Vision;
- deprecated (работают с предупреждением): gRPC → XHTTP stream-up H2; WebSocket/HTTPUpgrade → XHTTP.

Правило: сервер не старше клиента; перед апгрейдом читай release notes.
