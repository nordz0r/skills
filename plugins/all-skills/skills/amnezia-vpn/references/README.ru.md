# AmneziaWG и Xray: оптимальная конфигурация — по-русски

Только конфигурация: выбор параметров, серверные/клиентские конфиги, ключи, проверка.
Установка, Docker, systemd, подготовка VPS и запуск — вне скилла.

## Порядок действий агента

1. Собрать ограничения: движок и версия сервера, все клиенты и их версии, сеть (UDP, DPI, мобильная/CGNAT, CDN, блок IP).
2. Протокол: UDP проходит → AmneziaWG (`awg-config.md`); UDP режут/зондирование/белые SNI → Xray VLESS+REALITY+Vision (`xray-config.md`); нужен CDN → XHTTP (`xray-xhttp-finalmask.md`); оба — AWG основной, Xray на TCP/443 резерв.
3. Версия = минимальная общая у сервера и всех клиентов (`awg-protocol.md`, `versions-compat.md`).
4. AWG: shared-набор на сервер, sender-набор на устройство, MTU, рецепт сценария (`awg-config.md`).
5. Xray: транспорт → flow → донор → fingerprint → режим XHTTP → FinalMask / VLESS Encryption по необходимости → sniffing/routing.
6. Ключи `vpn://` / `vless://` — `key-formats.md`.
7. Проверка — `config-checklist.md`; ошибки — `troubleshooting.md`; вопросы — `faq.md`.
8. Ключи, PSK, HeaderProtectionKey, UUID, ссылки — только плейсхолдеры.

Порт AWG в примерах — 443/udp (дефолт приложения Amnezia — 55424).
Источники сверены 2026-10-15: amneziawg-go v3.1.20260828, kmod v3.1.20260906, amneziawg-tools v3.1.20260812, amnezia-client 5.0.3.0, Xray-core v26.10.10.

## Routing signals: amnezia amneziavpn amneziawg awg jc jmin jmax h1 s1 i1 headerprotectionkey randomtrailers mtu xray vless reality xhttp vision finalmask vlessenc x25519 shortids fingerprint vpn-key obfuscation dpi config
