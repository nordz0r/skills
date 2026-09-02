# AmneziaVPN Docker-стек на VPS

Официальный клиент ставит сервер через SSH: Docker + контейнеры +
`/opt/amnezia`. Не воспроизводи установщик «из головы», если есть живой
стек — сначала сними факты.

## Снять состояние

```bash
docker ps -a --filter name=amnezia --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}'
ls -la /opt/amnezia
ss -lntup | grep -E '443|1194|8443|51820'
df -h /opt /var/lib/docker
```

Имена контейнеров зависят от версии приложения и выбранных протоколов
(`amnezia-awg`, `amnezia-wireguard`, `amnezia-xray`, `amnezia-openvpn`,
`amnezia-dns`, и т.п.). Смотри фактический `docker ps`, не словарь.

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

Amnezia часто просит UDP 443 (или выбранный порт). Если на хосте уже есть
HTTPS/QUIC — конфликт. Проверяй `ss -ulnp` и `ss -lntup` до смены порта.

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
3. После обновления сверь AWG generation: старые клиенты могут не поднять
   туннель к новому серверу.

```bash
tar -C /opt -czf /root/amnezia-backup-$(date +%F).tgz amnezia
```

Архив с ключами — только на сервере/секретных носителях, не в wiki.

## Когда не трогать Docker-стек

- Нужен только kernel AWG без GUI — `linux-awg.md`.
- Роутер OpenWrt — `amneziawg-openwrt-guide`.
- «Починить Docker вообще» — `docker-ops`.
