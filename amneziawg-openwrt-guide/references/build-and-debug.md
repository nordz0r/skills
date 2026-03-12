# AmneziaWG OpenWrt: сборка и диагностика

## Что нужно на роутере

Минимально:

- `amneziawg-tools`
- `luci-proto-amneziawg`

Обычно также:

- `kmod-amneziawg`

Опционально:

- `qrencode` для QR в LuCI
- `amneziawg-go` для userspace fallback

## Watchdog

`amneziawg_watchdog` предназначен для динамических endpoint hostnames.

Условия нормальной работы:

- peer задан через hostname, а не IP;
- настроен `persistent_keepalive`;
- watchdog запускается по cron.

Пример идеи из комментария upstream:

```sh
* * * * * /usr/bin/amneziawg_watchdog
```

## Практические команды диагностики

```sh
logread | grep amneziawg
awg show all dump
ip link show
ubus call network.interface dump
ifup awg0
ifdown awg0
service network restart
```

Проверки состояния:

- существует ли `/sys/module/amneziawg`;
- установлен ли `awg`;
- не требуется ли `amneziawg-go`;
- есть ли handshakes и transfer counters на status page.

## Kernel vs userspace

Логика helper-а такая:

1. попробовать `modprobe amneziawg`;
2. если модуль появился, использовать kernel mode;
3. иначе искать `amneziawg-go`.

Если `amneziawg-go` не установлен, helper завершится сообщением о необходимости kernel module или userspace implementation.

## Сборка пакетов

Репозиторий оформлен как OpenWrt package tree. Ожидаемый workflow:

```sh
make package/amneziawg-tools/compile V=s
make package/kmod-amneziawg/compile V=s
make package/luci-proto-amneziawg/compile V=s
```

Это подразумевает, что repo подключен в OpenWrt SDK/Buildroot как feed/package source.

## Главные риски для разработчика

- `kmod-amneziawg` зависит от структуры in-tree WireGuard в OpenWrt kernel;
- LuCI и RPC часть надо менять согласованно;
- совместимость с конкретной веткой OpenWrt не расписана явно, так что любые broad claims нужно проверять на target system.
