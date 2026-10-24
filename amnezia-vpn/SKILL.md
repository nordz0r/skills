---
name: amnezia-vpn
description: "Optimal configuration of AmneziaWG and Xray VPN (not installation or deployment). AmneziaWG 1.0-3.1 parameters and recipes: Jc/Jmin/Jmax, S1-S4, H1-H4, I1-I5 mimicry, HeaderProtectionKey, ContentPaddingAddition, RandomTrailers, DisableCookies, MTU, strong DPI / mobile / router kmod / old clients. Xray-core VLESS server and client config.json: transport choice (RAW, XHTTP modes, Hysteria 2), flow/Vision, REALITY target donor, serverNames, shortIds, fingerprint, FinalMask, VLESS Encryption, sniffing/routing. vpn:// and vless:// key formats, config validation checklist, versions and client compatibility, config troubleshooting, FAQ. Not OpenWrt UCI/LuCI. Triggers: amneziawg config, awg conf, jc jmin jmax, h1 h4, i1 i5, xray config, vless reality, xhttp mode, finalmask, vless encryption, vpn:// key, vless://, параметры обфускации, конфиг впн, оптимальные настройки, амнезия, рукопожатие."
---

# AmneziaWG and Xray: optimal configuration

Configuration only: choosing parameters, writing and validating server/client configs and keys.
Installation, Docker, systemd, VPS prep and launch are out of scope — except the engine choice (see Key rules), because it changes the config.

Not here: OpenWrt AWG UCI/LuCI → `amneziawg-openwrt-guide`; router-wide sing-box → `podkop-openwrt-guide`;
Linux policy routing → `linux-routing`.

## Procedure: choosing the optimal config

1. **Collect constraints.** Server engine and version (amneziawg-go / kmod / Xray-core); every client app and version;
   network: is UDP passing, is there DPI or active probing, mobile/CGNAT, CDN needed, IP/ASN blocked.
   IP/ASN block or allow-lists → config cannot fix it; say so.
2. **Pick the protocol.**
   | Situation | Choice |
   |---|---|
   | UDP passes, full tunnel, phones/routers | AmneziaWG → `awg-config.md` |
   | UDP cut, active probing, SNI allow-lists | Xray VLESS + REALITY + Vision (RAW) → `xray-config.md` |
   | Need CDN / HTTP-shaped traffic | Xray VLESS + XHTTP → `xray-xhttp-finalmask.md` |
   | Both available | AWG primary + Xray on TCP/443 as fallback |
3. **Pick the version** = the lowest common version of server and all clients (`awg-protocol.md`, `versions-compat.md`).
   Never put keys newer than the oldest client.
4. **AWG:** shared set once per server (S1–S4, H1–H4, HeaderProtectionKey, RandomTrailers);
   sender set per device (Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition); MTU per network;
   apply the scenario recipe (strong DPI, mobile, router kmod, old clients) in `awg-config.md`.
5. **Xray:** transport → flow → REALITY donor → fingerprint → XHTTP mode → FinalMask/VLESS Encryption only if needed
   → sniffing/routing (`xray-config.md`, `xray-xhttp-finalmask.md`).
6. **Encode keys** if needed: `vpn://` / `vless://` (`key-formats.md`).
7. **Validate** with `config-checklist.md` (and `xray run -test -c` for Xray JSON); on errors → `troubleshooting.md`.
8. Report each choice with its source/version; mark inferences. Placeholders only — never print private keys,
   PSK, HeaderProtectionKey, UUIDs or real `vpn://`/`vless://` links.

## Key rules

- AWG: H1–H4, S1–S4, HeaderProtectionKey, RandomTrailers must match; Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition are sender-only.
- AWG: unknown key for the engine version → interface fails; S1–S4 ≥ 12 with HeaderProtectionKey; H ranges must not overlap.
- AWG port in examples: 443/udp (Amnezia app default is 55424).
- AWG engine: **always install the kernel module (DKMS `amneziawg`) when the host allows it**; userspace `amneziawg-go` is a fallback only. Check `lsmod | grep amneziawg` on the host and `ip -d link show awg0` (type `amneziawg`, not `tun`) → `awg-kmod.md`.
- Xray: Vision only over RAW + TLS/REALITY; REALITY only over RAW/XHTTP/gRPC; server flow only `""`/`xtls-rprx-vision`.
- Xray v26.7.11+: plain VLESS to a public address is rejected; `allowInsecure` removed; unknown JSON fields are silently ignored.

## References

- `references/awg-protocol.md` — AWG 1.0–3.1 parameters, what must match, tags, Amnezia defaults, minimum client versions.
- `references/awg-config.md` — AWG selection order, value generation, scenario recipes, MTU, I1–I5 mimicry, server/client templates.
- `references/awg-kmod.md` — kernel module (DKMS) over userspace: install, Docker restart, how to verify, pitfalls.
- `references/xray-config.md` — Xray selection order, server/client JSON, donor, fingerprint, VLESS Encryption, sniffing/routing.
- `references/xray-xhttp-finalmask.md` — XHTTP modes and options, FinalMask, Hysteria 2.
- `references/key-formats.md` — `vpn://` structure and editing, `vless://` parameters.
- `references/versions-compat.md` — Xray features by version, client compatibility.
- `references/config-checklist.md` — validation checklist (AWG `.conf`, `vpn://`, `vless://`, Xray JSON).
- `references/troubleshooting.md` — config errors for AWG and Xray.
- `references/faq.md` — configuration FAQ, each item verified/corrected/flagged.

Sources verified 2026-10-15: amneziawg-go v3.1.20260828, kmod v3.1.20260906, amneziawg-tools v3.1.20260812, amnezia-client 5.0.3.0, Xray-core v26.10.10 (prerelease; latest stable v26.3.27, install via `XTLS/Xray-install` with `--version <tag>` / `--beta`).

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amnezia amneziavpn amneziawg awg jc jmin jmax h1 s1 i1 headerprotectionkey randomtrailers mtu xray vless reality xhttp vision finalmask vlessenc x25519 shortids fingerprint vpn-key obfuscation dpi config
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
