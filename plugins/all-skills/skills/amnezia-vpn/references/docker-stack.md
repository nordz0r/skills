# AmneziaVPN Docker-стек на VPS

Сверено 2026-10-15 по `amnezia-client` 5.0.3.0: `client/core/utils/containerEnum.h`,
`containers/containerUtils.cpp`, `constants/protocolConstants.h`.

Официальный клиент ставит сервер через SSH: Docker + контейнеры +
`/opt/amnezia`. Не воспроизводи установщик «из головы», если есть живой
стек — сначала сними факты.

## Снять состояние

```bash
docker ps -a --filter name=amnezia --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}'
ls -la /opt/amnezia
ss -lntup | grep -E '443|1194|6789|51820|55424'
df -h /opt /var/lib/docker
```

Имя контейнера = `amnezia-` + протокол в нижнем регистре; исключения: `amnezia-awg`
(AWG legacy), `amnezia-awg2` (AWG 2.0+), `amnezia-openvpn-cloak`. Прочие:
`amnezia-wireguard`, `amnezia-openvpn`, `amnezia-shadowsocks`, `amnezia-ipsec`,
`amnezia-xray`, `amnezia-ssxray`, `amnezia-dns`, `amnezia-sftp`, `amnezia-socks5proxy` и др.
Всё равно смотри фактический `docker ps`.

| Протокол | Порт по умолчанию | Конфиг на сервере |
|---|---|---|
| AWG | 55424/udp | `/opt/amnezia/awg/awg0.conf` (legacy: `wg0.conf`) |
| WireGuard | 51820/udp | `/opt/amnezia/wireguard/wg0.conf` |
| Xray (VLESS+REALITY) | 443/tcp | `/opt/amnezia/xray/server.json` (+ `xray_uuid.key`, `xray_private.key`, `xray_public.key`, `xray_short_id.key`) |
| OpenVPN | 1194 | `/opt/amnezia/openvpn/server.conf` |

`amnezia-client` 5.0.3.0 ожидает на сервере Xray-core **v26.7.28** (`expectedServerXrayRelease`).
Параметры AWG и дефолты приложения — `awg-protocol.md`; правила Xray — `xray-server.md`.
AWG 2.0 на self-hosted: по release notes 4.8.12.9 контейнер ставится отдельно.

Логи:

```bash
docker logs --tail 200 CONTAINER
```

Конфиги и ключи лежат под `/opt/amnezia`. Не копируй их в git и в ответы.

## Типовые поломки

| Симптом | Куда смотреть |
|---------|----------------|
| Контейнер Restarting | `docker logs`, неверный device/tun, нет `/dev/net/tun` |
| Нет handshake AWG | UDP порт не опубликован, nft/ufw, params клиента |
| Docker не стартует | диск, `iptables`/`nft` backend, `overlay2` |
| После reboot стек мёртв | docker не enable, live-restore, unit conflict |
| Клиент «подключился», сайты нет | DNS контейнера, IP forward, NAT, mtusize |

TUN:

```bash
ls -l /dev/net/tun
# в compose/run обычно:
# cap_add: [NET_ADMIN, SYS_MODULE]
# devices: [/dev/net/tun]
```

Без `NET_ADMIN` userspace/kernel VPN-контейнер не поднимет интерфейс.

## Сеть хоста

AWG по умолчанию — UDP 55424, Xray — TCP 443. Если на хосте уже есть
HTTPS на 443 — конфликт с Xray. Проверяй `ss -ulnp` и `ss -lntup` до смены порта.

Firewall:

```bash
ufw status verbose
firewall-cmd --list-all
nft list ruleset | head
```

Открой только нужный UDP/TCP. Не `ufw disable`.

## Обновление

1. Backup `/opt/amnezia` и `docker compose`/`containers`.
2. Не обновляй Docker-стек вслепую поверх единственного прод-VPN.
3. После обновления сверь версию AWG/Xray: клиенты старше минимальных версий
   (`awg-protocol.md`, `vpn-setup.md`) не поднимут туннель к новому серверу.

```bash
tar -C /opt -czf /root/amnezia-backup-$(date +%F).tgz amnezia
```

Архив с ключами — только на сервере/секретных носителях, не в wiki.

## Когда не трогать Docker-стек

- Нужен только kernel AWG без GUI — `linux-awg.md`.
- Роутер OpenWrt — `amneziawg-openwrt-guide`.
- «Починить Docker вообще» — `docker-ops`.
