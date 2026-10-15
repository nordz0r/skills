---
name: amnezia-vpn
description: "Amnezia VPN and AmneziaWG on Linux/VPS/Docker, not OpenWrt: handshake, awg show, amneziawg-go, kernel module, Jc/H1, /opt/amnezia, Ubuntu VPS, UDP. Triggers: amneziawg, awg-quick, amneziawg-go, amnezia docker, VPS VPN, handshake, впн, амнезия, сервер VPN, рукопожатие."
---

# Amnezia VPN (Linux / Docker)

Skill for Amnezia on a Linux server and in an application Docker stack.
This is not the OpenWrt integration: UCI/LuCI/`kmod-amneziawg` on a router is
`amneziawg-openwrt-guide`.

Selective routing on OpenWrt via podkop is `podkop-openwrt-guide`.
Policy routing on a Linux host is `linux-routing`.

## When to use

- Bring up or fix AmneziaVPN on a VPS (the official Docker stack).
- Linux AWG without a GUI: `awg`, `awg-quick`, kernel module vs `amneziawg-go`.
- No handshake, wrong Jc/Jmin/Jmax/S1/S2/H1-H4, port closed.
- `amnezia-*` containers, `/opt/amnezia` data, docker logs.
- Neighbouring protocols of the stack: WireGuard, Xray/Reality, OpenVPN, Cloak, SS —
  only in the Amnezia context, not as separate products.

## Workflow

1. Split the scenario:
   - AmneziaVPN GUI → Docker containers on a VPS.
   - Bare AWG → `awg0` + `awg-quick` / kernel module.
   - OpenWrt router → a different skill.
2. Never log the PrivateKey, preshared key or obfuscation secrets in full.
   Use placeholders in answers.
3. Handshake = keys + identical obfuscation params + UDP port + endpoint.
4. After changes: `awg show` / `docker ps` / `ss -ulnp` / ping inside the tunnel.

## What is in the stack

The official app deploys Docker on the server. Data usually lives in
`/opt/amnezia`. Containers are prefixed with `amnezia-`.

Bare AmneziaWG is compatible with WireGuard's key model, but packets will not
pass if the junk/header params differ between the two sides.

| Layer | Purpose |
|------|--------|
| `kmod amneziawg` | kernel datapath, low overhead |
| `amneziawg-go` | userspace fallback when the module is missing |
| `awg` / `awg-quick` | like `wg` / `wg-quick` |

## Companion skills

- OpenWrt AWG → `amneziawg-openwrt-guide`.
- Docker engine/compose syntax → `docker-ops`.
- `ip rule`/nft for split-tunnel on Linux → `linux-routing`.
- Host systemd/disk/ssh → `administering-linux`.
- Xray VLESS/REALITY/XHTTP → `xray-reality`; end-to-end VPN rollout → `vpn-setup`.

## References

- `references/linux-awg.md` — awg-quick, kernel/userspace, diagnostics.
- `references/docker-stack.md` — AmneziaVPN containers on a VPS.
- `references/awg-protocol.md` — AWG 1.0–3.1 parameters (Jc/Jmin/Jmax, S1–S4, H1–H4, I1–I5, HeaderProtectionKey, 3.1 flags), what must match, client limits.
- `references/architect-audit.md` — audit of the architect.vai-rice.space generator: what is useful, what is wrong/outdated.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amnezia amneziavpn amneziawg awg-quick awg0 opt/amnezia docker vpn jc jmin jmax handshake amneziawg-go vps
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
