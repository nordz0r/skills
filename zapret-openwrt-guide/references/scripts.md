# Shell-скрипты Zapret-OpenWrt

## Обзор

Все скрипты расположены в `/opt/zapret/` на роутере.
В исходниках: `zapret/*.sh`.

---

## comfunc.sh — Общие функции

**Размер:** ~248 строк
**Назначение:** Библиотека общих функций, подключается через `source` другими скриптами.

### Константы

```sh
ZAPRET_BASE="/opt/zapret"
ZAPRET_CFG="$ZAPRET_BASE/config"
ZAPRET_CFG_NAME="zapret"
ZAPRET_IPSET="$ZAPRET_BASE/ipset"
```

### Ключевые функции

| Функция | Описание |
|---------|----------|
| `is_valid_config()` | Проверяет синтаксис shell-конфига (`sh -n`) |
| `is_run_via_procd()` | Определяет, запущен ли скрипт через procd |
| `is_run_on_boot()` | Проверяет, это загрузка системы |
| `get_run_on_boot_option()` | Читает UCI-опцию `run_on_boot` |
| `get_distrib_info()` | Получает информацию о дистрибутиве из `/etc/openwrt_release` |
| `init_before_start()` | Инициализация перед запуском: обновление конфига, timestamp LuCI |
| `create_default_cfg()` | Создание дефолтной конфигурации |
| `merge_config()` | Слияние текущего и нового конфига |
| `cron_del_log_task()` | Удаление cron-задачи очистки логов |
| `cron_add_log_task()` | Добавление cron-задачи очистки логов |
| `restore_ipset_files()` | Восстановление файлов ipset |

### Управление PID

```sh
# Чтение PID
read_pid_file(pidfile)

# Проверка процесса
is_process_running(pid)
```

### Патч заголовка LuCI

При обновлении пакета обновляется timestamp в `/usr/share/luci/menu.d/luci-app-zapret.json`, чтобы LuCI подхватил изменения без полного рефреша.

---

## init.d.sh — Init-скрипт (procd)

**Размер:** ~87 строк
**На роутере:** `/etc/init.d/zapret` (симлинк на `/opt/zapret/init.d.sh`)

### Конфигурация procd

```sh
USE_PROCD=1
START=21        # После инициализации сети
```

### Основные действия

| Команда | Описание |
|---------|----------|
| `enable` | Включить автозапуск (через upstream + UCI run_on_boot) |
| `enabled` | Проверить, включен ли автозапуск (exit code 0 = включен) |
| `boot` | Вызывается при загрузке. Проверяет `run_on_boot`, блокирует если отключен |
| `start` | Запуск: вызывает `init_before_start()` + upstream start |
| `restart` | Перезапуск: `init_before_start()` + upstream restart |
| `disable` | Отключить автозапуск |
| `stop` | Остановить сервис |

### Логика загрузки (boot)

```
1. Проверить run_on_boot в UCI
2. Если run_on_boot=0:
   a. Если is_run_on_boot() → заблокировать запуск (exit)
   b. Если не boot → продолжить обычный start
3. Если run_on_boot=1 → запустить сервис
```

---

## sync_config.sh — Синхронизация конфигурации

**Размер:** ~148 строк
**Назначение:** Читает параметры из UCI (`/etc/config/zapret`) и записывает их в основной конфиг (`/opt/zapret/config`).

### Когда вызывается

- Перед каждым `start` / `restart` сервиса
- Из UI при нажатии "Save & Apply"
- Вручную: `/opt/zapret/sync_config.sh`

### Синхронизируемые параметры

```
FWTYPE, POSTNAT, FLOWOFFLOAD, INIT_APPLY_FW
DISABLE_IPV4, DISABLE_IPV6, FILTER_TTL_EXPIRED_ICMP
WS_USER, MODE_FILTER, DISABLE_CUSTOM
NFQWS_ENABLE, DESYNC_MARK, DESYNC_MARK_POSTNAT, FILTER_MARK
NFQWS_PORTS_TCP, NFQWS_PORTS_UDP
NFQWS_TCP_PKT_OUT, NFQWS_TCP_PKT_IN
NFQWS_UDP_PKT_OUT, NFQWS_UDP_PKT_IN
NFQWS_PORTS_TCP_KEEPALIVE, NFQWS_PORTS_UDP_KEEPALIVE
NFQWS_OPT
AUTOHOSTLIST_RETRANS_THRESHOLD, AUTOHOSTLIST_FAIL_THRESHOLD
AUTOHOSTLIST_FAIL_TIME, AUTOHOSTLIST_DEBUGLOG
DAEMON_LOG_ENABLE, DAEMON_LOG_SIZE_MAX, DAEMON_LOG_FILE
```

### Механизм

1. Читает значение из UCI: `uci -q get zapret.config.PARAM`
2. Адаптирует значение для sed (экранирование спецсимволов)
3. Заменяет строку в `/opt/zapret/config` через `sed -i`
4. Проверяет валидность результирующего конфига через `is_valid_config`

---

## def-cfg.sh — Стратегии и дефолты

**Размер:** ~509 строк
**Назначение:** Определяет стратегии DPI-обхода и дефолтные значения конфигурации.

### Функции

| Функция | Описание |
|---------|----------|
| `set_cfg_reset_values(cfgname)` | Установить все базовые параметры в дефолт через UCI batch |
| `clear_nfqws_strat(cfgname)` | Очистить NFQWS_OPT и порты |
| `set_cfg_nfqws_strat(strat, cfgname)` | Применить именованную стратегию |
| `set_cfg_default_values(flags, strat, cfgname)` | Полный сброс с опциями |

