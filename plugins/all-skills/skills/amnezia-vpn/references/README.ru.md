# Amnezia VPN, AmneziaWG и Xray (Linux / Docker) — по-русски

Единственный скилл по своему VPN на Linux-сервере: Docker-стек приложения Amnezia,
голый AmneziaWG, голый Xray-core, клиенты, проверка, FAQ.
OpenWrt — `amneziawg-openwrt-guide` / `podkop-openwrt-guide`; policy routing — `linux-routing`.

## Порядок

1. Выбор протокола и план — `vpn-setup.md`.
2. Сервер: приложение Amnezia → `docker-stack.md`; голый AWG → `linux-awg.md`; голый Xray → `xray-server.md`.
3. Параметры: `awg-protocol.md`, `xray-versions.md`, `xray-xhttp-finalmask.md`.
4. Клиенты и минимальные версии, проверка, траблшутинг — `vpn-setup.md`, `xray-troubleshooting.md`.
5. Вопросы-ответы — `faq.md` (перенос FAQ architect.vai-rice.space со статусами проверки).

Ключи, PSK, HeaderProtectionKey, UUID, ссылки `vpn://`/`vless://` — только плейсхолдеры.

Сверка 2026-10-15: amneziawg-go v3.1.20260828, kmod v3.1.20260906, amneziawg-tools v3.1.20260812,
amnezia-client 5.0.3.0, Xray-core v26.10.10.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amnezia amneziavpn amneziawg awg-quick awg0 opt/amnezia docker vpn jc jmin jmax handshake amneziawg-go vps xray vless reality xhttp
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
