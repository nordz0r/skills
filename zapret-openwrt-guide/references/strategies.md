# Стратегии DPI-обхода в Zapret-OpenWrt

## Общие сведения

Стратегии — это предустановленные наборы параметров NFQWS_OPT, определяющие методы обхода DPI. Каждая стратегия оптимизирована для определённых типов DPI и провайдеров.

Все стратегии определены в файле `def-cfg.sh` (исходник: `zapret/def-cfg.sh`). На роутере: `/opt/zapret/def-cfg.sh`.

### Как выбрать стратегию

1. **Начать с `v6_by_StressOzz`** или **`v7_by_StressOzz`** — они наиболее универсальны и включают Discord/STUN поддержку
2. Проверить работу через **Diagnostics -> Sites check**
3. Если не работает — попробовать другие стратегии
4. Для тонкой настройки — редактировать NFQWS_OPT вручную

### Как применить стратегию

Через LuCI:
1. **Services -> Zapret -> Service -> Reset settings**
2. Выбрать стратегию из выпадающего списка
3. Нажать **Reset settings**
4. Сервис автоматически перезапустится

Через командную строку:
```sh
source /opt/zapret/def-cfg.sh
set_cfg_nfqws_strat "v7_by_StressOzz"
/opt/zapret/sync_config.sh
service zapret restart
```

---

## Подробное описание стратегий

### empty

Пустая стратегия — очищает все NFQWS_OPT. Используется как базовая точка для ручной настройки.

- Порты TCP: 80,443
- Порты UDP: 443
- NFQWS_OPT: пусто

### v1_by_StressOzz

Базовая стратегия с fake + multidisorder для TLS и fake для QUIC.

- **Порты TCP:** 80,443
- **Порты UDP:** 443
- **Секция 1 (TCP 443, Google hostlist):**
  - Метод: `fake,multidisorder`
  - Split: seqovl=681, pos=1
  - Fooling: badseq (increment=10000000)
  - Fake TLS: google_com.bin + mod rnd,dupsid,sni=fonts.google.com
  - Repeats: 2
- **Секция 2 (UDP 443, Google hostlist):**
  - Метод: `fake`
  - Repeats: 6
  - Fake QUIC: quic_initial_www_google_com.bin

### v2_by_StressOzz

Усиленная стратегия с fakeddisorder и двойным fake-TLS.

- **Порты TCP:** 80,443
- **Порты UDP:** 443
- **Секция 1 (TCP 443, Google hostlist):**
  - Метод: `fake,fakeddisorder`
  - Split: pos=10,midsld
  - Двойной fake-tls: google_com.bin (mod rnd,dupsid,sni=fonts.google.com) + 0x0F0F0F0F
  - Fakedsplit pattern: vk_com.bin
  - Seqovl: 336 с паттерном gosuslugi_ru.bin
  - Fooling: badseq,badsum (increment=0)
- **Секция 2 (UDP 443, Google hostlist):**
  - Метод: `fake`, repeats=6

### v3_by_StressOzz

Вариация v2 с другим TLS-шаблоном.

- Идентична v2, но вместо `tls_clienthello_www_google_com.bin` использует `t2.bin`
- Fake-tls-mod: `rnd,dupsid,sni=m.ok.ru` (вместо fonts.google.com)

### v4_by_StressOzz

Стратегия с multisplit и 3 секциями.

- **Порты TCP:** 80,443
- **Порты UDP:** 443
- **Секция 1 (TCP 443, Google hostlist):**
  - Метод: `fake,multisplit`
  - Split: pos=2,sld
  - Двойной fake-tls: 0x0F0F0F0F + google_com.bin (mod rnd,dupsid,sni=google.com)
  - Seqovl: 2108
  - Fooling: badseq
- **Секция 2 (TCP 443, user HOSTLIST):**
  - Метод: `multisplit` (any-protocol=1, cutoff=n5)
  - Seqovl: 582, pos=1
  - Pattern: 4pda.bin
- **Секция 3 (UDP 443, Google hostlist):**
  - Метод: `fake`, repeats=6

### v5_by_StressOzz

Стратегия с IP ID zeroing и multisplit.

