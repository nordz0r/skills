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

- форматирование;
- ESLint;
- тесты;
- build без неожиданных сгенерированных изменений.

## Backend / shell workflow

Критические shell-файлы:

- `install.sh`
- `podkop/files/usr/bin/podkop`
- `podkop/files/usr/lib/podkop/*.sh`

Для них в CI используется differential ShellCheck. Если меняешь shell-код, держи его POSIX/ash-friendly и не ломай существующую структуру helpers.

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
- Не предполагай наличие старых OpenWrt: upstream ориентируется на `24.10`.
- Если меняешь frontend validators, сверяйся с `String-example.md`, иначе UI и backend начнут расходиться.
