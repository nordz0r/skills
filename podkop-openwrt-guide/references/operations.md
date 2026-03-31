# Podkop: эксплуатация

## Совместимость и ограничения

- OpenWrt `24.10+`.
- Минимум `25 MB` свободного flash; install script отдельно проверяет overlay.
- `sing-box` ≥ 1.12.0, `jq` ≥ 1.7.1, `coreutils-base64` ≥ 9.7.
- Проект в активной разработке, формат конфига может меняться между релизами.
- Dashboard (YACD) работает только по HTTP. Не через HTTPS и не через доменное имя.
- IPv6 пока не реализован.

## Конфликты и зависимости

Конфликтующие пакеты (из `podkop/Makefile`):

- `https-dns-proxy`
- `nextdns`
- `luci-app-passwall`
- `luci-app-passwall2`

README отдельно требует удалить `Getdomains`.

Runtime зависимости:

- `sing-box` (≥ 1.12.0) — ядро проксирования
- `curl` — скачивание списков
- `jq` (≥ 1.7.1) — работа с JSON
- `kmod-nft-tproxy` — модуль ядра для tproxy
- `coreutils-base64` (≥ 9.7) — кодирование/декодирование
- `bind-dig` — DNS-утилиты

## Установка и обновление

```sh
PODKOP_REF="<pinned-tag-or-commit>"
curl -fsSL -o /tmp/podkop-install.sh \
  "https://raw.githubusercontent.com/itdoginfo/podkop/${PODKOP_REF}/install.sh"
sed -n '1,200p' /tmp/podkop-install.sh
sh /tmp/podkop-install.sh
```

Перед запуском зафиксируй `PODKOP_REF`, сверь release notes/commit и не выполняй удалённый install script напрямую с плавающей ветки `main`.

Если есть возможность, предпочитай скачать release-артефакты и install script на доверенной машине, проверить checksum/содержимое и только потом переносить их на роутер для установки.

Скрипт:

- определяет `opkg` или `apk`;
- тянет последние `ipk/apk` с GitHub Releases (до 3 попыток на пакет);
- проверяет DNS, свободное место, версию OpenWrt, rate limit GitHub;
- определяет старый конфиг (v0.7.0) и предлагает бэкап/сброс;
- устанавливает `podkop` и `luci-app-podkop`;
- включает сервис Podkop.

## Миграция конфига 0.7.0

Начиная с `0.7.0` структура `/etc/config/podkop` несовместима со старыми значениями.

```sh
PODKOP_REF="<same-pinned-tag-or-commit>"
mv /etc/config/podkop /etc/config/podkop-070
curl -fsSL -o /tmp/podkop.config \
  "https://raw.githubusercontent.com/itdoginfo/podkop/${PODKOP_REF}/podkop/files/etc/config/podkop"
sed -n '1,120p' /tmp/podkop.config
cp /tmp/podkop.config /etc/config/podkop
```

После этого настрой Podkop заново через LuCI или UCI.

## Основные файлы на роутере

- `/etc/config/podkop` — главный UCI-конфиг.
- `/etc/init.d/podkop` — procd service wrapper (START=99, мониторинг интерфейсов, triggers).
- `/usr/bin/podkop` — основной CLI/оркестратор (~2700 строк).
- `/usr/lib/podkop/constants.sh` — глобальные константы (версии, пути, теги, URL списков).
- `/usr/lib/podkop/logging.sh` — логирование (info, debug, warn, error).
- `/usr/lib/podkop/helpers.sh` — валидация, парсинг URL, UCI-обёртки, миграция.
- `/usr/lib/podkop/nft.sh` — создание NFTable таблиц/сетов/элементов.
- `/usr/lib/podkop/rulesets.sh` — генерация sing-box rulesets из plain text.
- `/usr/lib/podkop/sing_box_config_manager.sh` — низкоуровневые JSON-билдеры sing-box (~1450 строк).
- `/usr/lib/podkop/sing_box_config_facade.sh` — высокоуровневый API поверх config_manager (~330 строк).
- `/etc/sing-box/config.json` — рабочий конфиг sing-box (перезаписывается Podkop).
- `/tmp/sing-box/cache.db` — кэш sing-box.
- `/tmp/sing-box/rulesets/` — скачанные и сгенерированные rulesets.

## Архитектура маршрутизации трафика

```
Клиентский трафик (TCP/UDP)
    ↓
NFTable (PodkopTable)
  ├─ Match: iifname ∈ {br-lan, ...}
  ├─ Match: daddr ∈ pod_subnets / fakeip range
  ├─ Action: meta mark = 0x00100000
    ↓
Linux ip rule (fwmark → таблица podkop)
  ├─ Route: 0.0.0.0/0 dev lo (tproxy redirect)
    ↓
sing-box tproxy inbound (127.0.0.1:1602)
  ├─ SNI/domain sniffing
    ↓
Route rules (domain_suffix / ip_cidr / rulesets)
    ↓
Outbound: proxy / vpn-interface / block(reject) / direct(exclusion)
```