- **Порты TCP:** 80,443
- **Порты UDP:** 443
- **Секция 1 (TCP 443, Google hostlist):**
  - `--ip-id=zero`
  - Метод: `multisplit`
  - Seqovl: 681, pos=1
  - Pattern: google_com.bin
- **Секция 2 (TCP 443, user HOSTLIST):**
  - Метод: `fake,fakeddisorder`
  - Split: pos=10,midsld
  - Fake TLS: onetrust_com.bin (mod rnd,dupsid)
  - Fooling: badseq,badsum (increment=0)
- **Секция 3 (UDP 443, Google hostlist):**
  - Метод: `fake`, repeats=6

### v6_by_StressOzz (стратегия по умолчанию)

Расширенная стратегия с поддержкой Discord и STUN.

- **Порты TCP:** 80,443,2053,2083,2087,2096,8443
- **Порты UDP:** 443,19294-19344,50000-50100
- **Секция 1 (TCP 443, Google hostlist):**
  - Метод: `multisplit`
  - Split: pos=1,sniext+1, seqovl=1
- **Секция 2 (TCP 443, user HOSTLIST):**
  - Метод: `hostfakesplit`
  - hostfakesplit-mod: host=rzd.ru
  - midhost: host-2
  - Seqovl: 726
  - Fooling: badsum,badseq (increment=0)
- **Секция 3 (UDP 443, HOSTLIST_NOAUTO):**
  - Метод: `fake`, repeats=6
  - Fake QUIC: quic_initial_www_google_com.bin
- **Секция 4 (UDP 19294-19344,50000-50100):**
  - filter-l7: discord,stun
  - Метод: `fake`, repeats=6
- **Секция 5 (TCP 2053,2083,2087,2096,8443, discord.media):**
  - Метод: `multisplit`
  - Seqovl: 652, pos=2
  - Pattern: google_com.bin

### v7_by_StressOzz

Улучшенная версия v6 с большим количеством повторов.

- **Порты TCP:** 80,443,2053,2083,2087,2096,8443
- **Порты UDP:** 443,19294-19344,50000-50100
- **Секция 1 (TCP 443, Google hostlist):**
  - Метод: `fake,multisplit`
  - Split: pos=2,sld
  - Двойной fake-tls: 0x0F0F0F0F + google_com.bin (mod rnd,dupsid,sni=ggpht.com)
  - Repeats: 8
  - Seqovl: 620
  - Fooling: badsum,badseq
- **Секция 2 (TCP 443, user HOSTLIST):**
  - Метод: `fake,multisplit`
  - Seqovl: 654, pos=1
  - Repeats: 8
  - Fake TLS: onetrust_com.bin
  - Fooling: badseq,badsum (increment=0)
- **Секции 3-5:** аналогичны v6

### v9_by_StressOzz

Вариант с hostfakesplit вместо multisplit для пользовательского списка.

- **Порты TCP:** 80,443,2053,2083,2087,2096,8443
- **Порты UDP:** 443,19294-19344,50000-50100
- **Секция 1 (TCP 443, Google hostlist):**
  - Метод: `fake,multisplit` (как v7)
- **Секция 2 (TCP 443, user HOSTLIST):**
  - Метод: `hostfakesplit`
  - hostfakesplit-mod: host=mapgl.2gis.com
  - Fooling: badseq,badsum (increment=0)
- **Секции 3-5:** аналогичны v6/v7

### ALT7_by_Flowseal

Альтернативная стратегия с ip-id=zero.

- **Порты TCP:** 80,443
- **Порты UDP:** 443
- **Секция 1 (TCP 443, Google hostlist):**
  - `--ip-id=zero`
  - Метод: `multisplit`
  - Split: pos=2,sniext+1
  - Seqovl: 679
  - Pattern: google_com.bin
- **Секция 2 (TCP 80,443, user HOSTLIST):**
  - Метод: `multisplit`
  - Split: pos=2,sniext+1
  - Seqovl: 679
  - Pattern: google_com.bin
- **Секция 3 (UDP 443, Google hostlist):**
  - Метод: `fake`, repeats=6

### TLS_AUTO_ALT3_by_Flowseal

Стратегия с fooling=ts и большим количеством повторов.

