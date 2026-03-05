# Веб-интерфейс LuCI для Zapret-OpenWrt

## Общая структура

LuCI-интерфейс доступен по пути: **Services -> Zapret**

Меню определено в `luci-app-zapret/root/usr/share/luci/menu.d/luci-app-zapret.json`.
ACL-права — в `luci-app-zapret/root/usr/share/rpcd/acl.d/luci-app-zapret.json`.

### Файловая структура UI

```
luci-app-zapret/htdocs/luci-static/resources/view/zapret/
├── env.js          # Константы: пути, имена файлов, URL
├── tools.js        # Утилиты: RPC, POLLER, диалоги, decode
├── service.js      # Страница "Service" (управление)
├── settings.js     # Страница "Settings" (настройки)
├── diagnost.js     # Модуль диагностики (модальное окно)
├── updater.js      # Модуль обновления (модальное окно)
├── dmnlog.js       # Страница "Log" (логи)
└── styles.css      # Стили
```

---

## Страница Service (service.js)

Главная страница управления сервисом.

### Элементы интерфейса

**Заголовок:**
- Название пакета и версия (например: "Zapret v72.20260226")
- Ссылки на upstream и fork репозитории
- Предупреждение, если версии zapret и luci-app-zapret не совпадают

**Блок статуса (таблица):**
- CPU architecture — архитектура процессора роутера
- Service autorun status — Enabled/Disabled
- Service daemons status — Running [N/M] / Stopped / Starting

**Кнопки управления:**

| Кнопка | Действие | Описание |
|--------|----------|----------|
| Enable | `callInitAction('zapret', 'enable')` | Включить автозапуск |
| Disable | `callInitAction('zapret', 'disable')` | Отключить автозапуск |
| Start | sync_config.sh + start | Синхронизировать конфиг и запустить |
| Restart | sync_config.sh + restart | Синхронизировать и перезапустить |
| Stop | stop | Остановить сервис |
| Reset settings | Модальное окно | Сброс настроек к умолчаниям |
| Diagnostics | Модальное окно diagnost.js | DPI-проверка и тест сайтов |
| Upgrade... | Модальное окно updater.js | Проверка и установка обновлений |

### Модальное окно Reset settings

Опции сброса:
- **Restore all base settings** (чекбокс, по умолчанию вкл) — сбросить все основные параметры
- **Restore ipset configs** (чекбокс, по умолчанию вкл) — восстановить файлы списков
- **Set AutoHostList mode** (чекбокс, по умолчанию вкл) — включить autohostlist
- **Erase AutoHostList (ipset)** (чекбокс, по умолчанию выкл) — очистить zapret-hosts-auto.txt
- **Enable use custom.d scripts** (чекбокс, по умолчанию выкл) — включить custom.d
- **NFQWS_OPT strategy** (выпадающий список) — выбор стратегии или "not change"

Кнопки: **Reset settings** | **Cancel**

### Поллинг статуса

Сервис использует класс POLLER для периодического обновления статуса:
- Интервал: 2 секунды
- Первый опрос: через 500мс после загрузки
- Не обновляет страницу, когда открыто модальное окно
- Отображает количество работающих демонов [working/total]

### Deferred actions

При нажатии Start/Restart, если есть несохранённые изменения в UCI:
1. Сначала применяются UCI-изменения (`ui.changes.apply`)
2. Действие сохраняется в localStorage как "deferred action"
3. При следующей загрузке страницы deferred action выполняется автоматически

---

## Страница Settings (settings.js)

Форма настроек на основе `form.Map` с 5 вкладками.

### Вкладка "Main settings"

| Параметр | Тип элемента | Описание |
|----------|-------------|----------|
| FWTYPE | ListValue | Тип файрвола (только nftables) |
| POSTNAT | Flag (чекбокс) | Post-NAT режим |
| FLOWOFFLOAD | ListValue | Flow offloading (donttouch/none/software/hardware) |
| INIT_APPLY_FW | Flag | Применять правила FW при start/stop |
| DISABLE_IPV4 | Flag | Отключить IPv4 |
| DISABLE_IPV6 | Flag | Отключить IPv6 |
| FILTER_TTL_EXPIRED_ICMP | Flag | Фильтрация ICMP TTL exceeded |
| WS_USER | Value (текст) | Пользователь для демонов |
| DAEMON_LOG_ENABLE | Flag | Включить логирование |
| DAEMON_LOG_SIZE_MAX | ListValue | Максимальный размер лога (КБ) |

