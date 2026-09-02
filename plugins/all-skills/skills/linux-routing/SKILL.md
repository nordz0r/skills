---
name: linux-routing
description: >-
  Практическая IP-маршрутизация на Linux: ip route, ip rule, policy routing,
  fwmark, rt_tables, VRF, nftables/iptables NAT, masquerade, conntrack,
  rp_filter, split-tunnel, source-based routing, WireGuard/AWG AllowedIPs
  vs OS routes. Используй этот skill при задачах про linux routing, PBR,
  ip rule add, table 100, mark 0x1, nft nat postrouting, multiple WAN,
  default via VPN, трафик не возвращается. Не для OpenWrt podkop/UCI —
  там podkop-openwrt-guide. Триггеры: ip route, ip rule, policy routing,
  fwmark, nftables masquerade, conntrack, rp_filter, split tunnel, vrf,
  multiple default routes.
---

# Linux Routing

Skill про маршрутизацию и NAT на Linux-хосте (iproute2 + nftables).
Пиши команды `ip`/`nft`, которые можно вставить в консоль или unit.

Не используй для:

- OpenWrt + podkop/sing-box → `podkop-openwrt-guide`
- zapret DPI → `zapret-openwrt-guide`
- Docker bridge overlay как основной предмет → `docker-ops`
- Amnezia ключи/handshake → `amnezia-vpn`, сюда только OS-routes/NAT

## Когда использовать

- Два default route, VPN + WAN, split-tunnel.
- `ip rule`, таблицы, fwmark, source-based routing.
- NAT/masquerade, port forward, conntrack.
- Пакет уходит в VPN, ответ не возвращается; asymmetric routing.
- WireGuard/AWG `AllowedIPs` vs `ip route`.

## Workflow

1. Сними картину: `ip -br addr`, `ip route`, `ip rule`, `nft list ruleset`.
2. Отдели L3 (route/rule) от L4 NAT (nft) и от firewall drop.
3. Меняй одну таблицу/rule за раз. Не сноси default в main вслепую.
4. Проверяй `ip route get <dst> from <src> iif <if> mark <hex>`.
5. Persistence: `/etc/iproute2/rt_tables`, netplan/NM dispatcher, nftables.conf
   — не «команды в истории SSH».

## Быстрый снимок

```bash
ip -br addr
ip route show table all
ip rule show
ip route get 1.1.1.1
nft list ruleset
sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter
conntrack -S 2>/dev/null
```

## Модель

Пакет идёт так: **rule → table → route → nft (filter/nat) → device**.

`AllowedIPs` в WG/AWG — это cryptokey routing внутри интерфейса, не замена
`ip rule`. Если OS не отправила пакет в `awg0`, туннель ни при чём.

## Companion skills

- Host systemd/sshd/disk → `administering-linux`.
- Docker published ports vs iptables-nft → вместе с `docker-ops`.
- AWG handshake/keys → `amnezia-vpn`.

## References

- `references/policy-routing.md` — tables, rules, fwmark, split-tunnel.
- `references/nftables.md` — NAT, forward, conntrack, rp_filter.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: ip route ip rule policy routing fwmark rt_tables nftables masquerade conntrack rp_filter split tunnel vrf allowedips multiple wan
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
