# AmneziaWG OpenWrt: пакеты, обновление, диагностика

Источник: `Slava-Shchipunov/awg-openwrt` @ 03b6226 (README, `docs/custom-feed.md`, Makefile'ы), сверено 2026-10-15.

## Пакетный менеджер

| OpenWrt | Менеджер | Откуда |
|---|---|---|
| 23.05.x, 24.10.x | `opkg`, `.ipk` | GitHub Releases тега `v<версия OpenWrt>` под свой target/subtarget |
| 25.12.x и новее | `apk`, `.apk` | apk-feed GitHub Pages `https://slava-shchipunov.github.io/awg-openwrt/<ver>/<target>/<subtarget>/packages.adb` с ключом `/etc/apk/keys/awg-openwrt-feed.pem`; либо `.apk` из Releases |

- Проверка установленного: `apk list -I | grep -i amnezia` (25.x) / `opkg list-installed | grep -i amnezia` (≤24.10).
- AWG 3.1 есть только в сборках `v24.10.8` и `v25.12.5` (и новее); на другой версии OpenWrt пакеты 3.1 не встанут — сначала обнови прошивку до версии, под которую есть сборка, либо собери сам.
- Обновлять все три пакета вместе и одной версией; kmod строго под ядро прошивки.
- Скрипт `amneziawg-install.sh` из README ставит пакеты и **может создать интерфейс и включить весь трафик через туннель** (`route_allowed_ips`). На рабочем роутере — только вручную, с бэкапом `/etc/config/network` и `firewall`.

## Диагностика (только чтение)

```sh
logread | grep -i amneziawg
awg show all | grep -vE 'private key|preshared key'
ls /sys/module/amneziawg          # kernel mode?
ubus call network.interface.awg0 status
```

| Симптом | Где смотреть |
|---|---|
| `Please install either kernel module…` | `kmod-amneziawg` не встал/не той версии ядра; нет `amneziawg-go` |
| `Invalid argument` при подъёме | параметры новее пакетов (3.x на 2.0-пакетах); S < 12 при HPK; пересечение H — см. `amnezia-vpn/references/troubleshooting.md` |
| нет handshake | shared-параметры не совпадают с сервером (`amnezia-vpn`), endpoint/порт, часы |
| `Message too long` в `awg show` | длинная цепочка `awg_i1…i5` (kmod, `-EMSGSIZE`) |
| endpoint по имени не переразрешается | `amneziawg_watchdog` по cron (`* * * * * /usr/bin/amneziawg_watchdog`; в комментарии скрипта по ошибке указан `wireguard_watchdog`) + `persistent_keepalive` |

## Сборка

Репо — OpenWrt package tree; GitHub Actions собирает по тегу `vX.Y.Z` (версия OpenWrt) или по workflow_dispatch с target/subtarget.
Локально в SDK: `make package/{kmod-amneziawg,amneziawg-tools,luci-proto-amneziawg}/compile V=s`.