### Флаги set_cfg_default_values

Строка `opt_flags` может содержать:
- `(skip_base)` — не сбрасывать базовые настройки
- `(set_mode_autohostlist)` — включить autohostlist
- `(enable_custom_d)` — включить custom.d
- `(disable_custom_d)` — отключить custom.d

Стратегия по умолчанию: `v6_by_StressOzz` (второй аргумент).

---

## restore-def-cfg.sh — Сброс конфигурации

**Размер:** ~40 строк
**Назначение:** Сброс конфигурации к умолчаниям.

### Аргументы

Принимает строку флагов (из UI Reset settings):
- `(skip_base)` — пропустить сброс базовых настроек
- `(reset_ipset)` — восстановить ipset-файлы
- `(set_mode_autohostlist)` — включить autohostlist
- `(erase_autohostlist)` — очистить zapret-hosts-auto.txt
- `(enable_custom_d)` — включить custom.d
- `(sync)` — синхронизировать конфиг после сброса

Второй аргумент: имя стратегии (или `-` для "не менять").

### Пример вызова из UI

```sh
/opt/zapret/restore-def-cfg.sh "(skip_base)(reset_ipset)(set_mode_autohostlist)(sync)" "v7_by_StressOzz"
```

---

## update-pkg.sh — Обновление пакетов

**Размер:** ~570 строк
**Назначение:** Проверка и установка обновлений с GitHub.

### Аргументы

| Флаг | Описание |
|------|----------|
| `-c` | Проверить наличие обновлений |
| `-p` | Включить пререлизы в поиск |
| `-u URL` | Установить пакет по URL |
| `-f` | Принудительная переустановка (даже если версия совпадает) |
| `-t TEST` | Тестовый режим |

### Процесс проверки (`-c`)

1. Определяет CPU-архитектуру из `/etc/openwrt_release` (DISTRIB_ARCH)
2. Скачивает JSON с метаданными релизов: `https://raw.githubusercontent.com/remittor/zapret-openwrt/gh-pages/releases/`
3. Фильтрует по архитектуре и типу пакетов (IPK/APK)
4. Сравнивает с установленной версией
5. Выводит результат: `RESULT: (CODE) message` и `ZAP_PKG_URL = url`

Коды результата:
- `L` — доступна более новая версия
- `E` — установлена текущая версия
- `G` — установлена более новая версия

### Процесс установки (`-u URL`)

1. Скачивает ZIP-архив с GitHub
2. Извлекает пакеты для нужной архитектуры
3. Останавливает сервис
4. Удаляет старые пакеты (`opkg remove` / `apk del`)
5. Устанавливает новые пакеты
6. Запускает сервис
7. Выводит `RESULT: (+) Updated`

### Поддержка менеджеров пакетов

| Менеджер | Формат | Команды |
|----------|--------|---------|
| opkg | .ipk | `opkg remove`, `opkg install` |
| apk | .apk | `apk del`, `apk add --allow-untrusted` |

---

## dwc.sh — DPI-чекер

**Размер:** ~321 строка
**Назначение:** Диагностика DPI и проверка доступности сайтов.

### Аргументы

| Флаг | Описание |
|------|----------|
| `-s` | Режим проверки сайтов (вместо DPI check) |
| `-d IP` | Использовать указанный DNS-резолвер |
| `-R` | Показать рекомендации |

### Режим DPI check (по умолчанию)

Выполняет TCP 16-20 тест:
1. Скачивает тестовый набор с `hyperion-cs.github.io/dpi-checkers`
2. Проверяет ответы от DPI на различные паттерны
3. Определяет тип DPI и уровень блокировки

### Режим Sites check (`-s`)

Проверяет доступность списка заблокированных сайтов:
1. Резолвит DNS (через указанный или системный резолвер)
2. Пытается установить TLS-соединение
3. Выводит результат для каждого сайта

---

## script-exec.sh — Исполнитель скриптов

**Размер:** ~37 строк
**Назначение:** Запуск скриптов в фоне с перенаправлением вывода в лог-файл.

### Синтаксис

```sh
/opt/zapret/script-exec.sh <logfile> <command> [args...]
```

### Механизм

1. Создаёт лог-файл
2. Запускает команду через `start-stop-daemon -b` (фон)
3. Перенаправляет stdout+stderr в лог-файл
4. Записывает код возврата в `<logfile>.rc`

Используется из UI для неблокирующего выполнения `dwc.sh` и `update-pkg.sh`.

---

## renew-cfg.sh — Обновление конфига при загрузке

**Размер:** ~18 строк
**Назначение:** Слияние конфига с дефолтами и синхронизация.

### Что делает

1. Вызывает `merge_config()` — добавляет недостающие параметры из `config.default`
2. Вызывает `sync_config.sh` — синхронизирует UCI -> config

Вызывается при загрузке системы для обеспечения совместимости после обновления.

---

## uci-def-cfg.sh — Создание UCI-конфига

**Размер:** ~22 строки
**Назначение:** Создание начальной UCI-конфигурации при установке пакета.

### Что делает

1. Создаёт пустые ipset-файлы (если не существуют)
2. Вызывает `merge_config()` для инициализации
3. Вызывается из `postinst` скрипта Makefile
