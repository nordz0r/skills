---
name: podkop-openwrt-guide
description: "Complete guide to Podkop on OpenWrt. Use for any itdoginfo/podkop task: install, update, migrating /etc/config/podkop, selective/domain routing via sing-box, dnsmasq, nft/tproxy, LuCI UI, proxy URL strings (vless, trojan, ss, hysteria2, socks), community/user lists, selector/urltest, exclusion, Clash API/YACD dashboard, BadWAN monitoring, FakeIP, service diagnostics and development of podkop, luci-app-podkop, fe-app-podkop. Triggers: podkop, luci-app-podkop, sing-box on OpenWrt, fakeip, proxy_string, community lists, selective routing, clash api, yacd, urltest, selector, exclusion, роутер, обход блокировок, прокси, списки доменов."
---

# Podkop OpenWrt Guide

Podkop is an orchestration layer over `sing-box` for OpenWrt: it manages selective routing, edits `dnsmasq`, assembles rules/lists, generates NFTable rules for tproxy and provides a LuCI UI.

Use this skill when you need more than "change something in the config": when you need to understand how Podkop ties together `UCI`, `dnsmasq`, `sing-box`, `nft` and the service lifecycle.

## When to use

- Installing or updating Podkop on an OpenWrt router.
- Migrating the config after an incompatible release.
- Configuring proxy strings, selector/urltest groups, raw outbound JSON.
- Working with community lists, user domains/subnets, remote/local lists.
- Configuring mixed proxy, YACD dashboard, Clash API, FakeIP.
- Connection types: proxy, vpn, block, exclusion.
- BadWAN interface monitoring, DNS (UDP/DoT/DoH), NTP exclusion.
- Diagnosing `sing-box`, `dnsmasq`, `nft`, dashboard or LuCI breakage.
- Developing the shell backend, LuCI UI or TypeScript frontend in the `itdoginfo/podkop` repo.
- Analysing conflicts with `https-dns-proxy`, `nextdns`, `passwall`, `Getdomains`.

## Architecture (high level)

```
UCI config (/etc/config/podkop)
       ↓
  /usr/bin/podkop (orchestrator)
       ↓
  ┌────┴────┬──────────┬──────────┬──────────┐
  ↓         ↓          ↓          ↓          ↓
helpers   nft.sh    sing-box   dnsmasq   ip rule/
rulesets           config_*   redirect  rt table
```

Traffic: client → NFTable (mark 0x00100000) → tproxy (127.0.0.1:1602) → sing-box → outbound (proxy/vpn/block/direct). DNS: dnsmasq → 127.0.0.42:53 (sing-box DNS inbound) → FakeIP (198.18.0.0/15) for domain routing.

## Quick workflow picker

- Live router task → `references/operations.md`.
- Codebase and build task → `references/repo-map.md`, then `references/build-and-dev.md`.
- Proxy string correctness → `references/proxy-strings.md`.

Open only the reference you need; do not load all files at once.

## Safety Notes

- Podkop changes system services and router configs. Before install or migration back up `/etc/config/podkop` and know the rollback path.
- Do not run a remote install/update script without pinning the version and reviewing its contents.
- Remote domain/subnet lists and community data are external input. Do not treat them as trusted automatically.

## Router Workflow

1. Record the OpenWrt version and free flash space.
2. Back up `/etc/config/podkop`, the `sing-box` config and, if risky, `dnsmasq`.
3. Check constraints: OpenWrt `24.10+`, `sing-box` ≥ 1.12.0 (diagnostics want ≥ 1.12.4; xhttp links, urltest fallbacks and uTLS fallback need podkop-engine r11+), HTTP-only dashboard, no IPv6, conflicting packages.
4. Install/update with the upstream script; for migration see the section in `operations.md`.
5. Diagnose with the Podkop CLI (`global_check`, `check_proxy`), then `nft`, `dnsmasq`, `sing-box` logs.

## Development Workflow

- Shell backend: `podkop/files/usr/bin/podkop` + libraries `podkop/files/usr/lib/*.sh`.
- LuCI package: `luci-app-podkop/` (built JS + RPC ACL + menu).
- Frontend sources: `fe-app-podkop/` (TypeScript, vitest, eslint, prettier).
- Release pipeline: Docker (`Dockerfile-ipk`, `Dockerfile-apk`), CI ShellCheck for shell.

## Things to watch

- Podkop changes `dnsmasq` and `sing-box`; without a backup it is easy to lose working routing.
- The project is under active development; docs may lag behind the code.
- After updates clear the LuCI cache and check the config.
- The dashboard (YACD) only works over HTTP, not HTTPS or a domain name.
- Config `0.7.0+` is incompatible with older schemas — a migration is required.
- `sing-box` ≥ 1.12.0, `jq` ≥ 1.7.1, `coreutils-base64` ≥ 9.7. Verified against podkop 0.7.24 (2026-10-11) on 2026-10-15.

## References

- `references/operations.md`: full operations — install, migration, config model, all CLI commands, Clash API, traffic architecture.
- `references/repo-map.md`: repository structure, shell libraries, LuCI components, areas of responsibility.
- `references/build-and-dev.md`: frontend/backend workflow, CI and release build.
- `references/proxy-strings.md`: URL scheme formats, parameters, validation.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: podkop openwrt sing-box selective routing fakeip clash api selector urltest proxy strings luci dns router
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
