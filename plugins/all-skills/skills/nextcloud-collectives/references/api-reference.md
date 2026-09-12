# Collectives OCS API — Полный справочник (v1.0)

Источник истины: `openapi.json` из репозитория [nextcloud/collectives](https://github.com/nextcloud/collectives). Актуальная версия API: `1.0` (параметр пути `{apiVersion}`).

Базовый URL:

```
{NEXTCLOUD_URL}/ocs/v2.php/apps/collectives/api/v1.0
```

Общие требования ко всем запросам:

- Заголовок `OCS-APIRequest: true`.
- `?format=json` для JSON (иначе XML).
- Basic Auth: `-u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN"`.
- Тела запросов — JSON (`Content-Type: application/json`).
- Обёртка ответа: `{"ocs": {"meta": {...}, "data": {...}}}`, успех — `meta.statuscode == 200`.

## Обозначения

- `{cid}` — `collectiveId`, `{id}` — id страницы/тега/коллектива, `{token}` — токен шары.
- `*` — обязательное поле тела запроса.

---

## Коллективы

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives` | Список коллективов пользователя |
| POST | `/collectives` | Создать коллектив |
| PUT | `/collectives/{id}` | Обновить emoji коллектива |
| DELETE | `/collectives/{id}` | Переместить коллектив в корзину |
| PUT | `/collectives/{id}/editLevel` | Уровень права редактирования |
| PUT | `/collectives/{id}/shareLevel` | Уровень права шеринга |
| PUT | `/collectives/{id}/pageMode` | Режим страниц по умолчанию |

### POST /collectives
```json
{ "name": "Team Wiki", "emoji": "📚" }
```
Ответ: `{"collective": Collective, "info": string}`.

### PUT /collectives/{id}
```json
{ "emoji": "🚀" }
```
Ответ: `{"collective": Collective}`.

### PUT /collectives/{id}/editLevel | shareLevel
```json
{ "level": 4 }
```
Значения `level` (уровни member в Nextcloud Teams/circles): `1` — все члены, `4` — модераторы и выше, `8` — только админы. Требуются права admin команды.

### PUT /collectives/{id}/pageMode
```json
{ "mode": 1 }
```
`0` — view (по умолчанию просмотр), `1` — edit (сразу редактирование).

### GET /collectives
Ответ: `{"collectives": [Collective, ...]}`. Коллективы с `trashTimestamp` — уже в корзине.

---

## Корзина коллективов

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/trash` | Список удалённых коллективов |
| PATCH | `/collectives/trash/{id}` | Восстановить |
| DELETE | `/collectives/trash/{id}` | Удалить навсегда |

`DELETE /collectives/trash/{id}?circle=true` — заодно удалить команду (team/circle). Ответы: `{"collectives": [...]}` для GET.

---

## Страницы

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/pages` | Список страниц (всё дерево) |
| POST | `/collectives/{cid}/pages/{parentId}` | Создать страницу |
| GET | `/collectives/{cid}/pages/{id}` | Метаданные одной страницы (без контента!) |
| PUT | `/collectives/{cid}/pages/{id}` | Переместить/переименовать/копировать |
| DELETE | `/collectives/{cid}/pages/{id}` | Переместить страницу в корзину |
| GET | `/collectives/{cid}/pages/{id}/touch` | Обновить время/пользователя правки |
| PUT | `/collectives/{cid}/pages/{id}/to/{newCid}` | Переместить/копировать в другой коллектив |

### POST /collectives/{cid}/pages/{parentId}
`parentId: 0` — верхний уровень коллектива.
```json
{ "title": "Моя статья", "templateId": 123 }
```
`templateId` опционален. Ответ: `{"page": PageInfo}`. Контент не создаётся — запиши его через WebDAV.

### PUT /collectives/{cid}/pages/{id}
```json
{ "parentId": 42, "title": "Новое имя", "index": 0, "copy": false }
```
Все поля опциональны; `copy: true` копирует вместо перемещения. Ответ: `{"page": PageInfo}` (при копировании — новая страница).

### PUT /collectives/{cid}/pages/{id}/to/{newCid}
```json
{ "parentId": 0, "index": 0, "copy": false }
```

### Свойства страницы

| Метод | Путь | Тело |
|---|---|---|
| PUT | `/pages/{id}/emoji` | `{"emoji": "🔧"}` (или `{"emoji": null}` — сброс) |
| PUT | `/pages/{id}/fullWidth` | `{"fullWidth": true}` |
| PUT | `/pages/{id}/subpageOrder` | `{"subpageOrder": "[12,7,3]"}` — JSON-строка, массив id |

Ответ везде `{"page": PageInfo}`.

### Порядок и дерево

- Иерархия: `parentId` (0 = корень). Дети страницы X — страницы с `parentId == X.id`.
- `subpageOrder` — ручной порядок детей; может покрывать не всех детей, остальные добавляются в конец по сортировке коллектива (`userSettings/pageOrder`).

---

## Корзина страниц

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/pages/trash` | Список удалённых страниц |
| PATCH | `/collectives/{cid}/pages/trash/{id}` | Восстановить |
| DELETE | `/collectives/{cid}/pages/trash/{id}` | Удалить навсегда |

GET отвечает `{"pages": [PageInfo, ...]}` — у страниц в корзине заполнен `trashTimestamp`.

---

## Шаблоны

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/pages/templates` | Список шаблонов |
| POST | `/collectives/{cid}/pages/templates/{parentId}` | Создать шаблон (`{"title": "...", "parentId": 0}`) |
| PUT | `/collectives/{cid}/pages/templates/{id}` | Переименовать (`{"title": "..."}`) |
| DELETE | `/collectives/{cid}/pages/templates/{id}` | Удалить шаблон навсегда |
| PUT | `/collectives/{cid}/pages/templates/{id}/emoji` | Emoji шаблона |

Шаблон — обычная страница с ролью template; при создании страницы через `templateId` её контент копируется из шаблона.

---

## Поиск

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/search?searchString=...` | Полнотекстовый поиск по коллективу |
| GET | `/collectives/search/recent?query=&limit=` | Недавние страницы по всем коллективам (`limit` ≤ 100, по умолчанию 10) |

Оба отвечают `{"pages": [PageInfo, ...]}`.

---

## Теги

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/tags` | Список тегов |
| POST | `/collectives/{cid}/tags` | Создать тег |
| PUT | `/collectives/{cid}/tags/{id}` | Обновить тег |
| DELETE | `/collectives/{cid}/tags/{id}` | Удалить тег |
| PUT | `/collectives/{cid}/pages/{id}/tags/{tagId}` | Присвоить тег странице |
| DELETE | `/collectives/{cid}/pages/{id}/tags/{tagId}` | Снять тег |

Тело создания/обновления: `{"name": "важно", "color": "FF0000"}`.

---

## Вложения

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/pages/{id}/attachments` | Список вложений |
| POST | `/collectives/{cid}/pages/{id}/attachments` | Загрузить (multipart, поле `file`) |
| PUT | `/collectives/{cid}/pages/{id}/attachments/{attachmentId}` | Переименовать (`{"name": "..."}`) |
| DELETE | `/collectives/{cid}/pages/{id}/attachments/{attachmentId}` | Удалить |
| PATCH | `/collectives/{cid}/pages/{id}/attachments/trash/{attachmentId}` | Восстановить из корзины |

Ответы: `{"attachments": [...]}` и `{"attachment": {...}}`.

Вложение в markdown ссылается по имени: файл кладут рядом через загрузку, в тексте используют ссылку на имя вложения (WebUI вставляет её автоматически).

---

## Публичные шары

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/collectives/{cid}/shares` | Все шары коллектива (включая шары страниц) |
| POST | `/collectives/{cid}/shares` | Шара всего коллектива (`{"password": "..."}`) |
| PUT | `/collectives/{cid}/shares/{token}` | Обновить (`{"editable": false, "password": "..."}`) |
| DELETE | `/collectives/{cid}/shares/{token}` | Удалить шару |
| POST | `/collectives/{cid}/pages/{pageId}/shares` | Шара отдельной страницы |
| PUT/DELETE | `/collectives/{cid}/pages/{pageId}/shares/{token}` | Обновить/удалить шару страницы |

POST/PUT отвечают объектом шары (не обёрнутым в ключ), DELETE — пустой `{}`.

Публичные эндпоинты без авторизации (только чтение/редактирование по токену):

- `GET /p/collectives/{token}` — расшаренный коллектив или страница.
- `GET /p/collectives/{token}/pages` — список страниц шары.
- `GET /p/collectives/{token}/pages/{id}` — метаданные страницы.
- `GET /p/collectives/{token}/search?searchString=...` — поиск по шаре.
- Аналоги create/edit/emoji/trash/tags — работают по токену, если шара `editable`.
- `OCS-APIRequest: true` обязателен и здесь.

---

## Настройки пользователя

| Метод | Путь | Тело | Значения |
|---|---|---|---|
| PUT | `/collectives/{cid}/userSettings/pageOrder` | `{"pageOrder": 2}` | 0=byOrder, 1=byTimeAsc, 2=byTitleAsc, 3=byTimeDesc, 4=byTitleDesc |
| PUT | `/collectives/{cid}/userSettings/notify` | `{"notify": 2}` | 0=off, 1=mentions, 2=all |
| PUT | `/collectives/{cid}/userSettings/favoritePages` | `{"favoritePages": "[12,7]"}` | JSON-строка с массивом id |
| PUT | `/collectives/{cid}/userSettings/showMembers` | `{"showMembers": true}` | expanded виджета участников |
| PUT | `/collectives/{cid}/userSettings/showRecentPages` | `{"showRecentPages": true}` | expanded виджета недавних |

Прочее:

- `POST /settings/user` — `{"key": "...", "value": "..."}`; `GET /settings/user/{key}` — прочитать.
- Сессии совместного редактирования: `POST/PUT/DELETE /collectives/{cid}/sessions` — нужны только для реализации live-редактирования, агенту не требуются.

---

## Схемы объектов

### PageInfo
```json
{
  "id": 42,
  "slug": "my-page",
  "title": "Моя страница",
  "parentId": 0,
  "emoji": "🔧",
  "fileName": "Моя страница.md",
  "filePath": "",
  "collectivePath": "Collectives/Team Wiki",
  "subpageOrder": [12, 7],
  "tags": [],
  "timestamp": 1780000000,
  "size": 1234,
  "lastUserId": "admin",
  "lastUserDisplayName": "Admin",
  "isFullWidth": false,
  "trashTimestamp": null,
  "linkedPageIds": [],
  "shareToken": null
}
```

- `collectivePath` — путь от корня файлов пользователя до корня коллектива (уже включает имя коллектива).
- `filePath` — вложенность внутри коллектива (`""` для верхнего уровня).
- `fileName` — имя `.md`-файла; `Readme.md` — landing page (страница с `title: Readme` у корня коллектива).
- Контента в объекте нет — файл читается по WebDAV.

WebDAV-путь страницы:

```
/remote.php/dav/files/{user}/{collectivePath}/{filePath}/{fileName}
```

(`filePath` добавляется, только если не пуст.)

### Collective
```json
{
  "id": 7,
  "name": "Team Wiki",
  "slug": "team-wiki",
  "circleId": "...",
  "emoji": "📚",
  "level": 8,
  "pageMode": 0,
  "editPermissionLevel": 4,
  "sharePermissionLevel": 8,
  "canEdit": true,
  "canShare": true,
  "canLeave": false,
  "shareToken": null,
  "isPageShare": false,
  "sharePageId": 0,
  "shareEditable": false,
  "userPageOrder": 0,
  "userShowMembers": true,
  "userShowRecentPages": true,
  "userFavoritePages": [],
  "trashTimestamp": null
}
```

`level` — уровень текущего пользователя в команде: 1=member, 4=moderator, 8=admin, 9=owner.

### PageAttachment
```json
{
  "id": 91,
  "name": "schema.png",
  "filesize": 20480,
  "mimetype": "image/png",
  "timestamp": 1780000000,
  "path": "schema.png",
  "internalPath": ".attachments.42/schema.png",
  "hasPreview": true,
  "type": "text"
}
```

### CollectiveShare
```json
{
  "id": 5,
  "collectiveId": 7,
  "pageId": 0,
  "token": "a1b2c3d4e5",
  "owner": "admin",
  "editable": false,
  "hasPassword": false
}
```

`pageId: 0` — шара всего коллектива; `pageId > 0` — шара конкретной страницы.

### Tag
```json
{ "id": 3, "collectiveId": 7, "name": "важно", "color": "FF0000" }
```

---

## Проверка, что приложение включено

```bash
curl -sf -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" -H "OCS-APIRequest: true" \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/apps?filter=enabled&format=json" \
  | jq '.ocs.data.apps | map(select(test("collectives|circles")))'
```

Должны вернуться `collectives` и `circles` (Teams). Для этого вызова нужен admin-токен; остальные эндпоинты Collectives — обычный токен пользователя.
