# AmneziaWG OpenWrt: источники и пакеты

Сверено 2026-10-15.

## Какой апстрим актуален

| Репозиторий | Статус |
|---|---|
| `amnezia-vpn/amneziawg-openwrt` | **заброшен**: последний коммит 56bf9fe, 2024-03-12; только AWG 1.0 (`awg_jc…awg_h4`). Не использовать как источник. |
| **`Slava-Shchipunov/awg-openwrt`** (форк `yury-sannikov/awg-openwrt`) | основной: HEAD 03b6226 (2026-09-23, «add awg v3.1 support» #172); готовые `.ipk` в Releases и apk-feed для 25.x. Справка ниже — по нему. |
| `this-username-has-been-taken/amneziawg-openwrt` (YAAWG) | альтернативный форк с 3.1 (v3.1.2, 2026-09-13), переработанный LuCI; имена UCI-опций с основным не сверялись ❔. |
| `2Grey/awg-openwrt` | форк Slava-Shchipunov: luci-proto 3.1.1 (новая страница статуса, импорт `.conf`); сборки для 23.05/24.10. |

Пакеты собираются из официальных исходников по тегу (`PKG_SOURCE_URL` = `amnezia-vpn/…`, `PKG_SOURCE_VERSION:=v$(PKG_VERSION)`).

## Пакеты (Slava-Shchipunov @ 03b6226)

| Пакет | Версия | Что даёт |
|---|---|---|
| `kmod-amneziawg` | 3.1.20260906 | модуль ядра `amneziawg` из `amneziawg-linux-kernel-module` (не патч in-tree WireGuard, как в старом репо) |
| `amneziawg-tools` | 3.1.20260812 | `awg`, netifd-helper `/lib/netifd/proto/amneziawg.sh`, `/usr/bin/amneziawg_watchdog`; зависит от `kmod-amneziawg` (с 2026-05-20) |
| `luci-proto-amneziawg` | 3.1.0 | форма протокола, импорт `.conf`, генерация ключей/PSK/HPK, QR (через `luci-lib-uqr`, `qrencode` не нужен), статус `view/amneziawg/status.js`, rpcd `ucode/luci.amneziawg`; зависит от `ucode`, `luci-lib-uqr`, `resolveip` |

Сборки по версиям OpenWrt (README): AWG **3.1** — `v24.10.8` и `v25.12.5`; более ранние релизы 24.10.x/25.12.x — AWG 2.0; 23.05.x — 1.x/2.0.
Пакеты собраны под конкретную версию ядра: kmod ставится только той же версии OpenWrt/target, что на роутере.

## Runtime

1. `netifd` поднимает интерфейс `proto 'amneziawg'`.
2. Helper делает `modprobe amneziawg`; при успехе — `ip link add dev <iface> type amneziawg` (kernel mode).
3. Иначе — userspace `${WG_QUICK_USERSPACE_IMPLEMENTATION:-amneziawg-go}` (пакета `amneziawg-go` в репо нет).
4. Из UCI собирается конфиг `/tmp/amneziawg/<iface>.conf` (было `/tmp/wireguard` в старом репо), затем `awg setconf`.
5. LuCI status читает `awg show all dump` через rpcd.
