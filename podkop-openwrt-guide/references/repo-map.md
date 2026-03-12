# Podkop: карта репозитория

## Корень репозитория

- `README.md`: предупреждения, установка, миграция `0.7.0`, общие ограничения.
- `install.sh`: главный источник правды по install/update checks.
- `String-example.md`: форматы proxy URL-строк.
- `Dockerfile-ipk`, `Dockerfile-apk`: сборка релизных пакетов.
- `.github/workflows/*`: CI и release pipeline.

## Основной OpenWrt пакет

Папка: `podkop/`

Ключевые файлы:

- `podkop/Makefile`: runtime зависимости, conflicts, packaging.
- `podkop/files/etc/config/podkop`: дефолтный UCI-конфиг.
- `podkop/files/etc/init.d/podkop`: service wrapper.
- `podkop/files/usr/bin/podkop`: CLI и orchestration.
- `podkop/files/usr/lib/podkop/*.sh`: helpers для `nft`, `sing-box`, logging, rulesets.

## LuCI пакет

Папка: `luci-app-podkop/`

Что внутри:

- `Makefile`: пакет LuCI.
- `htdocs/luci-static/resources/view/...`: frontend bundle/entrypoints для LuCI.
- `root/usr/share/rpcd`: RPC ACL и backend hooks.
- `po/`: локализация.

## Frontend-исходники

Папка: `fe-app-podkop/`

Особенно важны:

- `package.json`: команды разработки.
- `src/podkop/*`: API, fetchers, services.
- `src/validators/*`: валидация proxy-строк, IP, DNS, subnet.
- `tests/` и `src/**/tests`: vitest coverage.
- `locales/`: gettext pipeline.

## Где править что

- Нужно поменять runtime логику маршрутизации, `sing-box`, `nft`, `dnsmasq`: правь `podkop/files/usr/bin/podkop` и `podkop/files/usr/lib/podkop/*`.
- Нужно изменить UI/UX в LuCI: смотри `fe-app-podkop/` и generated/static часть `luci-app-podkop/`.
- Нужно поменять packaging или conflicts: смотри `podkop/Makefile`, `luci-app-podkop/Makefile`.
- Нужно понять upgrade path или поддержку `apk/opkg`: читай `install.sh`.
