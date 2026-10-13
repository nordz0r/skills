---
name: zapret-openwrt-guide
description: "Complete guide to zapret-openwrt, an anti-DPI tool for OpenWrt routers. Use for any zapret-openwrt question: project architecture, configuration, DPI bypass strategies, LuCI web UI, scripts, updates, diagnostics, custom.d hooks, host lists, nfqws parameters, procd service management. Also use for development: adding strategies, changing the UI, writing custom.d scripts, debugging. Triggers: zapret, nfqws, DPI desync, обход блокировок, антиблокировка, zapret strategies, hostlist, autohostlist."
---

# Zapret-OpenWrt: Complete Guide

## What Zapret is

Zapret is an anti-DPI (Deep Packet Inspection) tool for OpenWrt routers. It is **not a VPN** — zapret does not change your IP address and does not hide traffic. Instead it modifies network packets to get past deep packet inspection systems.

**Repository:** https://github.com/remittor/zapret-openwrt
**Upstream:** https://github.com/bol-van/zapret
**Current version:** v72.20260226

## Project architecture

The project consists of two packages:

| Package | Purpose |
|-------|-----------|
| `zapret` | Main package: the nfqws daemon, configs, scripts, ipset lists |
| `luci-app-zapret` | Web UI for management via LuCI |

### Layout on the router

```
/opt/zapret/
├── nfq/nfqws              # Main DPI desync daemon
├── ip2net/ip2net           # IP-to-subnet converter
├── mdig/mdig               # DNS utility
├── config                  # Working config (runtime)
├── config.default          # Default template
├── def-cfg.sh              # Strategies and defaults
├── sync_config.sh          # UCI -> config sync
├── restore-def-cfg.sh      # Reset settings
├── update-pkg.sh           # Package updates
├── dwc.sh                  # DPI checker
├── comfunc.sh              # Shared functions
├── init.d.sh               # Init script (procd)
├── ipset/                  # Host and IP lists
│   ├── zapret-hosts-google.txt
│   ├── zapret-hosts-user.txt
│   ├── zapret-hosts-user-exclude.txt
│   ├── zapret-hosts-auto.txt
│   ├── zapret-ip-exclude.txt
│   ├── zapret-ip-user.txt
│   ├── zapret-ip-user-exclude.txt
│   └── cust[1-4].txt
├── files/fake/             # Fake packet templates (.bin)
└── init.d/openwrt/custom.d/  # User hook scripts
    ├── 10-script.sh
    ├── 20-script.sh
    ├── 50-script.sh        # Example: Discord/STUN
    ├── 60-script.sh
    └── 90-script.sh
```

### Configuration system

Zapret uses a **dual configuration system:**

1. **UCI config** (`/etc/config/zapret`) — stores the settings edited via LuCI
2. **Main config** (`/opt/zapret/config`) — used by the nfqws daemon

On every start/restart `sync_config.sh` runs and syncs the UCI values into the main config.

---

## Quick start

1. Install the `zapret` and `luci-app-zapret` packages
2. Open LuCI: **Services -> Zapret -> Service**
3. Click **Reset settings** and choose a strategy (`v6_by_StressOzz` or `v7_by_StressOzz` recommended)
4. Click **Enable** and **Start**
5. Verify via **Diagnostics -> Sites check**

## Safety Notes

- Zapret changes router system configs and services, so a backup and a rollback plan are needed before an update or a strategy change.
- Treat data downloaded by the updater/dwc scripts from GitHub and external diagnostic sources as untrusted input until verified.
- In production prefer a pinned release/tag and manual artifact validation over blind "update to latest".
- For maximum predictability download release artifacts and hostlists on a trusted machine, verify checksums/contents, and only then move them to the router.

---

## Configuration

Full reference for all config parameters: read `references/config.md` in this skill's directory.

