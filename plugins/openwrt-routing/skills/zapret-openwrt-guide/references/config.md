# Конфигурация Zapret-OpenWrt

## Система конфигурации

Zapret использует **двойную систему конфигурации:**

1. **UCI конфиг** — `/etc/config/zapret` — хранит пользовательские настройки, редактируется через LuCI
2. **Основной конфиг** — `/opt/zapret/config` — используется демоном nfqws при запуске

Синхронизация UCI -> config происходит через скрипт `sync_config.sh` при каждом start/restart сервиса.

### Шаблон конфигурации

Файл `/opt/zapret/config.default` содержит все параметры с комментариями. При установке копируется в `/opt/zapret/config`.

---

## Параметры конфигурации

### Firewall / Сетевой стек

| Параметр | Значения | По умолчанию | Описание |
|----------|----------|-------------|----------|
| FWTYPE | `nftables` | `nftables` | Тип файрвола. В текущей сборке поддерживается только nftables |
| POSTNAT | `0`, `1` | `1` | Режим обработки трафика. `1` = post-NAT (после NAT), `0` = pre-NAT (до NAT, видны IP клиентов в логах) |
| FLOWOFFLOAD | `donttouch`, `none`, `software`, `hardware` | `none` | Режим Flow Offloading. `donttouch` = не менять, `none` = отключить, `software` = программный, `hardware` = аппаратный |
| INIT_APPLY_FW | `0`, `1` | `1` | Применять правила файрвола при start/stop сервиса |

#### POSTNAT: подробности

- **post-NAT** (`POSTNAT=1`, по умолчанию): nfqws обрабатывает пакеты после NAT-трансляции. Работают все техники обхода для forwarded-трафика.
- **pre-NAT** (`POSTNAT=0`): nfqws обрабатывает пакеты до NAT. Позволяет видеть реальные IP клиентов в debug-логе, но отключает некоторые техники обхода.

#### FLOWOFFLOAD: подробности

Flow offloading ускоряет маршрутизацию, но может конфликтовать с nfqws, так как пакеты "проскакивают" мимо NFQUEUE. Рекомендуется `none` для максимальной совместимости.

### IPv4/IPv6

| Параметр | Значения | По умолчанию | Описание |
|----------|----------|-------------|----------|
| DISABLE_IPV4 | `0`, `1` | `0` | Отключить обработку IPv4 трафика |
| DISABLE_IPV6 | `0`, `1` | `1` | Отключить обработку IPv6 трафика (по умолчанию отключен) |
| FILTER_TTL_EXPIRED_ICMP | `0`, `1` | `1` | Блокировать ICMP "time exceeded" для обработанных соединений. В POSTNAT-режиме может мешать traceroute/mtr в TCP/UDP режиме |

### NFQWS — основные параметры

| Параметр | Значения | По умолчанию | Описание |
|----------|----------|-------------|----------|
| NFQWS_ENABLE | `0`, `1` | `1` | Включить/отключить демон nfqws |
| DESYNC_MARK | hex | `0x40000000` | Метка для desync-пакетов (предотвращение loop) |
| DESYNC_MARK_POSTNAT | hex | `0x20000000` | Метка для post-NAT режима |
| FILTER_MARK | hex или пусто | пусто | Дополнительная метка фильтра. Позволяет писать свои правила для ограничения обработки (по source IP, интерфейсу и т.д.) |

### NFQWS — порты и connbytes

| Параметр | Формат | По умолчанию | Описание |
|----------|--------|-------------|----------|
| NFQWS_PORTS_TCP | port,port,... | `80,443` | TCP-порты для обработки |
| NFQWS_PORTS_UDP | port,port,... | `443` | UDP-порты для обработки |
| NFQWS_TCP_PKT_OUT | число | `9` | connbytes лимит: количество исходящих TCP-пакетов для перехвата |
| NFQWS_TCP_PKT_IN | число | `3` | connbytes лимит: количество входящих TCP-пакетов для перехвата |
| NFQWS_UDP_PKT_OUT | число | `9` | connbytes лимит: количество исходящих UDP-пакетов |
| NFQWS_UDP_PKT_IN | число | `0` | connbytes лимит: количество входящих UDP-пакетов |
| NFQWS_PORTS_TCP_KEEPALIVE | port или 0 | `0` | TCP-порты без connbytes-лимита (для stateless DPI, HTTP keep-alive). Потребляет много CPU! |
| NFQWS_PORTS_UDP_KEEPALIVE | port или 0 | `0` | UDP-порты без connbytes-лимита |

