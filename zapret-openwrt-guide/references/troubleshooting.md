# Решение проблем Zapret-OpenWrt

## Диагностика

### Шаг 1: Проверить статус сервиса

**Через LuCI:**
Services -> Zapret -> Service

Статус должен показывать:
- Service autorun status: **Enabled**
- Service daemons status: **Running [N/N]**

**Через SSH:**
```sh
service zapret status
ps | grep nfqws
```

### Шаг 2: Включить логирование

1. Settings -> Main settings -> DAEMON_LOG_ENABLE = Вкл
2. Save & Apply
3. Перейти на вкладку Log
4. Смотреть логи nfqws в реальном времени

### Шаг 3: Запустить диагностику

1. Service -> Diagnostics
2. Выбрать DNS (рекомендуется 8.8.8.8 или 1.1.1.1)
3. Нажать **Sites check** — проверить доступность сайтов
4. Нажать **DPI check** — определить тип DPI

---

## Типичные проблемы

### Сервис не запускается

**Симптом:** Status = Stopped после нажатия Start

**Проверить:**
1. Конфиг валиден: `sh -n /opt/zapret/config` (должен вернуть 0)
2. nfqws существует: `ls -la /opt/zapret/nfq/nfqws`
3. Модули ядра загружены:
   ```sh
   lsmod | grep nft
   lsmod | grep nfnetlink_queue
   ```
4. Достаточно памяти: `free`
5. Логи ошибок: `logread | grep zapret`

**Решения:**
- Если конфиг невалиден: Reset settings через UI или `/opt/zapret/restore-def-cfg.sh "(sync)" "v6_by_StressOzz"`
- Если модули не загружены: `opkg install kmod-nft-queue kmod-nft-nat`
- Если недостаточно памяти: уменьшить SET_MAXELEM, отключить IPv6

### Сервис работает, но сайты не открываются

**Проверить:**
1. Правильные порты в NFQWS_PORTS_TCP/UDP
2. Домены добавлены в списки (zapret-hosts-google.txt или zapret-hosts-user.txt)
3. Домен не в списке исключений (zapret-hosts-user-exclude.txt)
4. NFQWS_OPT не пустой
5. MODE_FILTER = hostlist (или autohostlist)

**Решения:**
- Попробовать другую стратегию (Reset settings -> выбрать другую)
- Добавить домен в zapret-hosts-user.txt
- Включить autohostlist для автоматического обнаружения
- Проверить DNS: Diagnostics с разными DNS-серверами

### YouTube не работает

**Частые причины:**
1. Отсутствуют домены в zapret-hosts-google.txt
2. QUIC (UDP 443) не обрабатывается
3. Недостаточно repeats для fake-пакетов

**Решения:**
1. Проверить содержимое zapret-hosts-google.txt (должны быть youtube.com, googlevideo.com и т.д.)
2. Убедиться, что NFQWS_PORTS_UDP включает 443
3. Попробовать стратегию v7 (больше repeats)
4. Увеличить NFQWS_UDP_PKT_OUT (например, до 15)

### Discord голосовые каналы не работают

**Причина:** Нужна поддержка STUN/Discord UDP портов.

**Решения:**
1. Использовать стратегию v6/v7/v9 (включают Discord-порты)
2. Проверить, что UDP порты включают: `443,19294-19344,50000-50100`
3. Проверить, что TCP порты включают: `2053,2083,2087,2096,8443`
4. Включить custom.d скрипт #50 (STUN4ALL)

### Версии zapret и luci-app-zapret не совпадают

**Симптом:** Красная надпись "LuCI APP vX.X [ incorrect version! ]"

**Решение:**
1. Service -> Upgrade... -> Check -> Install
2. Или принудительная переустановка: включить "Forced reinstall packages" -> Check -> Install
3. После установки обновить страницу (F5)

### Ошибка при обновлении

**Симптомы:** Ошибки при установке пакетов

**Проверить:**
1. Интернет-соединение работает
2. Достаточно места: `df -h /tmp && df -h /overlay`
3. Правильная архитектура: посмотреть в Service -> CPU architecture

**Решения:**
- Освободить место в /tmp и /overlay
- Попробовать вручную через SSH: `/opt/zapret/update-pkg.sh -c`
- Принудительная переустановка: `/opt/zapret/update-pkg.sh -u URL -f`