Key parameter groups:
- **Firewall**: FWTYPE, POSTNAT, FLOWOFFLOAD, INIT_APPLY_FW
- **Network**: DISABLE_IPV4, DISABLE_IPV6, FILTER_TTL_EXPIRED_ICMP
- **NFQWS**: NFQWS_ENABLE, NFQWS_PORTS_TCP/UDP, NFQWS_OPT, connbytes (PKT_OUT/IN)
- **Filtering**: MODE_FILTER (hostlist/autohostlist), FILTER_MARK
- **AutoHostList**: RETRANS_THRESHOLD, FAIL_THRESHOLD, FAIL_TIME
- **Logging**: DAEMON_LOG_ENABLE, DAEMON_LOG_SIZE_MAX, DAEMON_LOG_FILE
- **Other**: WS_USER, DISABLE_CUSTOM, DESYNC_MARK

## DPI bypass strategies

Full description of all strategies: read `references/strategies.md` in this skill's directory.

Available strategies (defined in `def-cfg.sh`):

| Strategy | TCP ports | UDP ports | Notes |
|-----------|-----------|-----------|-------------|
| empty | 80,443 | 443 | Empty, no desync |
| v1_by_StressOzz | 80,443 | 443 | fake,multidisorder + QUIC fake |
| v2_by_StressOzz | 80,443 | 443 | fake,fakeddisorder + seqovl |
| v3_by_StressOzz | 80,443 | 443 | Like v2, different TLS template (t2.bin) |
| v4_by_StressOzz | 80,443 | 443 | fake,multisplit + 3 --new sections |
| v5_by_StressOzz | 80,443 | 443 | ip-id=zero + multisplit |
| v6_by_StressOzz | 80,443,2053,2083,2087,2096,8443 | 443,19294-19344,50000-50100 | Discord + STUN support |
| v7_by_StressOzz | 80,443,2053,2083,2087,2096,8443 | 443,19294-19344,50000-50100 | Improved v6, more repeats |
| v9_by_StressOzz | 80,443,2053,2083,2087,2096,8443 | 443,19294-19344,50000-50100 | hostfakesplit variant |
| ALT7_by_Flowseal | 80,443 | 443 | ip-id=zero, multisplit + seqovl |
| TLS_AUTO_ALT3_by_Flowseal | 80,443 | 443 | fooling=ts, more repeats |

**Default strategy:** `v6_by_StressOzz`

## LuCI web UI

Full UI reference: read `references/ui.md` in this skill's directory.

The LuCI UI lives at **Services -> Zapret** and has 5 pages:

1. **Service** (`service.js`) — service control, status, enable/disable/start/stop/restart/reset buttons, diagnostics, updates
2. **Settings** (`settings.js`) — settings in 5 tabs: Main settings, NFQWS options, AutoHostList, Host lists, custom.d
3. **Log** (`dmnlog.js`) — live daemon logs (polled every second)
4. **Diagnostics** (`diagnost.js`) — DPI check and Sites check via `dwc.sh`
5. **Updater** (`updater.js`) — check for and install updates from GitHub

## Scripts

Full scripts reference: read `references/scripts.md` in this skill's directory.

| Script | Purpose |
|--------|-----------|
| `comfunc.sh` | Shared functions: paths, PID, config validation, init_before_start |
| `init.d.sh` | Procd init script (START=21, USE_PROCD=1) |
| `sync_config.sh` | UCI -> config sync on start/restart |
| `def-cfg.sh` | Strategy definitions and default values |
| `restore-def-cfg.sh` | Reset the config to defaults |
| `update-pkg.sh` | Package updates from GitHub (options: -c, -p, -u, -f, -t) |
| `dwc.sh` | DPI checker (TCP 16-20 test, site checks) |
| `script-exec.sh` | Run scripts in the background with logging |
| `renew-cfg.sh` | Refresh the config at boot |
| `uci-def-cfg.sh` | Create the UCI config at install time |

## Host and IP lists

