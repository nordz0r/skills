# Свой VPN: выбор протокола, развёртывание, проверка

## Выбор

| Ситуация | Что ставить |
|---|---|
| UDP проходит, нужен полный туннель, роутеры/телефоны | AmneziaWG (`awg-protocol.md`) |
| UDP режут, активное зондирование, белые списки SNI | Xray VLESS + REALITY (`xray-server.md`) |
| Нужен CDN / HTTP-форма трафика | Xray VLESS + XHTTP (`xray-xhttp-finalmask.md`) |
| Весь дом через роутер | OpenWrt: `amneziawg-openwrt-guide`, `podkop-openwrt-guide` |
| Блок по IP/ASN | обфускация не поможет — менять IP/хостинг |

AWG (UDP) + Xray (443/TCP) на одном VPS — нормальная схема с резервом.

Источники: `awg-protocol.md`, `linux-awg.md`, `xray-*.md` этого скилла (сверка 2026-10-15), `amneziawg-tools` (`wg-quick/linux.bash`), Xray-core v26.10.10.

## 0. VPS

```bash
apt update && apt -y upgrade
timedatectl set-ntp true && timedatectl          # часы важны для REALITY/WireGuard
sysctl -w net.ipv4.ip_forward=1                  # для AWG (закрепи в /etc/sysctl.d/)
ufw allow 22/tcp; ufw allow 443/tcp; ufw allow <awg-port>/udp; ufw enable
```

## 1. Сервер

- Через приложение Amnezia VPN (Docker-стек) → `docker-stack.md`.
- Голый AWG (`awg-quick`, NAT, systemd) → `linux-awg.md`; параметры → `awg-protocol.md`.
- Голый Xray-core → `xray-server.md` (`xray run -test -c config.json` → `systemctl restart xray`).

## 2. Клиенты и минимальные версии

Сверено 2026-10-15 по GitHub releases. AWG — версии с поддержкой нужной версии протокола
(подробно — `amnezia-vpn/references/awg-protocol.md`); Xray-клиенты должны нести ядро не старее фич сервера.

| Клиент | Протокол | Минимум / актуальная |
|---|---|---|
| Amnezia VPN (все ОС) | AWG 1.5 / 2.0 / 3.0 / 3.1, Xray | 4.8.8.3 / 4.8.12.7 / 5.0.0.2 / 5.0.1.5; актуальная 5.0.3.0 |
| AmneziaWG Android | AWG 2.0 / 3.1 | 2.0.0 / v3.1.20260814 |
| AmneziaWG Windows | AWG 1.5–2.0 / 3.1 | 2.0.0 (H > 2³¹−1 — с 2.0.2) / 3.1.0 |
| AmneziaWG iOS/macOS | AWG | релизов на GitHub нет — App Store |
| Linux `awg-quick` | AWG 3.1 | amneziawg-tools v3.1.20260812 + kmod v3.1.20260906 или amneziawg-go v3.1.20260828 |
| OpenWrt | AWG | `amneziawg-openwrt-guide` |
| v2rayN (Win/Linux/macOS) | Xray | 7.25.6 (2026-10-11) |
| v2rayNG (Android) | Xray | 2.2.6 (2026-07-05) — проверь версию встроенного ядра |
| sing-box / mihomo / Hiddify | VLESS+REALITY (XHTTP/FinalMask — смотри поддержку в их docs) | mihomo v1.19.32; Hiddify v4.1.1 (2026-03) |

Сторонние клиенты (WireSock, wg-easy, Keenetic и т.п.) не сверялись — проверяй поддержку I1–I5/AWG 2.0+ по их документации.

## 3. Проверка

```bash
# AWG
awg show                       # latest handshake < 2–3 мин, transfer растёт
ping -c3 10.8.1.1              # из клиента
# Xray
curl -x socks5h://127.0.0.1:10808 https://ifconfig.me
# общее (из клиента)
curl -4 https://ifconfig.me    # IP = VPS при full tunnel
resolvectl query example.com   # нет DNS-утечки к провайдеру
ping -M do -s 1252 <tunnel-gw> # проверка MTU 1280 (Linux)
```

## 4. Траблшутинг по симптомам

| Симптом | Куда смотреть |
|---|---|
| AWG: `Invalid argument` при подъёме | ключи версии новее устройства, S<12 при HPK, пересечение H |
| AWG: нет handshake | несовпадение H/S/HPK; UDP-порт закрыт/режется; `Endpoint`; часы |
| AWG: handshake есть, трафика нет | `ip_forward`, NAT/MASQUERADE, `AllowedIPs`, DNS |
| AWG: тяжёлые сайты висят | уменьшить MTU (Amnezia: 1376 десктоп / 1280 мобильные) |
| AWG: долго подключается | уменьшить `Jc`, `Jmax` |
| Xray: не подключается | `password/publicKey`, `shortId`, `serverName`∈`serverNames`, `flow`, часы, `journalctl -u xray` |
| Работало и перестало | блок сигнатуры (сменить I1/параметры AWG или донора Xray) либо блок IP (сменить IP) |
| Сервер доступен только с части сетей | блок по IP/ASN у провайдера; обфускация не поможет |

Логи и конфиги в тикетах/чатах — только с замаскированными ключами.