### Вкладка "NFQWS options"

| Параметр | Тип элемента | Описание |
|----------|-------------|----------|
| NFQWS_ENABLE | Flag | Включить nfqws |
| DESYNC_MARK | Value | Метка desync |
| DESYNC_MARK_POSTNAT | Value | Метка post-NAT |
| FILTER_MARK | Value | Метка фильтра |
| NFQWS_PORTS_TCP | Value | TCP-порты |
| NFQWS_PORTS_UDP | Value | UDP-порты |
| NFQWS_TCP_PKT_OUT | Value | Connbytes TCP out |
| NFQWS_TCP_PKT_IN | Value | Connbytes TCP in |
| NFQWS_UDP_PKT_OUT | Value | Connbytes UDP out |
| NFQWS_UDP_PKT_IN | Value | Connbytes UDP in |
| NFQWS_PORTS_TCP_KEEPALIVE | Value (uinteger) | TCP keepalive порты |
| NFQWS_PORTS_UDP_KEEPALIVE | Value (uinteger) | UDP keepalive порты |
| NFQWS_OPT | TextValue + Edit диалог | Параметры desync (многострочный) |

**Редактирование NFQWS_OPT:**
- Отображается как read-only textarea
- Кнопка "Edit" открывает `longstrEditDialog`
- Многострочный режим (multiline=2): каждый `--параметр` на отдельной строке
- Ссылка на справку: https://github.com/remittor/zapret-openwrt/discussions/168
- Нельзя использовать кавычки в тексте (ограничение UCI)

### Вкладка "AutoHostList"

| Параметр | Тип элемента | Описание |
|----------|-------------|----------|
| MODE_FILTER | Flag | Включить AutoHostList (переключает hostlist <-> autohostlist) |
| AUTOHOSTLIST_RETRANS_THRESHOLD | Value (uinteger) | Порог ретрансмиссий |
| AUTOHOSTLIST_FAIL_THRESHOLD | Value (uinteger) | Порог неудач |
| AUTOHOSTLIST_FAIL_TIME | Value (uinteger) | Временное окно (сек) |
| Auto host list entries | Button -> fileEditDialog | Редактор zapret-hosts-auto.txt |
| AUTOHOSTLIST_DEBUGLOG | Flag | Логирование автохостлиста |
| Auto host debug list entries | Button -> fileEditDialog | Просмотр zapret-hosts-auto-debug.log |

### Вкладка "Host lists"

Кнопки для редактирования файлов через модальные диалоги:

| Элемент | Файл | Формат |
|---------|------|--------|
| Google hostname entries | zapret-hosts-google.txt | Домен на строку |
| User hostname entries `<HOSTLIST>` | zapret-hosts-user.txt | Домен на строку |
| User excluded hostname entries | zapret-hosts-user-exclude.txt | Домен на строку |
| Excluded IP entries | zapret-ip-exclude.txt | IP/CIDR на строку |
| User IP entries | zapret-ip-user.txt | IP/CIDR на строку |
| User excluded IP entries | zapret-ip-user-exclude.txt | IP/CIDR на строку |
| Custom file #1..#4 | cust1.txt...cust4.txt | Произвольный |

### Вкладка "custom.d"

| Элемент | Описание |
|---------|----------|
| Use custom.d scripts | Flag (инвертированный DISABLE_CUSTOM) |
| custom.d script #10 | Ранний init |
| custom.d script #20 | Ранняя основная фаза |
| custom.d script #50 | Основная фаза (Discord/STUN пример) |
| custom.d script #60 | Поздняя основная фаза |
| custom.d script #90 | Финальная фаза |

Для скрипта #50 отображаются ссылки на примеры Discord-скриптов из upstream.

### Save & Apply

При нажатии "Save & Apply":
1. Сохраняются UCI-изменения
2. Проверяются несохранённые изменения
3. Если есть — `ui.changes.apply()` + deferred restart
4. Если нет — сразу restart (если сервис инициализирован)

---

## Модуль Diagnostics (diagnost.js)

Модальное окно с инструментами диагностики.

### Элементы

