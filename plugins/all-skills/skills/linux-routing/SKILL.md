---
name: linux-routing
description: "Linux split-tunnel and policy routing: ip rule, fwmark, WAN, awg0, default via VPN, nft masquerade, rp_filter, conntrack. Not OpenWrt, not podkop, not UCI. Triggers: split-tunnel, ip rule, fwmark, multiple default, rt_tables, source-based routing, маршрутизация, таблица маршрутов, раздельный туннель."
---

# Linux Routing

Skill for routing and NAT on a Linux host (iproute2 + nftables).
Write `ip`/`nft` commands that can be pasted into a console or a unit.

Do not use it for:

- OpenWrt + podkop/sing-box → `podkop-openwrt-guide`
- zapret DPI → `zapret-openwrt-guide`
- Docker bridge overlay as the main subject → `docker-ops`
- Amnezia keys/handshake → `amnezia-vpn`; only OS routes/NAT belong here

## When to use

- Two default routes, VPN + WAN, split-tunnel.
- `ip rule`, tables, fwmark, source-based routing.
- NAT/masquerade, port forward, conntrack.
- A packet goes into the VPN and the reply never comes back; asymmetric routing.
- WireGuard/AWG `AllowedIPs` vs `ip route`.

## Workflow

1. Capture the picture: `ip -br addr`, `ip route`, `ip rule`, `nft list ruleset`.
2. Separate L3 (route/rule) from L4 NAT (nft) and from firewall drops.
3. Change one table/rule at a time. Never blindly delete the default route in main.
4. Check with `ip route get <dst> from <src> iif <if> mark <hex>`.
5. Persistence: `/etc/iproute2/rt_tables`, netplan/NM dispatcher, nftables.conf
   — not "commands in the SSH history".

## Quick snapshot

```bash
ip -br addr
ip route show table all
ip rule show
ip route get 1.1.1.1
nft list ruleset
sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter
conntrack -S 2>/dev/null
```

## Model

A packet flows: **rule → table → route → nft (filter/nat) → device**.

`AllowedIPs` in WG/AWG is cryptokey routing inside the interface, not a
replacement for `ip rule`. If the OS did not send the packet to `awg0`, the tunnel is not the problem.

## Companion skills

- Host systemd/sshd/disk → `administering-linux`.
- Docker published ports vs iptables-nft → together with `docker-ops`.
- AWG handshake/keys → `amnezia-vpn`.

## References

- `references/policy-routing.md` — tables, rules, fwmark, split-tunnel.
- `references/nftables.md` — NAT, forward, conntrack, rp_filter.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: ip route ip rule policy routing fwmark rt_tables nftables masquerade conntrack rp_filter split tunnel vrf allowedips multiple wan
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
