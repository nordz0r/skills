# Версии и совместимость

Сверено 2026-10-15: релизы `XTLS/Xray-core` (последний релиз **v26.10.10**, 2026-10-10 — **prerelease**; последний стабильный **v26.3.27**, 2026-03-27). Установка через `XTLS/Xray-install`: стабильный — по умолчанию, prerelease — `--beta`, конкретная версия — `--version v26.10.10` (флаги взаимоисключающие),
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

## Протокол AWG ↔ клиенты

Минимальные версии по версии протокола AWG и смысл версий — `awg-protocol.md` (единственный дом этой таблицы).

| Клиент | Протокол | Минимум / актуальная |
|---|---|---|
| Amnezia VPN (все ОС) | AWG 1.5 / 2.0 / 3.0 / 3.1, Xray | 4.8.8.3 / 4.8.12.7 / 5.0.0.2 / 5.0.1.5; актуальная 5.0.3.0 |
| AmneziaWG Android | AWG 2.0 / 3.1 | 2.0.0 / v3.1.20260814 |
| AmneziaWG Windows | AWG 1.5–2.0 / 3.1 | 2.0.0 (H > 2³¹−1 — с 2.0.2) / 3.1.0 |
| AmneziaWG iOS/macOS | AWG | релизов на GitHub нет — App Store |
| Linux `awg-quick` | AWG 3.1 | amneziawg-tools v3.1.20260812 + kmod v3.1.20260906 или amneziawg-go v3.1.20260828 |
| OpenWrt | AWG | пакет kmod-amneziawg той же версии, что tools |
| v2rayN (Win/Linux/macOS) | Xray | 7.25.6 (2026-10-11) |
| v2rayNG (Android) | Xray | 2.2.6 (2026-07-05) — проверь версию встроенного ядра |
| sing-box / mihomo / Hiddify | VLESS+REALITY (XHTTP/FinalMask — смотри поддержку в их docs) | mihomo v1.19.32; Hiddify v4.1.1 (2026-03) |

Сторонние клиенты (WireSock, wg-easy, Keenetic и т.п.) не сверялись — проверяй поддержку I1–I5/AWG 2.0+ по их документации.

Amnezia VPN 5.0.3.0 при настройке Xray ожидает на сервере Xray v26.7.28 (`protocolConstants.h`) ✅.
Конфиг собирай под минимальную версию ядра среди клиентов (незнакомые поля молча игнорируются).
