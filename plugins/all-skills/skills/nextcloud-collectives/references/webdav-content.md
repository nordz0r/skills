# Collectives — Контент страниц через WebDAV

Как устроено хранение markdown-контента, как собирать пути, читать и писать статьи, работать с версиями.

## Раскладка файлов на диске

Collectives не хранит контент в базе — каждая страница это `.md`-файл в Nextcloud Files:

```text
Файлы пользователя/
└── Collectives/                    # папка монтирования (user_folder, может быть локализована)
    └── Team Wiki/                  # корень коллектива (папка с именем коллектива)
        ├── Readme.md               # landing page коллектива (title: Readme)
        ├── Архитектура.md          # страница верхнего уровня без детей
        ├── Руководство/            # страница С детьми — это папка
        │   ├── Readme.md           #   контент самой страницы «Руководство»
        │   ├── Деплой.md           #   дочерняя страница
        │   └── Backup/             #   страница с детьми — снова папка
        │       └── Readme.md
        └── .attachments.42/        # вложения страницы с id=42
```

Правила:

- Страница без детей — файл `<Title>.md`.
- Страница с детьми — папка `<Title>/`, её контент лежит в `<Title>/Readme.md`, дети — внутри папки.
- Имя коллектива в пути совпадает с его `name`.
- Папка монтирования задаётся настройкой пользователя `user_folder` приложения `collectives` и по умолчанию локализована (`Collectives`, на русском инстансе может быть `Коллективы`). **Поэтому путь всегда собирай из полей PageInfo, а не конструируй сам.**

## Сборка WebDAV-пути из PageInfo

`PageInfo` содержит готовые компоненты пути:

```
WebDAV URL = {NEXTCLOUD_URL}/remote.php/dav/files/{user}
             /{collectivePath}[/{filePath}]/{fileName}
```

- `collectivePath` — например `Collectives/Team Wiki` (уже включает имя коллектива);
- `filePath` — вложенность внутри коллектива, добавляется только если непустой;
- `fileName` — `Страница.md` или `Readme.md`.

```bash
dav_url() { # $1=collectivePath $2=filePath $3=fileName
  local joined="$1/${2:+$2/}$3"
  printf '%s/remote.php/dav/files/%s/%s' \
    "$NEXTCLOUD_URL" \
    "$(jq -rn --arg v "$NEXTCLOUD_USER" '$v|@uri')" \
    "$(jq -rn --arg v "$joined" '$v|@uri|gsub("%2F"; "/")')"
}
```

Нюанс кодирования: `@uri` кодирует и слэши (`%2F`), а `collectivePath`/`filePath` содержат слэши как разделители сегментов. Поэтому `gsub("%2F"; "/")` возвращает разделители, оставляя закодированными пробелы и спецсимволы внутри имён.

Проверка здоровья пути: `PROPFIND` с `Depth: 0` на собранный URL должен вернуть 207. Если 404 — не пытайся чинить путь угадыванием; перечитай список страниц через OCS и собери путь заново.

## Грабли реальных инстансов

- **`GET /collectives/search/recent` и поиск возвращают display-путь** в `collectivePath` (например `/Wiki-1` или `/Knowledge-Base-2`) — по нему WebDAV не строится, будет 404. Канонические поля для сборки пути дают только `GET /collectives/{cid}/pages` и `GET /pages/{id}`. Если после поиска получаешь 404 на DAV — перезапроси PageInfo страницы основным эндпоинтом.
- **Корень монтирования зависит от режима инстанса**: по умолчанию это папка `Collectives` (локализуется, например `Коллективы`), в team-режиме коллективы могут монтироваться иначе (наблюдалось `Группы/Wiki/<имя>`). Ещё одна причина строить путь только из полей PageInfo и никогда не хардкодить префикс.
- **Кириллица и пробелы в пути** — сегменты коллективов и страниц часто содержат кириллицу/пробелы: кодируй каждый сегмент (`jq @uri` или `python` `urllib.parse.quote`); слэши-разделители кодировать нельзя.

## Чтение и запись контента