- **Resolve IP-Addr via** — выбор DNS-резолвера:
  - default (системный)
  - 8.8.8.8, 8.8.4.4 (Google)
  - 1.1.1.1, 1.0.0.1 (Cloudflare)
  - 9.9.9.9, 149.112.112.112 (Quad9)
  - 208.67.222.222, 208.67.220.220 (OpenDNS)
  - 8.26.56.26, 8.20.247.20 (Comodo)
  - 64.6.64.6, 64.6.65.6 (Verisign)

- **Текстовое поле** — вывод результатов (monospace, readonly)

### Кнопки

| Кнопка | Действие | Описание |
|--------|----------|----------|
| Sites check | `dwc.sh -s [-d DNS]` | Проверка доступности сайтов |
| DPI check | `dwc.sh [-d DNS]` | Проверка DPI (TCP 16-20 тест) |
| Cancel | Закрыть | Закрыть диалог |

### Как работает

1. Вызывает `script-exec.sh` с аргументами `dwc.sh`
2. Скрипт выполняется в фоне
3. UI поллит лог-файл `/tmp/zapret_dwc.log` каждые 500мс
4. Результаты отображаются в textarea в реальном времени
5. По завершении выводится разделитель `========`

---

## Модуль Updater (updater.js)

Модальное окно обновления пакетов.

### Элементы

- **Exclude PreReleases** (чекбокс, по умолчанию вкл) — исключить пререлизы
- **Forced reinstall packages** (чекбокс, по умолчанию выкл) — принудительная переустановка
- **Текстовое поле** — лог обновления (monospace, readonly)

### Кнопки

| Кнопка | Действие | Описание |
|--------|----------|----------|
| Check | `update-pkg.sh -c [-p]` | Проверить наличие обновлений |
| Install / Reinstall | `update-pkg.sh -u URL [-f]` | Установить обновление |
| Cancel | Закрыть | Закрыть диалог |

### Stages (внутренние состояния)

| Stage | Check | Install | Cancel | Описание |
|-------|-------|---------|--------|----------|
| 0 | Вкл | Выкл | Вкл | Начальное состояние |
| 1 | Выкл | Выкл | Вкл | Проверка идёт |
| 2 | Вкл | Вкл | Вкл | Обновление доступно |
| 3 | Выкл | Выкл | Выкл | Установка идёт |
| 8 | Выкл | Выкл | Вкл | Ожидание |
| 9+ | Выкл | Выкл | Выкл | Установка завершена |

### Результаты проверки

Скрипт `update-pkg.sh -c` возвращает строку `RESULT: (CODE) ...`:
- `(E)` — Установлена та же версия (кнопка меняется на "Reinstall")
- `(G)` — Установлена более новая версия
- Другое — Доступно обновление

URL пакета извлекается из строки `ZAP_PKG_URL = ...`.

---

## Страница Log (dmnlog.js)

Просмотр логов демонов nfqws.

### Как работает

1. Ищет файлы `/tmp/zapret+*.log`
2. Приоритизирует файл `*+main.log`
3. Каждый лог отображается во вкладке
4. Имя вкладки формируется из имени файла (например: `nfqws 0 zapret`)
5. Polling каждую секунду обновляет содержимое

### Элементы

- Вкладки (tabs) — по одной на каждый лог-файл
- Кнопка **Scroll to tail** — перейти к концу лога
- Кнопка **Scroll to head** — перейти к началу
- Textarea — содержимое лога (readonly, monospace, max-height: 50vh)

### Условия работы

Логи появляются только если:
- `DAEMON_LOG_ENABLE=1` в конфигурации
- Сервис запущен и демоны работают
- Файлы логов существуют в `/tmp/`

Если логи не найдены, показывается сообщение с указанием причины.

---

## Утилиты (tools.js)

### Ключевые компоненты

#### RPC-вызовы

```javascript
callServiceList(name, verbose)  // Список сервисов procd
callInitState(name)              // Состояние init-скрипта
callInitAction(name, action)     // Действие (enable/disable/start/stop/restart)
```

#### POLLER

Класс для периодического опроса с защитой от overlapping:
```javascript
let poll = new tools.POLLER({ });
poll.init(callback, 2000);  // интервал 2 сек
poll.start(500);             // первый вызов через 500мс
poll.stop();                 // остановить
poll.stopAndWait();          // остановить и дождаться завершения текущего вызова
```

