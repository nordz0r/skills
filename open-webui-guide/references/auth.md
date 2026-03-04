# Авторизация и управление доступом

## Содержание
1. [Общая архитектура](#общая-архитектура)
2. [JWT-токены](#jwt-токены)
3. [Парольная аутентификация](#парольная-аутентификация)
4. [OAuth/OIDC](#oauthoidc)
5. [LDAP](#ldap)
6. [API-ключи](#api-ключи)
7. [Trusted Headers (прокси-авторизация)](#trusted-headers)
8. [SCIM-провизия](#scim-провизия)
9. [Роли и права](#роли-и-права)
10. [Группы и Access Grants](#группы-и-access-grants)
11. [Rate Limiting](#rate-limiting)
12. [Безопасность: чеклист для production](#безопасность)

---

## Общая архитектура

Open WebUI поддерживает 5 методов аутентификации, которые можно комбинировать:

```
Пользователь → [Пароль | OAuth | LDAP | API-ключ | Trusted Header] → JWT → API
```

Все методы в итоге выдают JWT-токен, который используется для авторизации API-запросов.

Ключевой файл: `backend/open_webui/routers/auths.py`

---

## JWT-токены

### Как устроены

- **Алгоритм**: HS256
- **Секрет**: `WEBUI_SECRET_KEY` (КРИТИЧНО: установи в production!)
- **Структура payload**: `{id, exp, jti}`
  - `id` — UUID пользователя
  - `exp` — время истечения
  - `jti` — уникальный идентификатор токена (для отзыва)
- **Время жизни**: настраивается через `JWT_EXPIRES_IN` (формат: `"30m"`, `"24h"`, `"7d"`)

### Cookie-хранение

```env
WEBUI_SESSION_COOKIE_SAME_SITE=lax    # lax | strict | none
WEBUI_AUTH_COOKIE_SECURE=true          # true для HTTPS
WEBUI_AUTH_COOKIE_HTTP_ONLY=true       # защита от XSS
```

### Отзыв токенов

Если настроен Redis, Open WebUI поддерживает отзыв токенов через JTI-blacklist:
- При logout токен добавляется в Redis-блэклист
- При каждом запросе проверяется, не отозван ли JTI

Без Redis отзыв токенов не работает — токен валиден до истечения `exp`.

---

## Парольная аутентификация

### Эндпоинты

```
POST /api/v1/auths/signin     — вход
POST /api/v1/auths/signup     — регистрация
```

### Хеширование паролей

- Используется **bcrypt** (ограничение: первые 72 байта пароля)
- Опциональная валидация сложности пароля:

```env
ENABLE_PASSWORD_VALIDATION=true
PASSWORD_VALIDATION_REGEX_PATTERN="^(?=.*[A-Z])(?=.*\d).{8,}$"
```

### Управление регистрацией

```env
ENABLE_SIGNUP=true                    # разрешить регистрацию
ENABLE_PASSWORD_AUTH=true             # разрешить вход по паролю
ENABLE_INITIAL_ADMIN_SIGNUP=true      # первый пользователь = admin
DEFAULT_USER_ROLE=pending             # роль по умолчанию: pending | user
```

Если `DEFAULT_USER_ROLE=pending`, новые пользователи не смогут ничего делать, пока администратор не одобрит их и не изменит роль на `user`.

---

## OAuth/OIDC

### Поддерживаемые провайдеры

Open WebUI поддерживает из коробки:
- **Google**
- **Microsoft**
- **GitHub**
- **Feishu (Lark)**
- **Любой OIDC-совместимый провайдер** (Keycloak, Auth0, Okta и т.д.)

### Настройка

Каждый провайдер настраивается через переменные окружения. Пример для Google:

```env
ENABLE_OAUTH_SIGNUP=true
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true

# Google
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_OAUTH_SCOPE="openid email profile"
GOOGLE_REDIRECT_URI=https://your-domain.com/oauth/google/callback
```

### Пример для generic OIDC (Keycloak)

```env
OAUTH_CLIENT_ID=open-webui
OAUTH_CLIENT_SECRET=your-secret
OAUTH_PROVIDER_NAME=Keycloak
OAUTH_OPENID_CONFIG_URL=https://keycloak.example.com/realms/master/.well-known/openid-configuration
OAUTH_SCOPES="openid email profile"
OAUTH_REDIRECT_URI=https://your-domain.com/oauth/oidc/callback
```

### Важные флаги

```env
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true    # слияние аккаунтов по email
OAUTH_MAX_SESSIONS_PER_USER=10        # лимит активных сессий
ENABLE_OAUTH_TOKEN_EXCHANGE=false     # обмен OAuth-токенов
ENABLE_OAUTH_ID_TOKEN_COOKIE=false    # ID-токен в cookie
```

### Подводный камень: слияние аккаунтов

Если `OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true`, пользователь с одинаковым email из разных провайдеров будет считаться одним аккаунтом. Это удобно, но создаёт риск: если злоумышленник контролирует email на другом провайдере, он получит доступ к существующему аккаунту.

---

## LDAP

### Настройка

```env
ENABLE_LDAP=true
LDAP_SERVER_HOST=ldap.example.com
LDAP_SERVER_PORT=389                  # 636 для LDAPS
LDAP_USE_TLS=true
LDAP_BIND_DN="cn=admin,dc=example,dc=com"
LDAP_BIND_PASSWORD=secret
LDAP_SEARCH_BASE="ou=users,dc=example,dc=com"
LDAP_SEARCH_FILTERS="(&(objectClass=person)(uid={username}))"
LDAP_ATTRIBUTE_FOR_MAIL=mail
LDAP_ATTRIBUTE_FOR_USERNAME=uid
```

### Эндпоинт

```
POST /api/v1/auths/ldap    — вход через LDAP
```

### Маппинг групп

LDAP-группы могут маппиться на роли Open WebUI. Настройка через дополнительные LDAP-атрибуты.

---

## API-ключи

### Генерация

```
POST /api/v1/auths/api-key    — создать ключ (требует авторизации)
```

### Формат

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Формат: префикс `sk-` + 32 hex-символа.

### Использование

```bash
curl -H "Authorization: Bearer sk-your-key-here" \
     https://your-domain.com/api/v1/chats
```

### Особенности

- Ключи хранятся в таблице `api_key` с полями `expires_at` и `last_used_at`
- Поддерживается ротация ключей
- Можно задать время истечения
- Администратор может отзывать ключи других пользователей

---

## Trusted Headers

Используется при работе за reverse proxy (nginx, Traefik, Cloudflare Access и т.д.), который уже выполнил аутентификацию.

```env
WEBUI_AUTH_TRUSTED_EMAIL_HEADER=X-Forwarded-Email
WEBUI_AUTH_TRUSTED_NAME_HEADER=X-Forwarded-Name
WEBUI_AUTH_TRUSTED_GROUPS_HEADER=X-Forwarded-Groups
```

**Внимание**: убедись, что эти заголовки не могут быть подделаны клиентом! Настрой proxy так, чтобы он перезаписывал эти заголовки.

---

## SCIM-провизия

SCIM 2.0 позволяет автоматически создавать/обновлять/удалять пользователей из корпоративных IdP (Azure AD, Okta).

```env
ENABLE_SCIM=true
SCIM_AUTH_HEADER=Authorization
SCIM_AUTH_TOKEN=your-scim-secret
```

Эндпоинты: `backend/open_webui/routers/scim.py`

---

## Роли и права

### Иерархия

```
admin > user > pending
```

### Что может каждая роль

| Действие | admin | user | pending |
|----------|-------|------|---------|
| Чаты с моделями | + | + | - |
| Загрузка файлов | + | + | - |
| Создание функций | + | - (настраивается) | - |
| Управление моделями | + | - | - |
| Управление пользователями | + | - | - |
| Системные настройки | + | - | - |
| Создание knowledge bases | + | + | - |

### Модельный доступ

Администратор может ограничить доступ к конкретным моделям:
- По пользователю
- По группе
- `BYPASS_MODEL_ACCESS_CONTROL=true` — отключить проверку доступа к моделям

### Группы

Группы позволяют объединять пользователей и назначать права массово. Создаются через API или админ-панель.

---

## Группы и Access Grants

### Access Grants

Система fine-grained access control. Позволяет делиться ресурсами:

```
resource_type: "knowledge" | "model" | "chat" | ...
target_type: "user" | "group"
access_level: "read" | "write" | "admin"
```

Это позволяет, например, расшарить knowledge base определённой группе с правом только чтения.

---

## Rate Limiting

Защита от перебора паролей:
- **Лимит**: 5 попыток входа за 3 минуты (на уровне IP)
- Настраивается в коде `auths.py`

---

## Безопасность

### Чеклист для production

1. **ОБЯЗАТЕЛЬНО** установи `WEBUI_SECRET_KEY` — без него JWT-секрет генерируется случайно при каждом перезапуске, что инвалидирует все сессии
2. Включи `WEBUI_AUTH_COOKIE_SECURE=true` если используешь HTTPS
3. Установи `WEBUI_SESSION_COOKIE_SAME_SITE=strict` для максимальной защиты
4. Если используешь Trusted Headers — убедись, что proxy перезаписывает их
5. Настрой `DEFAULT_USER_ROLE=pending` чтобы новые пользователи требовали одобрения
6. Включи `ENABLE_PASSWORD_VALIDATION=true` для сложных паролей
7. Настрой Redis для поддержки отзыва токенов
8. Используй `ENABLE_AUDIT_LOGS_FILE=true` для аудита
