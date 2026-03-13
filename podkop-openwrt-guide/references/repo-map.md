# Podkop: карта репозитория

## Корень репозитория

- `README.md`: предупреждения, установка, миграция `0.7.0`, общие ограничения.
- `install.sh`: главный источник правды по install/update. Определяет `opkg`/`apk`, скачивает пакеты с GitHub Releases (до 3 попыток), проверяет версии и место.
- `String-example.md`: форматы proxy URL-строк (upstream reference).
- `Dockerfile-ipk`, `Dockerfile-apk`: сборка релизных пакетов.
- `.github/workflows/*`: CI и release pipeline.

## Основной OpenWrt пакет

Папка: `podkop/`

### Ключевые файлы

- `podkop/Makefile`: runtime зависимости, conflicts, packaging.
- `podkop/files/etc/config/podkop`: дефолтный UCI-конфиг (шаблон).
- `podkop/files/etc/init.d/podkop`: procd service wrapper (START=99, мониторинг интерфейсов, config/netdev triggers).
- `podkop/files/usr/bin/podkop`: CLI и orchestration (~2700 строк).

### Shell-библиотеки (`podkop/files/usr/lib/`)

| Файл | Строк | Назначение |
|------|-------|------------|
| `constants.sh` | ~65 | Глобальные константы: версии, пути, теги sing-box, имена NFT-таблиц/сетов, маски (fakeip `0x00100000`, outbound `0x00200000`), URL списков, `COMMUNITY_SERVICES` |
| `logging.sh` | ~30 | Функции логирования с уровнями (info, debug, warn, error) |
| `helpers.sh` | ~355 | Валидация IPv4/CIDR/доменов, определение base64, парсинг URL (scheme, host, port, path, query), UCI-обёртки, cron, миграция |
| `nft.sh` | ~70 | Создание NFT-таблиц, IPv4/interface-сетов, добавление элементов (chunked) |
| `rulesets.sh` | ~180 | Генерация sing-box JSON rulesets, импорт доменов/подсетей из plain text, batch-операции |
| `sing_box_config_manager.sh` | ~1450 | Низкоуровневые JSON-билдеры: log, DNS-серверы (UDP/TLS/HTTPS/FakeIP), DNS rules, inbounds (tproxy/direct/mixed), outbounds (direct/socks/vless/trojan/ss/hysteria2/selector/urltest/interface), route rules, rulesets, Clash API, NTP |
| `sing_box_config_facade.sh` | ~330 | Высокоуровневый API: добавление proxy outbound (парсинг URL), DNS-серверов, mixed inbound + route rule, security/transport для VLESS/Trojan, обработка raw JSON outbound |

## LuCI пакет

Папка: `luci-app-podkop/`

### Структура

- `Makefile`: пакет LuCI, зависимость от `luci-base`.
- `root/usr/share/luci/menu.d/luci-app-podkop.json`: определение меню (`/admin/services/podkop`).
- `root/usr/share/rpcd/acl.d/luci-app-podkop.json`: RPC ACL — доступ к `file exec`, `ubus service.list`, `uci podkop`.
- `root/etc/uci-defaults/50_luci-podkop`: post-install скрипт.
- `po/`: локализация (gettext).

### JavaScript-компоненты (`htdocs/luci-static/resources/view/podkop/`)

| Файл | Строк | Назначение |
|------|-------|------------|
| `main.js` | ~4900 | Валидаторы (IP, домен, DNS, URL, путь, подсеть), константы (DNS-серверы, community lists, интервалы), helpers (clipboard, file download, shell exec), Clash API интеграция, IP masking для диагностики |
| `podkop.js` | ~100 | Entry point: табы (sections, settings, diagnostics, dashboard), TypedSection формы, инициализация CoreService |
| `section.js` | ~700 | UI секции: выбор connection_type, proxy_config_type, proxy-строки с валидацией, URLTest параметры, community lists checkboxes, user domains/subnets, local/remote lists, fully_routed_ips, mixed proxy |
| `settings.js` | ~440 | UI настроек: DNS (type, server, bootstrap, TTL), source/output интерфейсы (DeviceSelect, блокирует wireless), BadWAN мониторинг, YACD, QUIC, update interval, download via proxy, DHCP, NTP exclusion, advanced (config/cache paths, log level) |
| `dashboard.js` | ~20 | Stub для YACD dashboard |
| `diagnostic.js` | ~20 | Stub для диагностики |

### LuCI URL-паттерны

```
/admin/services/podkop?tab=sections
/admin/services/podkop?tab=settings
/admin/services/podkop?tab=diagnostics
/admin/services/podkop?tab=dashboard
```

## Frontend-исходники

Папка: `fe-app-podkop/`

TypeScript-исходники для LuCI UI. Собираются в статические JS-файлы для `luci-app-podkop/`.

- `package.json`: команды разработки (yarn: install, format, lint, test, build, locales:actualize).
- `src/podkop/*`: API, fetchers, services.
- `src/validators/*`: валидация proxy-строк, IP, DNS, subnet — синхронизируй с `String-example.md`.
- `src/constants.ts`: константы (DNS-серверы, community lists, интервалы обновления).
- `tests/` и `src/**/tests`: vitest coverage.
- `locales/`: gettext pipeline.

## Где править что

| Задача | Где менять |
|--------|-----------|
| Runtime: маршрутизация, sing-box, nft, dnsmasq | `podkop/files/usr/bin/podkop` + `podkop/files/usr/lib/*.sh` |
| UI/UX в LuCI | `fe-app-podkop/` → build → `luci-app-podkop/` |
| Packaging, conflicts, зависимости | `podkop/Makefile`, `luci-app-podkop/Makefile` |
| Upgrade path, apk/opkg | `install.sh` |
| Proxy URL форматы, валидация | `String-example.md` + `fe-app-podkop/src/validators/` |
| Community lists | `constants.sh` (URL и имена) + `fe-app-podkop/src/constants.ts` (UI) |
| Конфиг-шаблон по умолчанию | `podkop/files/etc/config/podkop` |