DNS-поток:

1. Клиент запрашивает домен.
2. dnsmasq перенаправляет на 127.0.0.42:53 (sing-box DNS inbound).
3. sing-box проверяет domain routing rules.
4. Если домен в proxy-секции → возвращает FakeIP из 198.18.0.0/15.
5. sing-box хранит маппинг fake IP ↔ домен ↔ outbound.
6. Когда пакет приходит на fake IP, NFTable помечает его → tproxy → sing-box → нужный outbound.

Для output-трафика (с самого роутера) используется отдельная NFTable output chain с меткой `0x00200000`.

## Модель конфига — полная спецификация

### config settings 'settings'

| Опция | Тип | Default | Описание |
|-------|-----|---------|----------|
| `dns_type` | string | `udp` | Протокол DNS: `udp`, `dot`, `doh` |
| `dns_server` | string | `77.88.8.8` | Upstream DNS-сервер |
| `bootstrap_dns_server` | string | `77.88.8.8` | DNS для резолва доменных имён DNS-серверов |
| `dns_rewrite_ttl` | int | `60` | TTL для DNS-ответов (секунды) |
| `source_network_interfaces` | list | `br-lan` | Интерфейсы, трафик которых перехватывается |
| `enable_output_network_interface` | bool | `0` | Включить выбор output-интерфейса |
| `output_network_interface` | string | — | Конкретный исходящий интерфейс |
| `enable_badwan_interface_monitoring` | bool | `0` | Мониторинг WAN-интерфейсов (перезагрузка при failover) |
| `badwan_monitored_interfaces` | list | — | Список WAN-интерфейсов для мониторинга |
| `badwan_reload_delay` | int | `2000` | Задержка перезагрузки при смене интерфейса (мс) |
| `enable_yacd` | bool | `0` | Включить YACD dashboard (Clash API) |
| `disable_quic` | bool | `0` | Блокировать QUIC-протокол |
| `update_interval` | string | `1d` | Интервал обновления списков: `1h`, `3h`, `12h`, `1d`, `3d` |
| `download_lists_via_proxy` | bool | `0` | Скачивать списки через proxy |
| `dont_touch_dhcp` | bool | `0` | Не менять конфиг dnsmasq |
| `config_path` | string | `/etc/sing-box/config.json` | Путь к конфигу sing-box |
| `cache_path` | string | `/tmp/sing-box/cache.db` | Путь к кэшу sing-box |
| `log_level` | string | `warn` | Уровень логирования: `trace`, `debug`, `info`, `warn`, `error` |
| `exclude_ntp` | bool | `0` | Исключить NTP-трафик из проксирования |
| `shutdown_correctly` | bool | `0` | Внутренний флаг корректного завершения |
| `routing_excluded_ips` | list | — | IP-адреса/подсети, исключённые из маршрутизации |

### config section 'name'

Каждая секция — правило маршрутизации трафика.

**connection_type** — тип соединения:

| Значение | Описание |
|----------|----------|
| `proxy` | Маршрутизация через proxy-сервер |
| `vpn` | Маршрутизация через физический VPN-интерфейс |
| `block` | Блокировка (reject) |
| `exclusion` | Белый список — трафик идёт напрямую, минуя все правила |

**Опции для proxy** (`connection_type = proxy`):

| Опция | Тип | Default | Описание |
|-------|-----|---------|----------|
| `proxy_config_type` | string | `url` | Тип конфигурации: `url`, `selector`, `urltest`, `outbound` |
| `proxy_string` | string | — | Proxy URL для типа `url` |
| `selector_proxy_links` | list | — | Список proxy URL для `selector` (ручной выбор через Clash API) |
| `urltest_proxy_links` | list | — | Список proxy URL для `urltest` (авто-выбор по latency) |
| `urltest_check_interval` | string | `3m` | Интервал health-check: `30s`, `1m`, `3m`, `5m` |
| `urltest_tolerance` | int | `50` | Допустимая разница latency (мс, 50–1000) |
| `urltest_testing_url` | string | `https://www.gstatic.com/generate_204` | URL для проверки связности |
| `outbound_json` | string | — | Raw sing-box outbound JSON для типа `outbound` |
| `enable_udp_over_tcp` | bool | `0` | UDP-over-TCP для SOCKS/Shadowsocks |

**Опции для vpn** (`connection_type = vpn`):

| Опция | Тип | Default | Описание |
|-------|-----|---------|----------|
| `interface` | string | — | Имя физического VPN-интерфейса (обязательно) |
| `domain_resolver_enabled` | bool | `0` | Включить DNS-резолвер для этого интерфейса |
| `domain_resolver_dns_type` | string | — | Тип DNS: `udp`, `dot`, `doh` |
| `domain_resolver_dns_server` | string | — | DNS-сервер для этого интерфейса |

**Списки доменов и подсетей** (для всех connection_type):