Два режима:
- `mode=0` — стандартный (running сбрасывается автоматически)
- `mode=1` — ручной (running сбрасывается вручную, блокирует новые вызовы)

#### fileEditDialog

Диалог для редактирования файлов на роутере:
```javascript
new tools.fileEditDialog({
    file: '/opt/zapret/ipset/zapret-hosts-user.txt',
    title: 'User entries',
    desc: 'One hostname per line.',
    rows: 15,
}).show();
```

Особенности:
- Запись через temp-файл + mv (атомарная)
- Чанковая запись (по 8000 байт) для больших файлов
- Установка прав 644 после записи

#### longstrEditDialog

Диалог для редактирования UCI-строк (например, NFQWS_OPT):
```javascript
new tools.longstrEditDialog({
    cfgsec: 'config',
    cfgparam: 'NFQWS_OPT',
    title: 'NFQWS_OPT',
    rows: 21,
    multiline: 2,  // каждый --param на отдельной строке
}).show();
```

Ограничения:
- Нельзя использовать кавычки (`"`) в multiline=2 режиме
- Символы `˂` и `˃` заменяются на `<` и `>` при сохранении

#### execAndRead

Асинхронный исполнитель скриптов с поллингом вывода:
```javascript
tools.execAndRead({
    cmd: ['/opt/zapret/dwc.sh', '-s'],
    log: '/tmp/zapret_dwc.log',
    logArea: textarea_element,
    callback: callbackFn,
    ctx: this,
    hiderow: [/regex/],
});
```

Механизм:
1. Создаёт rc-файл и лог-файл
2. Запускает скрипт через `script-exec.sh` в фоне
3. Поллит rc-файл и лог каждые 500мс
4. Обновляет textarea с новыми данными
5. Возвращает результат через callback

#### decode_svc_info

Декодирует информацию о сервисе из procd:
```javascript
{
    autorun: true/false,
    dmn: {
        inited: true/false,    // сервис зарегистрирован в procd
        total: N,               // всего демонов
        running: N,             // демонов со статусом running
        working: N,             // демонов с реально работающим PID
    },
    status: statusDict.running  // текущий статус
}
```

### Константы (env.js)

```javascript
appName           : 'zapret'
AppName           : 'Zapret'
execPath          : '/etc/init.d/zapret'
appDir            : '/opt/zapret'
syncCfgPath       : '/opt/zapret/sync_config.sh'
defCfgPath        : '/opt/zapret/def-cfg.sh'
defaultCfgPath    : '/opt/zapret/restore-def-cfg.sh'

// Host lists
hostsGoogleFN     : '/opt/zapret/ipset/zapret-hosts-google.txt'
hostsUserFN       : '/opt/zapret/ipset/zapret-hosts-user.txt'
hostsUserExcludeFN: '/opt/zapret/ipset/zapret-hosts-user-exclude.txt'
autoHostListFN    : '/opt/zapret/ipset/zapret-hosts-auto.txt'
autoHostListDbgFN : '/opt/zapret/ipset/zapret-hosts-auto-debug.log'

// IP lists
iplstExcludeFN    : '/opt/zapret/ipset/zapret-ip-exclude.txt'
iplstUserFN       : '/opt/zapret/ipset/zapret-ip-user.txt'
iplstUserExcludeFN: '/opt/zapret/ipset/zapret-ip-user-exclude.txt'

// Custom files
custFileMax       : 4
custFileTemplate  : '/opt/zapret/ipset/cust%s.txt'
customdPrefixList : [10, 20, 50, 60, 90]
customdFileFormat : '/opt/zapret/init.d/openwrt/custom.d/%s-script.sh'

// Package manager (определяется динамически)
packager.name     : 'apk' или 'opkg'
```

---

## Поддержка zapret2

UI поддерживает второй экземпляр zapret через `appName='zapret2'`. При этом:
- Все параметры получают префикс NFQWS2_ (NFQWS2_ENABLE, NFQWS2_PORTS_TCP и т.д.)
- Появляются дополнительные параметры AutoHostList (INCOMING_MAXSEQ, RETRANS_MAXSEQ, RETRANS_RESET, UDP_IN, UDP_OUT)
- Файлы конфигурации и логов используют суффикс zapret2
