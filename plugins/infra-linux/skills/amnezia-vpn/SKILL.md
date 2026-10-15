---
name: amnezia-vpn
description: "Self-hosted VPN on Linux/VPS/Docker (not OpenWrt): AmneziaVPN Docker stack, AmneziaWG 1.0-3.1 (awg, awg-quick, amneziawg-go, kernel module, Jc/Jmin/Jmax, S1-S4, H1-H4, I1-I5, HeaderProtectionKey, RandomTrailers), Xray-core VLESS + REALITY / XHTTP / Vision (config.json, x25519, shortIds, target, vless:// links, FinalMask), vpn:// keys, protocol choice, clients and minimum versions, verification, troubleshooting, FAQ. Triggers: amneziawg, awg-quick, amnezia docker, xray, vless, reality, xhttp, VPS VPN, handshake, obfuscation, DPI, впн, амнезия, свой vpn, обход блокировок, рукопожатие."
---

# Amnezia VPN, AmneziaWG and Xray (Linux / Docker)

One home for self-hosted VPN on a Linux server: the Amnezia app's Docker stack,
bare AmneziaWG, bare Xray-core, clients and verification.

Not here: OpenWrt AWG (UCI/LuCI/`kmod-amneziawg`) → `amneziawg-openwrt-guide`;
router-wide sing-box routing → `podkop-openwrt-guide`; Linux policy routing → `linux-routing`.

## Workflow

1. Pick the protocol and plan → `references/vpn-setup.md`.
2. Server:
   - Amnezia app installs Docker containers → `references/docker-stack.md`.
   - Bare AWG (`awg-quick`, kmod vs `amneziawg-go`) → `references/linux-awg.md`.
   - Bare Xray-core → `references/xray-server.md`.
3. Parameters: AWG → `references/awg-protocol.md`; Xray versions → `references/xray-versions.md`.
4. Clients and minimum versions → `references/vpn-setup.md`.
5. Verify, then troubleshoot (`vpn-setup.md`, `linux-awg.md`, `xray-troubleshooting.md`).
6. Never log private keys, PSK, HeaderProtectionKey, UUIDs, `vpn://`/`vless://` links; use placeholders.

## Key rules

- AWG: H1–H4, S1–S4, HeaderProtectionKey, RandomTrailers must match; Jc/Jmin/Jmax/I1–I5 are sender-only.
- AWG: unknown key for the device version → interface does not come up; S1–S4 ≥ 12 with HeaderProtectionKey.
- Xray: `flow` matches on both sides; Vision only over TLS/REALITY; REALITY only over RAW/XHTTP/gRPC.
- Xray v26.7.11+: plain VLESS to a public address is rejected; `allowInsecure` removed.

## References

- `references/vpn-setup.md` — protocol choice, VPS prep, clients + minimum versions, verification, troubleshooting by symptom.
- `references/docker-stack.md` — Amnezia containers, ports, `/opt/amnezia` paths.
- `references/linux-awg.md` — `awg-quick`, kernel/userspace, NAT, systemd, handshake diagnostics.
- `references/awg-protocol.md` — AWG 1.0–3.1 parameters, what must match, Amnezia defaults, client versions.
- `references/xray-server.md` — install, server/client JSON, `vless://`, donor rules.
- `references/xray-xhttp-finalmask.md` — XHTTP modes, FinalMask, Hysteria 2.
- `references/xray-versions.md` — Xray features by version.
- `references/xray-troubleshooting.md` — Xray errors and checks.
- `references/faq.md` — FAQ (from the architect.vai-rice.space generator), every item verified/corrected/flagged.

Sources verified 2026-10-15: amneziawg-go v3.1.20260828, kmod v3.1.20260906, amneziawg-tools v3.1.20260812, amnezia-client 5.0.3.0, Xray-core v26.10.10.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amnezia amneziavpn amneziawg awg-quick awg0 opt/amnezia docker vpn jc jmin jmax handshake amneziawg-go vps xray vless reality xhttp vision x25519 shortids vpn-key obfuscation dpi
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
