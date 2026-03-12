# AmneziaWG OpenWrt: архитектура

## Что именно покрывает upstream

Репозиторий `amneziawg-openwrt` это не desktop/mobile клиент Amnezia, а пакетная интеграция протокола AmneziaWG в OpenWrt.

Он состоит из трех основных пакетов:

- `amneziawg-tools`
- `kmod-amneziawg`
- `luci-proto-amneziawg`

## Роли пакетов

### amneziawg-tools

Дает:

- userspace control binary `awg`;
- `netifd` protocol helper `amneziawg.sh`;
- watchdog для re-resolve endpoint hostnames.

Ключевые файлы:

- `amneziawg-tools/Makefile`
- `amneziawg-tools/files/amneziawg.sh`
- `amneziawg-tools/files/amneziawg_watchdog`

### kmod-amneziawg

Дает kernel module `amneziawg`.

Особенность:

- модуль собирается патчем in-tree WireGuard sources из OpenWrt kernel tree;
- это делает пакет чувствительным к изменениям upstream kernel/WireGuard layout.

Ключевые файлы:

- `kmod-amneziawg/Makefile`
- `kmod-amneziawg/files/000-initial-amneziawg.patch`
- `kmod-amneziawg/src/Makefile`

### luci-proto-amneziawg

Дает:

- LuCI protocol plugin;
- страницу статуса;
- RPC methods для key generation/status;
- ACL/menu integration.

Ключевые файлы:

- `luci-proto-amneziawg/htdocs/luci-static/resources/protocol/amneziawg.js`
- `luci-proto-amneziawg/htdocs/luci-static/resources/view/amneziawg/status.js`
- `luci-proto-amneziawg/root/usr/share/rpcd/ucode/luci.amneziawg`

## Runtime логика

1. `netifd` поднимает интерфейс с `proto 'amneziawg'`.
2. Helper пытается использовать kernel mode.
3. Если module не загрузился, он пытается fallback на `amneziawg-go`.
4. Из UCI строится временный конфиг в `/tmp/wireguard/<iface>`.
5. Бинарник `awg` применяет `setconf`.
6. LuCI status page читает `awg show all dump` через RPC-обвязку.
