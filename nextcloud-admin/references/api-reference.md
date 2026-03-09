# Nextcloud API — Полный справочник

## Содержание

1. [WebDAV File API](#webdav-file-api)
2. [OCS Share API](#ocs-share-api)
3. [User Provisioning API](#user-provisioning-api)
4. [Groups API](#groups-api)
5. [Apps API](#apps-api)
6. [Коды ошибок](#коды-ошибок)

---

## WebDAV File API

Базовый URL: `$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/`

Все операции используют Basic Auth: `-u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN"`

### PROPFIND — Листинг файлов

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X PROPFIND \
  -H "Depth: 1" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{path}"
```

**Заголовок Depth:**
- `0` — только указанный ресурс (свойства файла/папки)
- `1` — ресурс + непосредственные дочерние элементы
- `infinity` — полная рекурсия (может быть отключена на сервере)

**Расширенный PROPFIND** (запрос конкретных свойств):
```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X PROPFIND \
  -H "Depth: 1" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:" xmlns:oc="http://owncloud.org/ns" xmlns:nc="http://nextcloud.org/ns">
  <d:prop>
    <d:getlastmodified/>
    <d:getcontentlength/>
    <d:getcontenttype/>
    <oc:fileid/>
    <oc:permissions/>
    <oc:size/>
    <nc:has-preview/>
  </d:prop>
</d:propfind>' \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{path}"
```

### PUT — Загрузка файла

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -T "/local/path/file.txt" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{remote_path}/file.txt"
```

Если промежуточные директории не существуют, запрос завершится с ошибкой 409 Conflict. Создай директории заранее через MKCOL.

### GET — Скачивание файла

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -o "/local/path/file.txt" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{remote_path}/file.txt"
```

### MKCOL — Создание директории

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X MKCOL \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{path}/new-folder/"
```

Создаёт только один уровень. Для вложенных директорий создавай поуровнево.

### DELETE — Удаление

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{path}"
```

Удаляет файл или директорию рекурсивно. Файл попадает в корзину (если включена).

### MOVE — Перемещение/переименование

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X MOVE \
  -H "Destination: $NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{new_path}" \
  -H "Overwrite: F" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{old_path}"
```

- `Overwrite: T` (по умолчанию) — перезаписать если существует
- `Overwrite: F` — вернуть ошибку если существует

### COPY — Копирование

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X COPY \
  -H "Destination: $NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{dest_path}" \
  "$NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/{source_path}"
```

### Chunked Upload (большие файлы)

Для файлов >50MB рекомендуется chunked upload:

```bash
# 1. Создать upload-сессию
UPLOAD_ID="upload-$(date +%s)"
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X MKCOL \
  "$NEXTCLOUD_URL/remote.php/dav/uploads/$NEXTCLOUD_USER/$UPLOAD_ID"

# 2. Загрузить чанки (по 10MB)
split -b 10485760 largefile.zip chunk_
for chunk in chunk_*; do
  curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
    -T "$chunk" \
    "$NEXTCLOUD_URL/remote.php/dav/uploads/$NEXTCLOUD_USER/$UPLOAD_ID/$chunk"
done

# 3. Собрать файл
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X MOVE \
  -H "Destination: $NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/largefile.zip" \
  "$NEXTCLOUD_URL/remote.php/dav/uploads/$NEXTCLOUD_USER/$UPLOAD_ID/.file"
```

### Корзина (Trashbin WebDAV)

```bash
# Список удалённых файлов
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X PROPFIND \
  -H "Depth: 1" \
  "$NEXTCLOUD_URL/remote.php/dav/trashbin/$NEXTCLOUD_USER/trash/"

# Восстановить файл
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X MOVE \
  -H "Destination: $NEXTCLOUD_URL/remote.php/dav/files/$NEXTCLOUD_USER/restored-file.txt" \
  "$NEXTCLOUD_URL/remote.php/dav/trashbin/$NEXTCLOUD_USER/trash/{filename}"

# Очистить корзину (удалить всё)
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/remote.php/dav/trashbin/$NEXTCLOUD_USER/trash"
```

---

## OCS Share API

Базовый URL: `$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1`

Все запросы требуют `-H "OCS-APIRequest: true"`.

### GET /shares — Все шары пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/shares?format=json" \
  -H "OCS-APIRequest: true"
```

### GET /shares — Шары конкретного файла/папки

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/shares?path=/Documents/file.pdf&format=json" \
  -H "OCS-APIRequest: true"
```

Аргументы:
- `path` (string, обязательный) — путь к файлу/папке
- `reshares` (boolean) — включить ре-шары
- `subfiles` (boolean) — шары внутри папки

### GET /shares/{shareId} — Информация о шаре

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/shares/{shareId}?format=json" \
  -H "OCS-APIRequest: true"
```

### POST /shares — Создать шару

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/shares" \
  -H "OCS-APIRequest: true" \
  -d "path={path}" \
  -d "shareType={type}" \
  -d "shareWith={recipient}" \
  -d "permissions={permissions}" \
  -d "password={password}" \
  -d "expireDate={YYYY-MM-DD}"
```

**shareType:**
| Значение | Тип |
|---|---|
| 0 | Пользователь |
| 1 | Группа |
| 3 | Публичная ссылка |
| 4 | Email |
| 6 | Федеративный (другой Nextcloud) |
| 7 | Circle |
| 10 | Talk-беседа |

**permissions (битовая маска):**
| Бит | Значение | Описание |
|---|---|---|
| 1 | read | Чтение |
| 2 | update | Обновление |
| 4 | create | Создание |
| 8 | delete | Удаление |
| 16 | share | Переделивание |
| 31 | all | Все права |

Обязательные поля: `shareType`, `path`. Для `shareType=0` и `shareType=1` также обязателен `shareWith`.

Дополнительные аргументы:
- `publicUpload` (string, "true"/"false") — разрешить публичную загрузку
- `password` (string) — пароль для публичной ссылки
- `expireDate` (string, "YYYY-MM-DD") — дата истечения
- `note` (string) — заметка для получателя
- `label` (string) — метка для ссылки

**Коды ответа:** 100=ок, 400=неизвестный тип, 403=публичная загрузка отключена, 404=файл не найден

### PUT /shares/{shareId} — Обновить шару

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X PUT \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/shares/{shareId}" \
  -H "OCS-APIRequest: true" \
  -d "permissions=1" \
  -d "password=NewPassword" \
  -d "expireDate=2025-06-01"
```

Можно менять: `permissions`, `password`, `expireDate`, `publicUpload`, `note`.

### DELETE /shares/{shareId} — Удалить шару

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/shares/{shareId}" \
  -H "OCS-APIRequest: true"
```

### Федеративные шары

```bash
# Список входящих ожидающих
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/remote_shares/pending?format=json" \
  -H "OCS-APIRequest: true"

# Принять
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/remote_shares/pending/{shareId}" \
  -H "OCS-APIRequest: true"

# Отклонить
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/ocs/v2.php/apps/files_sharing/api/v1/remote_shares/pending/{shareId}" \
  -H "OCS-APIRequest: true"
```

---

## User Provisioning API

Базовый URL: `$NEXTCLOUD_URL/ocs/v1.php/cloud`

Требует admin-токен. Все запросы: `-H "OCS-APIRequest: true"`.

### GET /users — Список пользователей

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users?format=json" \
  -H "OCS-APIRequest: true"
```

Аргументы: `search` (string), `limit` (int), `offset` (int)

### POST /users — Создать пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users" \
  -H "OCS-APIRequest: true" \
  -d "userid={userid}" \
  -d "password={password}" \
  -d "displayName={name}" \
  -d "email={email}" \
  -d "groups[]={group1}" \
  -d "quota={quota}"
```

Аргументы:
- `userid` (string, обязательный) — логин
- `password` (string) — пароль (если пуст, будет отправлено приветственное письмо)
- `displayName` (string) — отображаемое имя
- `email` (string) — email (обязателен если пароль пуст)
- `groups[]` (array) — группы
- `subadmin[]` (array) — группы субадмина
- `quota` (string) — квота (например "1 GB", "500 MB")
- `language` (string) — язык

**Коды:** 100=ок, 101=невалидные данные, 102=пользователь существует, 103=ошибка создания, 104=группа не существует, 105=недостаточно прав, 108=нужен пароль или email

### GET /users/{userid} — Детали пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}?format=json" \
  -H "OCS-APIRequest: true"
```

Возвращает: `enabled`, `storageLocation`, `id`, `lastLogin`, `backend`, `subadmin`, `quota`, `email`, `displayname`, `phone`, `address`, `website`, `groups`

### PUT /users/{userid} — Редактировать пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X PUT \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}" \
  -H "OCS-APIRequest: true" \
  -d "key={key}" \
  -d "value={value}"
```

Доступные ключи `key`:
| Ключ | Описание |
|---|---|
| `email` | Email адрес |
| `quota` | Квота ("1 GB", "none", "default") |
| `displayname` | Отображаемое имя |
| `phone` | Телефон |
| `address` | Адрес |
| `website` | Веб-сайт |
| `twitter` | Аккаунт Twitter |
| `password` | Пароль |
| `language` | Язык интерфейса |
| `locale` | Локаль |

**Коды:** 100=ок, 101=пользователь не найден, 102=невалидные данные

### PUT /users/{userid}/disable — Выключить пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X PUT \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}/disable" \
  -H "OCS-APIRequest: true"
```

### PUT /users/{userid}/enable — Включить пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X PUT \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}/enable" \
  -H "OCS-APIRequest: true"
```

### DELETE /users/{userid} — Удалить пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}" \
  -H "OCS-APIRequest: true"
```

**Коды:** 100=ок, 101=не найден

### GET /users/{userid}/groups — Группы пользователя

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}/groups?format=json" \
  -H "OCS-APIRequest: true"
```

### POST /users/{userid}/groups — Добавить в группу

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}/groups" \
  -H "OCS-APIRequest: true" \
  -d "groupid={groupid}"
```

**Коды:** 100=ок, 101=нет такого пользователя, 102=нет такой группы, 103=ошибка добавления, 104=недостаточно прав

### DELETE /users/{userid}/groups — Удалить из группы

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}/groups" \
  -H "OCS-APIRequest: true" \
  -d "groupid={groupid}"
```

### POST /users/{userid}/subadmins — Назначить субадмином группы

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/users/{userid}/subadmins" \
  -H "OCS-APIRequest: true" \
  -d "groupid={groupid}"
```

### GET /user — Текущий пользователь

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/user?format=json" \
  -H "OCS-APIRequest: true"
```

Возвращает метаданные текущего авторизованного пользователя. Не требует admin-токен.

---

## Groups API

Базовый URL: `$NEXTCLOUD_URL/ocs/v1.php/cloud/groups`

### GET /groups — Список групп

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/groups?format=json" \
  -H "OCS-APIRequest: true"
```

Аргументы: `search` (string), `limit` (int), `offset` (int)

### POST /groups — Создать группу

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/groups" \
  -H "OCS-APIRequest: true" \
  -d "groupid={groupid}"
```

**Коды:** 100=ок, 101=невалидные данные, 102=группа существует, 103=ошибка создания

### GET /groups/{groupid} — Участники группы

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/groups/{groupid}?format=json" \
  -H "OCS-APIRequest: true"
```

### GET /groups/{groupid}/subadmins — Субадмины группы

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/groups/{groupid}/subadmins?format=json" \
  -H "OCS-APIRequest: true"
```

**Коды:** 100=ок, 101=группа не существует, 102=ошибка

### DELETE /groups/{groupid} — Удалить группу

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/groups/{groupid}" \
  -H "OCS-APIRequest: true"
```

**Коды:** 100=ок, 101=нет такой группы, 102=ошибка удаления

---

## Apps API

Базовый URL: `$NEXTCLOUD_URL/ocs/v1.php/cloud/apps`

### GET /apps — Список приложений

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/apps?format=json" \
  -H "OCS-APIRequest: true"
```

Аргумент `filter`: `enabled` или `disabled`

### GET /apps/{appid} — Информация о приложении

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X GET \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/apps/{appid}?format=json" \
  -H "OCS-APIRequest: true"
```

### POST /apps/{appid} — Включить приложение

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X POST \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/apps/{appid}" \
  -H "OCS-APIRequest: true"
```

### DELETE /apps/{appid} — Выключить приложение

```bash
curl -u "$NEXTCLOUD_USER:$NEXTCLOUD_ADMIN_TOKEN" \
  -X DELETE \
  "$NEXTCLOUD_URL/ocs/v1.php/cloud/apps/{appid}" \
  -H "OCS-APIRequest: true"
```

---

## Коды ошибок

### HTTP-коды
| Код | Описание |
|---|---|
| 200 | Успех |
| 201 | Создано (WebDAV) |
| 204 | Нет содержимого (удаление OK) |
| 207 | Multi-Status (PROPFIND) |
| 400 | Неверный запрос |
| 401 | Не авторизован |
| 403 | Запрещено |
| 404 | Не найдено |
| 405 | Метод не разрешён |
| 409 | Конфликт (родительская директория не существует) |
| 412 | Предусловие не выполнено |
| 423 | Заблокировано |
| 507 | Недостаточно места |

### OCS-коды (v1 API)
| Код | Описание |
|---|---|
| 100 | Успех |
| 101 | Невалидные входные данные |
| 102 | Ресурс уже существует |
| 103 | Ошибка при создании |
| 104 | Ресурс не найден (группа/пользователь) |
| 105 | Недостаточно привилегий |
| 997 | Не авторизован (пропущен OCS-APIRequest) |
| 998 | Не авторизован |
| 999 | Ошибка (общая) |

### OCS-коды (v2 API)
OCS v2 API маппит коды на стандартные HTTP: 100→200, 400→400, 404→404, и т.д.
