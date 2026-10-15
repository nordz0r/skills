<!-- Russian original of SKILL.md (frontmatter omitted). Paths are relative to the skill root. Canonical English version: ../SKILL.md -->

# AmneziaWG на OpenWrt

Только OpenWrt-слой: пакеты, имена UCI/LuCI, runtime на роутере, диагностика.
**Смысл параметров обфускации и выбор значений — скилл `amnezia-vpn`** (`awg-protocol.md`, `awg-config.md`); здесь не дублируется.

Апстрим: `Slava-Shchipunov/awg-openwrt` @ 03b6226 (2026-09-23, AWG 3.1). `amnezia-vpn/amneziawg-openwrt` заброшен с 2024-03 (только AWG 1.0). Сверено 2026-10-15.

## Порядок

1. Сначала чтение: версия OpenWrt, пакетный менеджер (apk на 25.x, opkg на ≤24.10), версии `kmod-amneziawg`/`amneziawg-tools`/`luci-proto-amneziawg` → `references/build-and-debug.md`.
2. Версия протокола пакетов (3.1 — сборки `v24.10.8` / `v25.12.5`+) ≥ версии параметров в конфиге.
3. Перенос конфига в UCI → `references/uci-model.md`; значения — по `amnezia-vpn`.
4. Диагностика: kernel/userspace, `logread`, `awg show` с фильтром ключей, handshake.
5. Изменения интерфейсов, пиров, ключей, пакетов — только с явного согласия, с бэкапом `/etc/config/network`.

## Ключевое

- Пакеты собираются из официальных исходников `amnezia-vpn` по тегу; kmod — строго под ядро прошивки.
- UCI 3.x: `awg_header_protection_key`, `awg_content_padding_addition`, таймеры `awg_rekey_after_time` и др., 3.1 — `awg_random_trailers`, `awg_disable_cookies` (boolean).
- Конфиг в runtime — `/tmp/amneziawg/<iface>.conf`; QR — через `luci-lib-uqr`.
- `amneziawg-install.sh` может завернуть весь трафик в туннель — не запускать на рабочем роутере без контроля.
- Не выводить `private_key`, `preshared_key`, `awg_header_protection_key`.