```bash
# Прочитать страницу
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" "$(dav_url "$cp" "$fp" "$fn")"

# Записать/перезаписать страницу целиком
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" -X PUT \
  -H "Content-Type: text/markdown" \
  --data-binary @article.md "$(dav_url "$cp" "$fp" "$fn")"

# Дописать в конец (прочитай, добавь, запиши — атомарного append нет)
curl -sf ... old.md > tmp.md
printf '\n\n## Новый раздел\n\nТекст.\n' >> tmp.md
curl -sf ... -X PUT --data-binary @tmp.md "$(dav_url "$cp" "$fp" "$fn")"

# Посмотреть содержимое папки коллектива
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" -X PROPFIND -H "Depth: 1" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/Collectives/Team%20Wiki/"
```

Важно:

- PUT перезаписывает **весь файл**: сначала GET, потом изменение, потом PUT.
- Если кто-то правит страницу в браузере (Text-редактор с совместным редактированием), твой PUT может затереть его правки, а его правки — твои. Перед редактированием перечитай файл; после записи сообщи пользователю о возможном конфликте.
- Не используй MKCOL/MOVE внутри коллектива для «создания страниц» — создавай страницы через OCS API, чтобы sync дерева (`parentId`, индексация, поиск) отработал корректно.

## Переименование и структура

Переименовывать страницы и менять иерархию нужно через OCS (`PUT /pages/{id}` с `title`/`parentId`) — сервер сам переместит файлы. Ручной MOVE по WebDAV ломает соответствие дерева и файлов.

## Вложения страницы

Вложения лежат в скрытой папке `.attachments.{pageId}` в корне коллектива. Загружай их через OCS-эндпоинт `POST /pages/{id}/attachments` (multipart `file`) — он сам создаст папку и зарегистрирует вложение. В тексте страницы на вложение ссылаются по относительному пути/имени.

## Версии страниц

История версий — стандартный механизм Nextcloud Files (files_versions). Нужен числовой `fileId` файла страницы:

```bash
# 1. Получить fileId через PROPFIND
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" -X PROPFIND \
  -H "Depth: 0" -H "Content-Type: application/xml" \
  --data '<?xml version="1.0"?><d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns"><d:prop><oc:fileid/></d:prop></d:propfind>' \
  "$(dav_url "$cp" "$fp" "$fn")" | grep -o '<oc:fileid>[0-9]*</oc:fileid>'

# 2. Список версий файла
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" -X PROPFIND -H "Depth: 1" \
  "$NEXTCLOUD_URL/remote.php/dav/versions/$NEXTCLOUD_USER/versions/{fileId}/"

# 3. Скачать конкретную версию (имя версии — timestamp)
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  "$NEXTCLOUD_URL/remote.php/dav/versions/$NEXTCLOUD_USER/versions/{fileId}/{timestamp}"

# 4. Восстановить версию — MOVE в служебную папку restore
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" -X MOVE \
  -H "Destination: $NEXTCLOUD_URL/remote.php/dav/versions/$NEXTCLOUD_USER/restore" \
  "$NEXTCLOUD_URL/remote.php/dav/versions/$NEXTCLOUD_USER/versions/{fileId}/{timestamp}"
```

Доступность версий зависит от включённого приложения `files_versions` и настроек хранения ревизий на сервере. Если нужно только посмотреть старый текст — скачивай версию шага 3 и не трогай restore: восстановление меняет текущее содержимое страницы.

## Публичная ссылка на страницу

Расшаренная страница доступна без авторизации:

```bash
# Список страниц публичной шары
curl -sf -H "OCS-APIRequest: true" \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/collectives/api/v1.0/p/collectives/{token}/pages?format=json"

# Контент публичной страницы — обычный GET по DAV не работает для шары;
# используй веб-URL шары: {NEXTCLOUD_URL}/apps/collectives/p/{token}
```

## Ограничения целостности

- Не переименовывай и не удаляй `Readme.md` вручную — это landing page коллектива/раздела.
- Не создавай файлы `.md` через WebDAV (`PUT` на новый путь) с надеждой получить страницу: дерево страниц строится из OCS-операций. Новый `.md`-файл останется неиндексированным, пока синхронизация не подхватит его (а это недетерминировано между версиями приложения).
- Имена страниц не могут содержать `/`; сервер может заменить недопустимые символы в имени файла, но `title` сохранит оригинал.
