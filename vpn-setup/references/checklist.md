# Чек-лист развёртывания и проверки VPN

## 0. VPS

```bash
apt update && apt -y upgrade
timedatectl set-ntp true && timedatectl          # часы важны для REALITY/WireGuard
sysctl -w net.ipv4.ip_forward=1                  # для AWG (закрепи в /etc/sysctl.d/)
ufw allow 22/tcp; ufw allow 443/tcp; ufw allow <awg-port>/udp; ufw enable
```

## 1. AmneziaWG сервер (Linux)

Детали — `amnezia-vpn` (`references/linux-awg.md`, `references/awg-protocol.md`).

```bash
awg genkey | tee server.key | awg pubkey > server.pub     # chmod 600 server.key
awg-quick up awg0 && awg show awg0
iptables -t nat -A POSTROUTING -s 10.8.1.0/24 -o <wan-if> -j MASQUERADE   # или nft
```

Клиенту — свой `[Peer]` на сервере (`AllowedIPs = 10.8.1.N/32`) и конфиг-зеркало
с теми же `S1–S4/H1–H4/HeaderProtectionKey`.

## 2. Xray сервер

Детали — `xray-reality`. `xray run -test -c config.json` → `systemctl restart xray`.

## 3. Клиенты

| Платформа | AWG | Xray |
|---|---|---|
| Android | AmneziaWG, Amnezia VPN, WG Tunnel | v2rayNG, Hiddify, NekoBox |
| iOS/macOS | AmneziaWG, Amnezia VPN | Streisand, v2rayTun, Hiddify |
| Windows | AmneziaWG, Amnezia VPN | v2rayN, Hiddify, Throne |
| Linux | `awg-quick` | `xray`, sing-box |
| OpenWrt | `amneziawg-openwrt-guide` | `podkop-openwrt-guide` (sing-box) |
| mihomo/Clash.Meta | outbound `amnezia-wg-option` (для AWG 3.x — `version: 3`) | vless outbound |

Перед выдачей конфига сверь версию протокола с клиентом (AWG 2.0/3.x поддерживают не все; WireSock игнорирует I1–I5).

## 4. Проверка

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

## 5. Траблшутинг по симптомам

| Симптом | Куда смотреть |
|---|---|
| AWG: `Invalid argument` при подъёме | ключи версии новее устройства, S<12 при HPK, пересечение H |
| AWG: нет handshake | несовпадение H/S/HPK; UDP-порт закрыт/режется; `Endpoint`; часы |
| AWG: handshake есть, трафика нет | `ip_forward`, NAT/MASQUERADE, `AllowedIPs`, DNS |
| AWG: тяжёлые сайты висят | MTU → 1280 |
| AWG: долго подключается | уменьшить `Jc`, `Jmax` |
| Xray: не подключается | `password/publicKey`, `shortId`, `serverName`∈`serverNames`, `flow`, часы, `journalctl -u xray` |
| Работало и перестало | блок сигнатуры (сменить I1/параметры AWG или донора Xray) либо блок IP (сменить IP) |
| Сервер доступен только с части сетей | блок по IP/ASN у провайдера; обфускация не поможет |

Логи и конфиги в тикетах/чатах — только с замаскированными ключами.
