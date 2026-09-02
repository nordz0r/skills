# Podkop: разработка и сборка

## Frontend workflow

Рабочая директория:

```sh
cd fe-app-podkop
```

Команды из CI:

```sh
yarn install --frozen-lockfile
yarn format
yarn lint --max-warnings=0
yarn test --run
yarn build
yarn locales:actualize
```

Что проверяет upstream CI:

- форматирование (prettier);
- ESLint;
- тесты (vitest);
- build без неожиданных сгенерированных изменений.

Результат `yarn build` копируется в `luci-app-podkop/htdocs/luci-static/resources/view/podkop/`.

## Backend / shell workflow

Критические shell-файлы:

- `install.sh` — установка/обновление.
- `podkop/files/usr/bin/podkop` — основной оркестратор (~2700 строк).
- `podkop/files/usr/lib/*.sh` — библиотеки:
  - `constants.sh` — константы, теги, URL.
  - `logging.sh` — логирование.
  - `helpers.sh` — валидация, парсинг URL, UCI, cron, миграция.
  - `nft.sh` — NFTable-операции.
  - `rulesets.sh` — sing-box rulesets.
  - `sing_box_config_manager.sh` — низкоуровневые JSON-билдеры sing-box.
  - `sing_box_config_facade.sh` — высокоуровневый API.

Для них в CI используется differential ShellCheck. Код должен быть POSIX/ash-friendly (busybox).

Init script (`podkop/files/etc/init.d/podkop`):
- procd-based, `START=99` (после основных сервисов).
- Поддерживает interface monitoring triggers (BadWAN).
- Config change triggers для автоматического reload.
- Netdev triggers для отслеживания состояния интерфейсов.

## Сборка релизных пакетов

Upstream release pipeline строит `ipk` и `apk` через Docker:

- `Dockerfile-ipk`
- `Dockerfile-apk`
- `.github/workflows/build.yml`

Логика релиза:

1. взять version/tag;
2. собрать docker image;
3. вытащить артефакты из контейнера;
4. отфильтровать `podkop`, `luci-app-podkop`, `luci-i18n-podkop-ru`;
5. опубликовать GitHub Release.

## Практические правила для изменений

- Изменения shell-части проверяй на побочные эффекты для `dnsmasq` и `sing-box`.
- Любая правка схемы `/etc/config/podkop` должна сопровождаться migration story.
- Не предполагай наличие старых OpenWrt: upstream ориентируется на `24.10+`.
- Если меняешь frontend validators, сверяйся с `String-example.md`, иначе UI и backend начнут расходиться.
- При добавлении нового community list: обнови `constants.sh` (COMMUNITY_SERVICES + URL подсетей если есть) и `fe-app-podkop/src/constants.ts`.
- Версии зависимостей проверяются в runtime: `sing-box` ≥ 1.12.0, `jq` ≥ 1.7.1, `coreutils-base64` ≥ 9.7.
