---
name: amneziawg-openwrt-guide
description: "Complete guide to amneziawg-openwrt. Use for any AmneziaWG task on OpenWrt: installing amneziawg-tools, kmod-amneziawg, luci-proto-amneziawg, configuring proto amneziawg, UCI/LuCI interface and peer config, key generation, QR, watchdog, package builds and kernel/userspace fallback debugging. Triggers: amneziawg, amnezia, awg, luci-proto-amneziawg, kmod-amneziawg, amneziawg-tools, amneziawg-go, openwrt awg."
---

# AmneziaWG OpenWrt Guide

This skill covers the integration of the AmneziaWG protocol into OpenWrt, not "the whole Amnezia product". The repository contains a kernel module, userspace tools, a `netifd` helper and a LuCI UI.

Use it to understand how to bring up `proto 'amneziawg'`, how peer sections work, how the userspace fallback works, and where to fix the LuCI/RPC part.

## When to use

- Configuring an AmneziaWG interface on OpenWrt.
- Understanding the UCI schema or LuCI form fields.
- Debugging handshakes, endpoint resolution, key generation, the status page.
- Building packages in the OpenWrt SDK/Buildroot.
- Working with `kmod-amneziawg`, `amneziawg-tools`, `luci-proto-amneziawg`.
- Finding out why the kernel module did not load and the userspace fallback kicked in.

## Quick workflow picker

- Router and UCI/LuCI task: start with `references/uci-model.md`.
- Repository layout task: open `references/architecture.md`.
- Build, compatibility or diagnostics task: open `references/build-and-debug.md`.

Open only the reference you need: upstream barely explains the workflow in prose and the important details are hidden in the code.

## Router Workflow

1. Clarify whether kernel mode is required or the userspace fallback is acceptable.
2. Check which packages are actually installed on the router: `amneziawg-tools`, `luci-proto-amneziawg`, `kmod-amneziawg`.
3. Check the interface UCI model and peer sections.
4. If the problem is the endpoint/dynamic DNS, check `persistent_keepalive` and the watchdog workflow.
5. For LuCI tasks, check the JS form, the RPC ucode and the status page together.

## Development Workflow

- `amneziawg-tools/` provides the `awg` binary, the `netifd` helper and the watchdog.
- `kmod-amneziawg/` patches OpenWrt's in-tree WireGuard sources and is therefore very sensitive to kernel layout changes.
- `luci-proto-amneziawg/` contains the protocol form, RPC methods, ACL and the status page.
- Any change must account for both the runtime on the router and the packaging in Buildroot.

## Things to watch

- The repository does not ship a "full Amnezia client", only the OpenWrt integration layer.
- The userspace fallback needs `amneziawg-go`, but the upstream repository does not ship that binary.
- QR generation needs `qrencode` installed.
- Kernel patch changes break easily on new OpenWrt/kernel trees.

## Security Notes

- Install packages and binaries only from a verified feed, a release artifact or a pinned commit/tag, not from an unverified mirror.
- For `amneziawg-go`, kernel patches and LuCI components, pin the version and check the source before updating.
- Do not feed values from an untrusted external source into UCI/LuCI without manual review.

## References

- `references/architecture.md`: package roles and a map of key files.
- `references/uci-model.md`: the `proto amneziawg` interface, peer sections, options and their meaning.
- `references/build-and-debug.md`: builds, kernel/userspace fallback, watchdog and runtime diagnostics.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amneziawg awg openwrt luci uci peer interface handshake endpoint keys qr watchdog kernel userspace vpn router
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
