# nftables, NAT, conntrack

На современных дистрибутивах iptables часто backend `iptables-nft`.
Смотри факт:

```bash
iptables -V
nft list tables
```

Не пиши параллельно iptables-legacy и nft на одни и те же hooks.

## Forward + masquerade (VPN egress)

```bash
sysctl -w net.ipv4.ip_forward=1
```

`/etc/sysctl.d/99-forward.conf`:

```
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=2
net.ipv4.conf.default.rp_filter=2
```

`rp_filter=1` (strict) ломает asymmetric PBR. Для policy routing ставь `2`
(loose) или per-iface.

Минимальный nft:

```
table inet nat {
  chain postrouting {
    type nat hook postrouting priority srcnat;
    oifname "eth0" ip saddr 10.8.1.0/24 masquerade
  }
}

table inet filter {
  chain forward {
    type filter hook forward priority filter;
    ct state established,related accept
    iifname "awg0" oifname "eth0" accept
    iifname "eth0" oifname "awg0" ct state established,related accept
  }
}
```

Применить:

```bash
nft -f /etc/nftables.conf
systemctl enable --now nftables
nft list ruleset
```

## DNAT / port forward

```
table inet nat {
  chain prerouting {
    type nat hook prerouting priority dstnat;
    iifname "eth0" tcp dport 443 dnat to 10.8.1.2:443
  }
}
```

Forward chain должен пустить `eth0 → awg0` на этот порт, не только NAT.

## conntrack

```bash
conntrack -L | head
conntrack -L -p udp --dport 443
dmesg | grep -i 'nf_conntrack: table full'
sysctl net.netfilter.nf_conntrack_max net.netfilter.nf_conntrack_count
```

UDP VPN без keepalive выглядит как «отвалился через NAT timeout».
Лечи `PersistentKeepalive` на пире за NAT, не бесконечным timeout.

## Docker и nft

Docker пишет свои iptables/nft chains (`DOCKER`, `DOCKER-USER`).
Порт `0.0.0.0:80` в compose ≠ маршрут VPN.

Если VPN-forward сломался после `docker restart` — Docker пересобрал
filter/nat. Свои правила клади в `DOCKER-USER` (iptables) или отдельную
nft table с понятным priority, не в `DOCKER`.

## Диагностика «пакет ушёл и не вернулся»

```bash
ip route get 1.1.1.1 from 10.8.1.2 iif awg0
tcpdump -ni awg0 icmp
tcpdump -ni eth0 icmp
nft monitor trace
```

Trace (временно):

```
nft add rule inet filter forward meta nftrace set 1
nft monitor trace
```

Сними trace сразу после теста.

Чеклист:

1. `ip_forward=1`
2. reverse path: `rp_filter`
3. NAT на правильном `oifname`
4. firewall forward
5. AllowedIPs пира содержит исходный префикс
6. MSS/MTU: `nft ... tcp flags syn tcp option maxseg size set 1360`

## MTU

AWG/WG + интернет часто режет TCP на 1420+. Симптом: ping есть, HTTPS висит.

```bash
ip link show awg0
ping -M do -s 1372 10.8.1.1
```

Clamp MSS в forward, либо `MTU = 1280` на интерфейсе.