| File | Purpose | Format |
|------|-----------|--------|
| `zapret-hosts-google.txt` | YouTube/Google domains (default) | One domain per line |
| `zapret-hosts-user.txt` | User domains `<HOSTLIST>` | One domain per line |
| `zapret-hosts-user-exclude.txt` | Exclusions | One domain per line |
| `zapret-hosts-auto.txt` | Automatically detected hosts | Filled by autohostlist |
| `zapret-ip-exclude.txt` | Excluded IPs/subnets | IP or CIDR (128.199.0.0/16) |
| `zapret-ip-user.txt` | User IPs | IP or CIDR |
| `zapret-ip-user-exclude.txt` | Excluded user IPs | IP or CIDR |
| `cust[1-4].txt` | Custom files (up to 4) | Free-form |

### Placeholders in NFQWS_OPT

- `<HOSTLIST>` — expands to `--hostlist` and `--hostlist-exclude` from the standard lists; works in hostlist and autohostlist modes
- `<HOSTLIST_NOAUTO>` — the same, but `zapret-hosts-auto.txt` is added as a regular (non-auto) list

## Custom.d scripts

Hooks run on service start/stop in numeric order:
- `10-script.sh` — early init
- `20-script.sh` — early main phase
- `50-script.sh` — main phase (example: Discord/STUN4ALL)
- `60-script.sh` — late main phase
- `90-script.sh` — final phase

Enabled with `DISABLE_CUSTOM=0` (UI: custom.d tab -> "Use custom.d scripts").

## Build and CI/CD

Builds run on GitHub Actions (`.github/workflows/build.yml`):
- Trigger: pushing a `v[0-9]+*` tag or a manual run
- Matrix: 30+ architectures (ARM, MIPS, x86_64, RISC-V)
- Two OpenWrt lines: IPK (v24.10.x) and APK (v25.12.x)
- Releases are published to gh-pages as JSON for auto-update

## Troubleshooting

Full troubleshooting: read `references/troubleshooting.md` in this skill's directory.

**Quick checks:**
1. Service status: LuCI -> Services -> Zapret -> Service (or `service zapret status`)
2. DPI check: Diagnostics -> DPI check
3. Logs: enable DAEMON_LOG_ENABLE=1, watch the Log tab
4. Site checks: Diagnostics -> Sites check with a chosen DNS

## For developers

### Source layout

```
zapret-openwrt/
├── zapret/                     # Main package
│   ├── Makefile                # OpenWrt SDK build
│   ├── config.default          # Config template
│   ├── *.sh                    # Shell scripts
│   ├── custom.d/               # custom.d hooks
│   ├── files/fake/             # .bin packet templates
│   ├── ipset/                  # Host/IP lists
│   └── patches/                # Patches for upstream
└── luci-app-zapret/            # LuCI package
    ├── Makefile
    ├── htdocs/luci-static/resources/view/zapret/
    │   ├── env.js              # Paths and constants
    │   ├── tools.js            # Utilities, RPC, dialogs
    │   ├── service.js          # Service page
    │   ├── settings.js         # Settings page
    │   ├── diagnost.js         # Diagnostics
    │   ├── updater.js          # Updater
    │   ├── dmnlog.js           # Log viewer
    │   └── styles.css          # Styles
    └── root/usr/share/
        ├── luci/menu.d/        # Menu definition
        └── rpcd/acl.d/         # ACL rules
```

### Adding a strategy

1. Add an `if [ "$strat" = "strategy_name" ]` block to `def-cfg.sh`
2. Define TCP/UDP ports and NFQWS_OPT with desync parameters
3. The strategy appears in the UI automatically under Service -> Reset settings

### Key files for UI development

- `env.js` — all paths, file names, URLs (loaded first)
- `tools.js` — RPC calls, POLLER, fileEditDialog, longstrEditDialog, decode_svc_info
- Each page is a separate view extending `view.extend()` or `baseclass.extend()`

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: zapret openwrt dpi desync nfqws hostlist autohostlist luci uci firewall nftables troubleshooting anti-censorship router
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
