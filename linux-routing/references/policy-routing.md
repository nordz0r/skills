# Policy routing (ip rule / tables)

## Таблицы

Именованные таблицы в `/etc/iproute2/rt_tables`:

```
100 vpn
101 wan2
```

```bash
ip route show table main
ip route show table vpn
ip route add default dev awg0 table vpn
ip route add 10.0.0.0/8 via 10.0.0.1 table main
```

Не клади второй `default` в `main`, если хочешь предсказуемый PBR.
Второй default в той же таблице = dead race по metric.

## Rules

Порядок: меньший `pref` выигрывает. `from all lookup main` обычно pref 32766.

```bash
ip rule show
ip rule add pref 100 from 10.8.1.0/24 lookup vpn
ip rule add pref 110 fwmark 0x1 lookup vpn
ip rule add pref 200 to 192.168.10.0/24 lookup main
```

Проверка:

```bash
ip route get 1.1.1.1
ip route get 1.1.1.1 from 10.8.1.2
ip route get 1.1.1.1 mark 0x1
```

`route get` — главный инструмент. Если он показывает `dev eth0`, а ты ждал
`awg0`, правило не сработало (mark не выставлен / from не совпал).

## fwmark

Mark ставит nft/iptables в mangle, rule его читает.

```bash
nft add table inet mangle
nft add chain inet mangle prerouting '{ type filter hook prerouting priority mangle; }'
nft add rule inet mangle prerouting ip daddr 1.1.1.1 meta mark set 0x1
```

Для locally-generated трафика нужен `output` hook, не только prerouting:

```bash
nft add chain inet mangle output '{ type route hook output priority mangle; }'
nft add rule inet mangle output ip daddr 8.8.8.8 meta mark set 0x1
```

`type route` в output — чтобы kernel заново выбрал маршрут после mark.

## Split-tunnel VPN

Цель: `10.8.1.0/24` и выбранные префиксы в VPN, остальное в WAN.

```bash
ip route add 10.8.1.0/24 dev awg0 table main
ip route add 203.0.113.0/24 dev awg0 table main
# default остаётся через WAN
```

Полный туннель без blackhole:

```bash
ip route add default dev awg0 table vpn
ip rule add pref 110 fwmark 0x1 lookup vpn
# mark 0x1 на «весь TCP/UDP кроме LAN»
```

Не заворачивай endpoint VPN в туннель. Исключи `/32` сервера в `main`:

```bash
ip route add 198.51.100.10/32 via 192.0.2.1 dev eth0 table main
```

Иначе после `default via awg0` handshake умрёт.

## Multiple WAN

```bash
ip route add default via 192.0.2.1 dev eth0 table wan1
ip route add default via 198.51.100.1 dev eth1 table wan2
ip rule add pref 100 from 192.0.2.10 lookup wan1
ip rule add pref 101 from 198.51.100.10 lookup wan2
```

Исходящий source IP должен жить на том же uplink. Иначе ISP дропает.

## VRF (когда PBR уже мало)

```bash
ip link add vrf-vpn type vrf table 100
ip link set vrf-vpn up
ip link set awg0 master vrf-vpn
ip route add default dev awg0 vrf vrf-vpn
```

VRF изолирует стек сильнее fwmark. Не мешай VRF и mark на одном интерфейсе
без схемы.

## WG/AWG AllowedIPs

`AllowedIPs = 0.0.0.0/0` заставляет wg-quick/awg-quick сам поставить default
и часто `fwmark`. Смотри, что скрипт уже натворил:

```bash
ip rule show
ip route show table all | grep -E 'awg0|wg0'
```

Двойной PBR (скрипт + твои rules) — классика «интернет пропал».
Либо управляет `awg-quick`, либо ты, не оба.

## Persistence

- netplan `routes:` / `routing-policy:` на Ubuntu
- NetworkManager dispatcher
- `/etc/nftables.conf` + `nftables.service`
- кастомный oneshot unit, который вызывает проверенный скрипт

Не оставляй `ip rule add` только в SSH-сессии.