#### Что такое connbytes

connbytes — это ядерный механизм, реализующий `--dpi-desync-cutoff=nX` на уровне ядра. Вместо того чтобы пропускать все пакеты через NFQUEUE (что дорого по CPU), connbytes перенаправляет в NFQUEUE только первые N пакетов каждого соединения. Это эффективно, потому что DPI анализирует только начало соединения (handshake, первые данные).

- `PKT_OUT=9` — обрабатывать первые 9 исходящих пакетов (покрывает TLS ClientHello)
- `PKT_IN=3` — обрабатывать первые 3 входящих пакета

### NFQWS_OPT — параметры десинхронизации

Главный параметр — `NFQWS_OPT`. Содержит аргументы командной строки для демона nfqws. Может быть многострочным.

Синтаксис:
```
--filter-tcp=PORT [<HOSTLIST>]
--dpi-desync=METHOD
--dpi-desync-split-pos=POS
...
--new
--filter-udp=PORT
--dpi-desync=METHOD
...
```

Разделитель `--new` создаёт новую секцию правил. Порядок секций важен — пакет обрабатывается первой подходящей секцией.

#### Основные параметры nfqws

| Параметр | Описание |
|----------|----------|
| `--filter-tcp=PORTS` | Фильтр по TCP-портам |
| `--filter-udp=PORTS` | Фильтр по UDP-портам |
| `--filter-l7=PROTO` | Фильтр по L7-протоколу (discord, stun, quic, tls) |
| `--hostlist=FILE` | Список доменов для обработки |
| `--hostlist-exclude=FILE` | Список доменов-исключений |
| `--hostlist-domains=DOMAIN` | Inline-список доменов (через запятую) |
| `--hostlist-exclude-domains=DOMAIN` | Inline-исключения |
| `--dpi-desync=METHOD` | Метод десинхронизации (fake, multisplit, multidisorder, fakeddisorder, hostfakesplit, и т.д.) |
| `--dpi-desync-split-pos=POS` | Позиция разбиения пакета (число, sld, midsld, sniext+N, host+N, endhost-N) |
| `--dpi-desync-split-seqovl=N` | Размер overlapping-сегмента |
| `--dpi-desync-split-seqovl-pattern=FILE` | Файл с паттерном для overlap |
| `--dpi-desync-fake-tls=FILE_OR_HEX` | Файл или hex-паттерн для fake TLS |
| `--dpi-desync-fake-tls-mod=MODS` | Модификации fake TLS (rnd, dupsid, sni=DOMAIN) |
| `--dpi-desync-fake-quic=FILE` | Файл для fake QUIC Initial |
| `--dpi-desync-fakedsplit-pattern=FILE` | Паттерн для fakedsplit |
| `--dpi-desync-fooling=METHOD` | Методы обмана (badsum, badseq, ts) |
| `--dpi-desync-badseq-increment=N` | Инкремент badseq (0 = случайный) |
| `--dpi-desync-repeats=N` | Количество повторов fake-пакетов |
| `--dpi-desync-cutoff=nN` | Прекратить обработку после N-го пакета |
| `--dpi-desync-any-protocol=1` | Обрабатывать любой протокол (не только TLS/HTTP) |
| `--dpi-desync-autottl=N` | Автоматический TTL для fake-пакетов |
| `--dpi-desync-hostfakesplit-mod=host=DOMAIN` | Подмена хоста в hostfakesplit |
| `--dpi-desync-hostfakesplit-midhost=host-N` | Позиция вставки в hostfakesplit |
| `--ip-id=zero` | Установить IP ID в 0 |
| `--comment=TEXT` | Комментарий (для идентификации стратегии в логах) |
| `--new` | Начать новую секцию правил |

### Режим фильтрации

| Параметр | Значения | По умолчанию | Описание |
|----------|----------|-------------|----------|
| MODE_FILTER | `none`, `ipset`, `hostlist`, `autohostlist` | `hostlist` | Режим фильтрации |