| Опция | Тип | Описание |
|-------|-----|----------|
| `community_lists` | list | Предзаданные списки (см. ниже) |
| `user_domain_list_type` | string | Тип ввода доменов: `dynamic` (список) или `text` (textarea) |
| `user_domains` | list | Пользовательские домены (при `dynamic`) |
| `user_domains_text` | string | Пользовательские домены многострочно (при `text`) |
| `user_subnet_list_type` | string | Тип ввода подсетей: `dynamic` или `text` |
| `user_subnets` | list | Пользовательские подсети (при `dynamic`) |
| `user_subnets_text` | string | Пользовательские подсети многострочно (при `text`) |
| `local_domain_lists` | list | Пути к локальным файлам доменов |
| `local_subnet_lists` | list | Пути к локальным файлам подсетей |
| `remote_domain_lists` | list | URL удалённых списков доменов (.srs/.json) |
| `remote_subnet_lists` | list | URL удалённых списков подсетей |
| `fully_routed_ips` | list | Source IP, весь трафик которых идёт через этот outbound |
| `mixed_proxy_enabled` | bool | Включить mixed inbound (HTTP/SOCKS5) для этой секции |
| `mixed_proxy_port` | int | Порт mixed inbound (default: 2080) |

### Community lists

Полный список (`COMMUNITY_SERVICES` из constants.sh):

`russia_inside`, `russia_outside`, `ukraine_inside`, `geoblock`, `block`, `porn`, `news`, `anime`, `youtube`, `hdrezka`, `tiktok`, `google_ai`, `google_play`, `hodca`, `discord`, `meta`, `twitter`, `cloudflare`, `cloudfront`, `digitalocean`, `hetzner`, `ovh`, `telegram`, `roblox`

Для сервисов с подсетями (discord, meta, twitter, telegram, roblox, cloudflare, cloudfront, digitalocean, hetzner, ovh) автоматически подтягиваются IPv4-подсети из `itdoginfo/allow-domains`.

Community lists и remote lists считай внешним вводом. Для production-контуров лучше зеркалировать нужные списки во внутренний источник и обновлять их после ревью.

## CLI команды Podkop

### Lifecycle

```sh
podkop start          # Инициализация: загрузка конфига, создание NFT-правил, запуск sing-box
podkop stop           # Остановка: удаление NFT-правил, восстановление dnsmasq, остановка sing-box
podkop reload         # Hot reload без полного перезапуска
podkop restart        # Полный перезапуск (stop + start)
```

### Диагностика

```sh
podkop list_update           # Обновить community/remote списки
podkop check_proxy           # Проверить связность proxy
podkop check_nft_rules       # Показать NFTable-правила
podkop check_sing_box        # Проверить установку и версию sing-box
podkop check_logs            # Логи Podkop из системного журнала
podkop check_sing_box_logs   # Логи sing-box
podkop check_fakeip          # Тест FakeIP-резолва на роутере
podkop check_dns_available   # Проверить доступность DNS
podkop show_config           # Показать текущий UCI-конфиг
podkop show_sing_box_config  # Показать сгенерированный конфиг sing-box
podkop show_system_info      # Информация о системе
podkop show_version          # Версия Podkop
podkop show_sing_box_version # Версия sing-box
podkop get_status            # Статус сервиса Podkop
podkop get_sing_box_status   # Статус сервиса sing-box
podkop get_system_info       # Системная информация (JSON)
podkop global_check          # Комплексная диагностика
```

### Clash API

Доступно при `enable_yacd=1`. Работает через sing-box Clash API (порт 9090).

```sh
podkop clash_api get_proxies                    # Список всех proxy-групп
podkop clash_api get_proxy_latency <tag> [timeout]  # Latency конкретного proxy
podkop clash_api get_group_latency <tag> [timeout]  # Latency всей группы
podkop clash_api set_group_proxy <group> <proxy>    # Переключить proxy в группе
```

HTTP-эндпоинты Clash API:

```
GET  /proxies                        # Все proxy-группы
GET  /proxies/{tag}/delay?url=&timeout=  # Latency proxy
GET  /group/{tag}/delay?url=&timeout=    # Latency группы
PUT  /proxies/{tag}  {"name":"proxy"}    # Переключить proxy
```

Держи Clash API и YACD на loopback или за отдельным auth/reverse-proxy контуром. Не публикуй их напрямую в LAN/WAN без контроля доступа.

## Что проверять первым при поломке

1. Совместима ли версия OpenWrt (24.10+).
2. Не установлен ли конфликтующий пакет (`https-dns-proxy`, `nextdns`, `passwall`, `Getdomains`).
3. Есть ли рабочий outbound в секциях `config section`.
4. Существует ли `sing-box` и подходит ли его версия (≥ 1.12.0).
5. Не остались ли старые значения в `/etc/config/podkop` после обновления.
6. Не сломан ли `dnsmasq` после вмешательства Podkop (проверь `dont_touch_dhcp`).
7. Работает ли DNS: `podkop check_dns_available`, `podkop check_fakeip`.
8. NFTable-правила на месте: `podkop check_nft_rules`.
9. Логи sing-box: `podkop check_sing_box_logs`.
10. Комплексная проверка: `podkop global_check`.