### Высокая нагрузка на CPU

**Причины:**
1. KEEPALIVE-порты включены (NFQWS_PORTS_TCP_KEEPALIVE)
2. Слишком много repeats в стратегии
3. Обрабатывается весь трафик (MODE_FILTER=none)
4. FLOWOFFLOAD отключён

**Решения:**
1. Отключить KEEPALIVE (установить 0)
2. Уменьшить repeats (6-8 обычно достаточно)
3. Включить hostlist/autohostlist вместо none
4. Попробовать FLOWOFFLOAD=software
5. Уменьшить connbytes: PKT_OUT=5, PKT_IN=2

### Сайты стали медленнее

**Причины:**
1. Слишком большие connbytes (PKT_OUT/PKT_IN)
2. Неоптимальные параметры desync
3. Конфликт с FLOWOFFLOAD

**Решения:**
1. Уменьшить PKT_OUT до 5-7
2. Попробовать другую стратегию
3. Если FLOWOFFLOAD=software/hardware — попробовать none

### Ошибка "text cannot contain quotes!"

**Причина:** При редактировании NFQWS_OPT через UI нельзя использовать кавычки (`"`).

**Решение:** Убрать кавычки из параметров. Значения параметров nfqws не требуют кавычек.

### AutoHostList не работает / пустой

**Проверить:**
1. MODE_FILTER = autohostlist (вкладка AutoHostList, чекбокс включён)
2. Пороговые значения адекватны (RETRANS_THRESHOLD=3, FAIL_THRESHOLD=3)
3. AUTOHOSTLIST_DEBUGLOG = 1 для диагностики

**Решения:**
1. Включить autohostlist: Settings -> AutoHostList -> Use AutoHostList mode
2. Попробовать снизить пороги (RETRANS_THRESHOLD=2, FAIL_THRESHOLD=2)
3. Проверить debug-лог: Settings -> AutoHostList -> Auto host debug list entries

### Конфигурация сбрасывается при обновлении

**Это нормальное поведение:** Файлы конфигурации помечены как `conffiles` в Makefile, но при крупных обновлениях конфиг может обновиться.

**Решения:**
1. Записать свои настройки перед обновлением
2. Бэкапить `/etc/config/zapret` и `/opt/zapret/ipset/zapret-hosts-user.txt`
3. После обновления восстановить через Reset settings + ручную правку

---

## Полезные команды SSH

```sh
# Статус сервиса
service zapret status

# Перезапуск
service zapret restart

# Логи
logread | grep zapret
cat /tmp/zapret+*.log

# Проверка процессов nfqws
ps | grep nfqws

# Ручная синхронизация конфига
/opt/zapret/sync_config.sh

# Сброс к дефолтам
/opt/zapret/restore-def-cfg.sh "(sync)" "v6_by_StressOzz"

# Проверка обновлений
/opt/zapret/update-pkg.sh -c

# Проверка конфига
sh -n /opt/zapret/config && echo "OK" || echo "INVALID"

# Просмотр nft-правил
nft list ruleset | grep -i zapret

# DPI-проверка
/opt/zapret/dwc.sh -d 8.8.8.8

# Проверка сайтов
/opt/zapret/dwc.sh -s -d 8.8.8.8
```

---

## FAQ

**Q: Zapret — это VPN?**
A: Нет. Zapret не меняет IP-адрес и не шифрует трафик. Он модифицирует пакеты, чтобы обмануть DPI.

**Q: Какую стратегию выбрать?**
A: Начните с v6_by_StressOzz. Если не работает — v7. Если нужен только YouTube без Discord — можно попробовать v1-v5.

**Q: Можно ли использовать два экземпляра zapret?**
A: Да, проект поддерживает zapret2 как второй экземпляр с отдельной конфигурацией.

**Q: Как добавить свой сайт в обработку?**
A: Settings -> Host lists -> User hostname entries -> Edit -> добавить домен -> Save. Затем Restart сервиса.

**Q: Безопасно ли обновлять через UI?**
A: Да, обновление через UI (Service -> Upgrade) безопасно. Конфигурация сохраняется.

**Q: Почему IPv6 отключен по умолчанию?**
A: На многих роутерах IPv6-трафик не проходит через DPI, поэтому обработка не нужна. Если у вас IPv6 блокируется — включите DISABLE_IPV6=0.