- **none** — обрабатывать весь трафик на указанных портах
- **ipset** — фильтрация по IP-адресам из ipset
- **hostlist** — фильтрация по спискам доменов (ручной режим)
- **autohostlist** — автоматическое обнаружение заблокированных хостов

### AutoHostList

Когда `MODE_FILTER=autohostlist`, zapret автоматически определяет заблокированные хосты по паттернам ретрансмиссий и ошибок, добавляя их в `zapret-hosts-auto.txt`.

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| AUTOHOSTLIST_RETRANS_THRESHOLD | `3` | Порог ретрансмиссий TCP для добавления хоста |
| AUTOHOSTLIST_FAIL_THRESHOLD | `3` | Порог неудачных попыток |
| AUTOHOSTLIST_FAIL_TIME | `60` | Окно времени в секундах для подсчёта неудач |
| AUTOHOSTLIST_DEBUGLOG | `0` | Логирование добавлений в `zapret-hosts-auto-debug.log` |

### Логирование демона

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| DAEMON_LOG_ENABLE | `0` | Включить логирование nfqws |
| DAEMON_LOG_SIZE_MAX | `2000` | Максимальный размер лога в КБ. Варианты: 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 7000 |
| DAEMON_LOG_FILE | `/tmp/zapret+<DAEMON_NAME>+<DAEMON_IDNUM>+<DAEMON_CFGNAME>.log` | Шаблон имени лог-файла |

Плейсхолдеры в DAEMON_LOG_FILE:
- `<DAEMON_NAME>` — имя демона (nfqws)
- `<DAEMON_IDNUM>` — номер экземпляра
- `<DAEMON_CFGNAME>` — имя конфига (zapret / zapret2)

Cron-задача автоматически удаляет логи, превышающие DAEMON_LOG_SIZE_MAX.

### Прочие параметры

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| WS_USER | `daemon` | Пользователь для запуска демонов. На Keenetic обычно нужен root |
| DISABLE_CUSTOM | `1` | `1` = отключить custom.d скрипты, `0` = включить |
| SET_MAXELEM | `522288` | Максимальное количество элементов в nft sets |
| MDIG_THREADS | `30` | Количество потоков для DNS-резолвинга через mdig |
| GZIP_LISTS | `0` | Сжатие больших списков |

### Сетевые интерфейсы (опционально)

| Параметр | Описание |
|----------|----------|
| OPENWRT_LAN | Сети, рассматриваемые как LAN (по умолчанию "lan") |
| OPENWRT_WAN4 | Сети WAN для IPv4 (по умолчанию — интерфейсы с default route) |
| OPENWRT_WAN6 | Сети WAN для IPv6 |

### Хуки файрвола (редко используются)

| Параметр | Описание |
|----------|----------|
| INIT_FW_PRE_UP_HOOK | Скрипт перед включением файрвола |
| INIT_FW_POST_UP_HOOK | Скрипт после включения файрвола |
| INIT_FW_PRE_DOWN_HOOK | Скрипт перед отключением файрвола |
| INIT_FW_POST_DOWN_HOOK | Скрипт после отключения файрвола |

---

## Пример конфигурации

Минимальная рабочая конфигурация для обхода блокировок YouTube:

```sh
FWTYPE=nftables
POSTNAT=1
FLOWOFFLOAD=none
DISABLE_IPV4=0
DISABLE_IPV6=1
MODE_FILTER=hostlist
NFQWS_ENABLE=1
NFQWS_PORTS_TCP=80,443
NFQWS_PORTS_UDP=443
NFQWS_TCP_PKT_OUT=9
NFQWS_TCP_PKT_IN=3
NFQWS_UDP_PKT_OUT=9
NFQWS_UDP_PKT_IN=0
NFQWS_OPT="
--filter-tcp=443
--hostlist=/opt/zapret/ipset/zapret-hosts-google.txt
--dpi-desync=fake,multisplit
--dpi-desync-split-pos=2,sld
--dpi-desync-repeats=8
--new
--filter-udp=443
--hostlist=/opt/zapret/ipset/zapret-hosts-google.txt
--dpi-desync=fake
--dpi-desync-repeats=6
--dpi-desync-fake-quic=/opt/zapret/files/fake/quic_initial_www_google_com.bin
"
```
