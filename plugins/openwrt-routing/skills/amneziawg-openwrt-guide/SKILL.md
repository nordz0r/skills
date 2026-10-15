---
name: amneziawg-openwrt-guide
description: "AmneziaWG on OpenWrt routers: packages kmod-amneziawg, amneziawg-tools, luci-proto-amneziawg (Slava-Shchipunov/awg-openwrt builds, AWG 1.0-3.1), opkg .ipk on 23.05/24.10 vs apk feed on 25.12, proto amneziawg UCI options (awg_jc..awg_i5, awg_header_protection_key, awg_random_trailers, awg_disable_cookies, timers), peer sections, LuCI import/QR/status, watchdog, kernel vs userspace, router-side diagnostics. Parameter meaning and optimal values live in amnezia-vpn. Triggers: amneziawg openwrt, luci-proto-amneziawg, kmod-amneziawg, proto amneziawg, uci awg, awg на роутере, амнезия роутер, cudy awg."
---

# AmneziaWG on OpenWrt

OpenWrt-specific layer only: packages, UCI/LuCI names, router runtime and diagnostics.
**What each obfuscation parameter means and which values to choose → `amnezia-vpn`** (`awg-protocol.md`, `awg-config.md`). Do not duplicate it here.

Upstream: `Slava-Shchipunov/awg-openwrt` @ 03b6226 (2026-09-23, AWG 3.1). `amnezia-vpn/amneziawg-openwrt` is abandoned since 2024-03 (AWG 1.0 only). Verified 2026-10-15.

## Workflow

1. Read-only first: OpenWrt version (`/etc/openwrt_release`), package manager (apk on 25.x, opkg on ≤24.10), installed `kmod-amneziawg`/`amneziawg-tools`/`luci-proto-amneziawg` versions → `references/build-and-debug.md`.
2. Protocol version the packages support (3.1 needs builds `v24.10.8` / `v25.12.5`+) must be ≥ the parameters in the config.
3. Map the server/client config to UCI options → `references/uci-model.md`; choose values with `amnezia-vpn`.
4. Diagnose: kernel vs userspace, `logread`, `awg show` with keys filtered, handshake → `references/build-and-debug.md`.
5. Changes to interfaces, peers, keys or packages only with explicit approval; back up `/etc/config/network` first.

## Key facts

- Packages build from official `amnezia-vpn` sources by tag; kmod must match the firmware kernel exactly.
- UCI: `awg_s3/s4`, `awg_i1..i5` (2.0/1.5+), `awg_header_protection_key`, `awg_content_padding_addition`, `awg_rekey_after_time`, `awg_rekey_timeout`, `awg_reject_after_time`, `awg_keepalive_timeout`, `awg_max_handshake_attempts` (3.0+), `awg_random_trailers`, `awg_disable_cookies` (3.1, boolean).
- Runtime config `/tmp/amneziawg/<iface>.conf`; QR via `luci-lib-uqr` (no `qrencode`).
- `amneziawg-install.sh` can reroute all traffic into the tunnel — never run it unattended on a live router.

## Safety

- Never print `private_key`, `preshared_key`, `awg_header_protection_key`; filter `uci show`/`awg show`.
- Install only from the upstream Releases/feed with its signing key, pinned by version.

## References

- `references/architecture.md` — which upstream is current, packages and versions, runtime.
- `references/uci-model.md` — UCI option ↔ `.conf` key ↔ AWG version, peer sections, template.
- `references/build-and-debug.md` — opkg vs apk, update rules, read-only diagnostics, build.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amneziawg awg openwrt luci uci proto peer interface handshake endpoint kmod apk opkg feed qr watchdog kernel userspace router cudy
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
