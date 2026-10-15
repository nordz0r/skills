---
name: xray-reality
description: "Xray-core VLESS + REALITY / XHTTP / Vision server and client setup on a Linux VPS: config.json inbound/outbound, x25519 keys, shortIds, target/serverNames donor choice, fingerprint, xtls-rprx-vision, XHTTP modes, ML-DSA-65, VLESS Encryption, FinalMask, vless:// share links, systemd, troubleshooting. Triggers: xray, vless, reality, xhttp, xtls, vision, 3x-ui, sing-box outbound vless, иксрей, реалити, влесс, обход блокировок."
---

# Xray (VLESS + REALITY / XHTTP)

Operator guide for Xray-core on a VPS and for client profiles (Xray JSON,
`vless://` links, sing-box / mihomo outbounds).

Not covered here:
- AmneziaWG (UDP, WireGuard-based) → `amnezia-vpn` (Linux) or `amneziawg-openwrt-guide`.
- Router-side selective routing with sing-box → `podkop-openwrt-guide`.
- Linux policy routing (`ip rule`, fwmark, nft) → `linux-routing`.
- Choosing between AWG and Xray, end-to-end VPN rollout → `vpn-setup`.

## Workflow

1. Check the core version first: `xray version`. Parameters depend on it
   (see `references/versions.md`). Keep server ≥ client.
2. Pick the stack:
   - Default: VLESS + REALITY + RAW(TCP) + `flow: xtls-rprx-vision`, port 443.
   - Need CDN / HTTP-shaped traffic or Vision is fingerprinted: VLESS + REALITY (or TLS) + XHTTP.
3. Generate secrets on the server, never paste them into chats/repos:
   `xray uuid`, `xray x25519`, `openssl rand -hex 8` (shortId),
   optional `xray mldsa65`, `xray vlessenc`.
4. Choose the donor (`target` + `serverNames`): TLS 1.3 + HTTP/2, real CA cert,
   reachable from the VPS, SNI covered by the donor's cert. Verify from the VPS.
5. Write `/usr/local/etc/xray/config.json`, `xray run -test -c ...`, restart the unit.
6. Build the client (JSON or `vless://`), verify, then wire routing.

## Hard rules

- `flow` must match on both sides; the `-udp443` suffix is client-only.
- Vision works only over TLS/REALITY and RAW; not with XHTTP.
- REALITY transports: RAW, XHTTP, gRPC only.
- `shortIds`: even-length hex, ≤16 chars; `""` allows an empty sid.
- `serverNames` / `shortIds` must not be empty on the server.
- Client must set `fingerprint` (e.g. `chrome`); `serverName` from `serverNames`.
- Use `target` (formerly `dest`, renamed in v24.10.31).
- v26.7.11+: plain VLESS/Trojan to a public address is rejected; `allowInsecure` is removed.
- Facts are verified against Xray-core v26.10.10 code/releases (2026-10-15); each reference states its sources.
- Never log `privateKey`, UUIDs or full share links; use placeholders.

## References

- `references/server-config.md` — install, server/client JSON, systemd, share links, donor rules.
- `references/xhttp-finalmask.md` — XHTTP modes, padding knobs, FinalMask.
- `references/versions.md` — feature-by-version table (verified against releases).
- `references/troubleshooting.md` — checks and failure patterns.
- `references/README.ru.md` — Russian summary.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: xray vless reality xhttp xtls vision x25519 shortids servernames target fingerprint 3x-ui share link vps proxy
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
