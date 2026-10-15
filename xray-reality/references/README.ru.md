# Xray (VLESS + REALITY / XHTTP) — кратко по-русски

Скилл для развёртывания Xray-core на VPS и сборки клиентских профилей.

- Базовый стек: VLESS + REALITY + RAW + `xtls-rprx-vision` на 443/TCP.
- Альтернатива: VLESS + REALITY/TLS + XHTTP (без `flow`), в т.ч. через CDN.
- Секреты генерируй на сервере (`xray uuid`, `xray x25519`, `openssl rand -hex 8`), в доки и чаты — только плейсхолдеры.
- Донор (`target` + `serverNames`): TLS 1.3 + H2, сертификат покрывает SNI, доступен с VPS.
- Проверка: `xray run -test`, `journalctl -u xray`, `curl -x socks5h://…`.

Файлы: `server-config.md`, `xhttp-finalmask.md`, `versions.md`, `troubleshooting.md`.
Смежные скиллы: `amnezia-vpn`, `vpn-setup`, `podkop-openwrt-guide`, `linux-routing`.