- **Порты TCP:** 80,443
- **Порты UDP:** 443
- **Секция 1 (TCP 443, Google hostlist):**
  - `--ip-id=zero`
  - Метод: `fake,multisplit`
  - Seqovl: 681, pos=1
  - Fooling: `ts` (timestamp-based)
  - Repeats: 8
  - Pattern: google_com.bin
  - Fake-tls-mod: rnd,dupsid,sni=www.google.com
- **Секция 2 (TCP 80,443, user HOSTLIST):**
  - Аналогична секции 1
- **Секция 3 (UDP 443, Google hostlist):**
  - Метод: `fake`, repeats=11

---

## Файлы fake-пакетов

Хранятся в `/opt/zapret/files/fake/`:

| Файл | Описание | Используется в |
|------|----------|---------------|
| `tls_clienthello_www_google_com.bin` | TLS ClientHello для google.com | v1, v2, v4-v9, ALT7, TLS_AUTO_ALT3 |
| `tls_clienthello_www_onetrust_com.bin` | TLS ClientHello для onetrust.com | v5, v7 |
| `tls_clienthello_vk_com.bin` | TLS ClientHello для vk.com | v2, v3, v5 |
| `tls_clienthello_gosuslugi_ru.bin` | TLS ClientHello для gosuslugi.ru | v2, v3 |
| `quic_initial_www_google_com.bin` | QUIC Initial для google.com | все стратегии с UDP |
| `t2.bin` | Альтернативный TLS-шаблон | v3 |
| `4pda.bin` | Альтернативный паттерн | v4 |
| `max.bin` | Альтернативный паттерн | не используется в текущих стратегиях |

---

## Создание собственной стратегии

### Через LuCI

1. Выбрать базовую стратегию через Reset settings
2. Перейти на вкладку **Settings -> NFQWS options**
3. Нажать **Edit** рядом с NFQWS_OPT
4. Отредактировать параметры
5. Нажать **Save & Apply**

### Через код (добавление в def-cfg.sh)

Добавить новый блок в функцию `set_cfg_nfqws_strat`:

```sh
if [ "$strat" = "my_custom_strat" ]; then
    uci batch <<-EOF
        set $cfgname.config.NFQWS_PORTS_TCP='80,443'
        set $cfgname.config.NFQWS_PORTS_UDP='443'
        set $cfgname.config.NFQWS_OPT="
            --comment=Strategy__$strat

            --filter-tcp=443 <HOSTLIST>
            --dpi-desync=fake,multisplit
            --dpi-desync-split-pos=2,sld
            --dpi-desync-repeats=8

            --new
            --filter-udp=443 <HOSTLIST_NOAUTO>
            --dpi-desync=fake
            --dpi-desync-repeats=6
            --dpi-desync-fake-quic=/opt/zapret/files/fake/quic_initial_www_google_com.bin
        "
        commit $cfgname
    EOF
fi
```

Стратегия автоматически появится в UI, так как `tools.js` парсит `def-cfg.sh` через awk:
```sh
awk -F'"' '/if \[ "\$strat" = "/ {print $4}' /opt/zapret/def-cfg.sh
```

---

## Сравнение стратегий

| Стратегия | Discord | STUN | Сложность | CPU-нагрузка | Рекомендация |
|-----------|---------|------|-----------|-------------|-------------|
| v1 | Нет | Нет | Низкая | Низкая | Базовый тест |
| v2 | Нет | Нет | Средняя | Средняя | Если v1 не работает |
| v3 | Нет | Нет | Средняя | Средняя | Альтернатива v2 |
| v4 | Нет | Нет | Высокая | Средняя | Сложные DPI |
| v5 | Нет | Нет | Средняя | Средняя | IP ID zeroing |
| **v6** | **Да** | **Да** | **Средняя** | **Средняя** | **Рекомендуемая** |
| **v7** | **Да** | **Да** | **Высокая** | **Выше средней** | **Если v6 нестабильна** |
| v9 | Да | Да | Высокая | Средняя | hostfakesplit вариант |
| ALT7 | Нет | Нет | Средняя | Средняя | Альтернативный подход |
| TLS_AUTO_ALT3 | Нет | Нет | Средняя | Выше средней | Fooling через timestamp |
