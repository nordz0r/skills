---
name: vpn-setup
description: "End-to-end self-hosted VPN / anti-DPI rollout playbook: choose AmneziaWG (UDP) vs Xray VLESS+REALITY/XHTTP (TCP), prepare a VPS, deploy server, issue per-device client configs, split tunnelling and routing on Linux/OpenWrt, verification checklist and troubleshooting by symptom. Triggers: настроить vpn, свой vpn сервер, обход блокировок, dpi, awg или xray, vps vpn, split tunnel, vpn не работает, vpn setup, self-hosted vpn."
---

# VPN setup playbook (AWG + Xray)

Router skill for a full rollout. Protocol details live in the protocol skills;
this one decides *what* to deploy and in *which order*, and how to verify it.

## Pick the protocol

| Situation | Choose |
|---|---|
| UDP passes, need full-tunnel speed, routers/phones | AmneziaWG → `amnezia-vpn` (`references/awg-protocol.md`) |
| UDP throttled/blocked, active probing, whitelists by SNI | Xray VLESS + REALITY → `xray-reality` |
| Need CDN fronting / HTTP-shaped traffic | Xray VLESS + XHTTP → `xray-reality` |
| Router-wide selective routing | OpenWrt: `podkop-openwrt-guide` (sing-box) / `amneziawg-openwrt-guide` |
| Neither helps | IP-level block: change IP/provider; obfuscation does not fix address blocks |

Deploying both (AWG on UDP + Xray on 443/TCP) on one VPS is a normal fallback setup.

## Workflow

1. VPS: fresh Linux, updates, SSH keys, firewall (allow 22/tcp, 443/tcp for Xray,
   chosen UDP port for AWG), `net.ipv4.ip_forward=1` for AWG, time sync (REALITY is time-sensitive).
2. Server: follow the protocol skill. Generate keys on the server only.
3. Clients: one identity per device (AWG peer / Xray UUID + shortId) so access can be revoked individually.
4. Routing: full tunnel first, then split (`linux-routing`, `podkop-openwrt-guide`).
5. Verify with the checklist in `references/checklist.md`.
6. Document placeholders only; never commit keys, UUIDs, share links, `vpn://` keys.

## References

- `references/checklist.md` — deploy + verification + troubleshooting by symptom.
- `references/README.ru.md` — Russian summary.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: vpn setup self-hosted vps anti-dpi amneziawg xray reality split tunnel routing checklist troubleshooting
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
