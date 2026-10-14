<!-- Russian guide for SKILL.md. Paths relative to the skill root. -->

# Telegram Formatting Skill

Для ответа через Hermes gateway пиши GFM и учитывай правила установленного адаптера. Для явной интеграции через Bot API используй `InputRichMessage` в Rich HTML, Markdown или blocks. Builder `tg-rich-messages` создаёт HTML-пейлоад; он не отправляет запросы.

## When to Use

- Готовишь ответ для Telegram через gateway.
- Выбираешь таблицу, чек-лист, код, спойлер, формулу или изображение.
- Собираешь rich-пейлоад через Bot API или `tg-rich-messages`.

Не используй для настройки gateway, работы с токенами или реализации обработчика callback. `MEDIA:` — соглашение gateway, не синтаксис Telegram. См. [справочник Rich HTML](rich-html.md), [пример](../examples/rich-message.mjs) и [архивный снимок Hermes](adapter-internals.md).

## Gateway и Bot API — разные контракты

Install stamp установленного Hermes указывает v0.22.0, baseline commit `e06df9c2eae6901f4c88f464e0ae6e753c0428b8`, `dirty: true`; локальные правки могут влиять на поведение. В этом runtime rich-триггеры: GFM-таблица; task list с `-`/`*` и ` `, `x`/`X`; `<details>`/`<summary>`; `$$`; `PRLENS:`; отдельное HTTPS markdown-image; `<tg-emoji emoji-id=…>`. Rich-путь также требует opt-in и поддержки API; guards по форме/размеру могут выбрать MarkdownV2. Это профиль установленного хоста, не универсальное правило Telegram.

`InputRichMessage` принимает ровно одно поле `markdown`, `html` или `blocks`. Объект передают методу `sendRichMessage` как `rich_message`; `is_rtl` управляет направлением письма, `skip_entity_detection` отключает автоопределение сущностей. Повторно используемые Telegram media-ссылки требуют поля `media`. Rich HTML не является обычным `sendMessage(parse_mode="HTML")`.

## Rich Markdown

Частый синтаксис `markdown` по [спецификации Telegram](https://core.telegram.org/bots/api/rich-messages.md):

````markdown
**жирный** __жирный__ *курсив* _курсив_ ~~зачёркнутый~~ ==выделенный== ||спойлер||
`код` [ссылка](https://…) [почта](mailto:u@x.ru) [тел](tel:+7…)
[упоминание](tg://user?id=123) ![👍](tg://emoji?id=5368324170671202286)
![время](tg://time?unix=1647531900&format=wDT) $inline math$
```python …```   ```math …```   $$E=mc^2$$   ---

# H1 … ###### H6
- / * / + маркированный список; 1. 2. нумерованный
- [ ] незавершённое дело; - [x] выполненное
> цитата
![](https://…/photo.jpg "подпись")
| Колонка | Значение |
|:---|---:|
| Скорость | 42 |
Сноска[^id] … [^id]: расшифровка
````

Автоматически обнаруживаются URL, e-mail, упоминания, хештеги, cashtag, команды бота, телефоны и номера банковских карт. Отключить автодетект можно через `skip_entity_detection`.

## Rich HTML и builder

Дополнительно доступны `<footer>`, `<br>`, `<tg-math>`/`<tg-math-block>`, якоря и `<tg-reference>`, раскрываемые цитаты, списки с `start`/`type`/`reversed`, чекбоксы, таблицы с `caption`, `colspan`, `rowspan`, `align` и `valign`, карты, подписи и кредиты медиа, спойлеры, документы, коллажи, слайдшоу и кнопки. Подробности — в [справочнике Rich HTML](rich-html.md).

Markdown внутри блочных HTML-тегов не разбирается, кроме `<details>`, `<tg-collage>` и `<tg-slideshow>`; в таблицах разрешено только inline-форматирование. Медиа — отдельный блок по HTTP(S). `tg://photo|video|document|audio?id=…` с соответствующим полем `media` повторно использует загруженный файл. `tg://emoji` и `tg://time` — inline-сущности, не media URL. Формат даты/времени: `r|w?[dD]?[tT]?`; `r` нельзя комбинировать с другими флагами.

Builder `tg-rich-messages@0.4.0` требует Node.js `^22.0.0 || >=24.0.0`; установка явная в проекте-потребителе. Перед сериализацией вызови `message.validate()`: `toInputRichMessage()` не валидирует автоматически. Валидатор приблизительно считает текст и не обходит вложенность inline-узлов. `unsafeRawInline()` вставляет HTML без экранирования — только доверенные константы. Экранирование не подтверждает безопасность URL, ID или права на действие кнопки. `callback_data` требует серверного обработчика; `web_app` работает только в личных чатах, домен `login_url` должен быть настроен через BotFather.

## Streaming & Drafts

Если установленный gateway и API поддерживают rich draft, черновик может отправляться через `sendRichMessageDraft`. `<tg-thinking>` предназначен только для черновика. Builder создаёт разметку и не включает стриминг; отправитель должен доставить финальное сообщение. Групповой транспорт и другие детали зависят от адаптера.

## Limits

| Лимит Telegram Rich | Значение |
|---|---:|
| Текст, включая fallback custom emoji и исходник формулы | 32 768 символов |
| Блоки, включая вложенные, пункты списков и строки таблиц | 500 |
| Вложенность форматирования и блоков | 16 уровней |
| Медиа-вложения | 50 |
| Колонки таблицы | 20 |
| Обычное сообщение | 4 096 символов |

## Long Content & Media

Длинные отчёты и логи передавай файлом через `MEDIA:/абсолютный/путь`, добавив краткую выжимку. `MEDIA:` — соглашение gateway; не вставляй путь ФС или `file://` в `![]()`.

Inline-медиа задавай отдельным блоком `![](https://… "подпись")`. Добавляй картинку, только если она несёт смысл: схема/сравнение — генерация, заголовок секции — баннер.

### Когда картинка не нужна

- Короткий фактический ответ без сравнения, схемы, инвентаря или карточки.
- Картинка не добавляет смысла — только шум.

### placehold.co и генерация

Баннер `placehold.co` — заголовок, не иллюстрация:

```markdown
![Software Updates](https://placehold.co/1200x300/0f172a/38bdf8/png?text=Software+Updates&font=montserrat)
```

- Размеры: `1200x300` (дайджест) или `1200x500` (секция).
- `text=`: ASCII `[A-Za-z0-9 ._|-]`, 1–80 символов; без e-mail, PII и секретов.
- Язык текста баннера — русский или английский, без транслита.
- Отдельный блок с пустыми строками; не стакать баннеры подряд.
- Для алерта/отката допустима красная палитра (`450a0a` / `f87171`).

Для смысловой иллюстрации в OCX `POST /v1/images/generations`:

1. Основная модель: `google-antigravity/gemini-3.1-flash-image`.
2. Fallback: `xai/grok-4.6`, если основная недоступна или исчерпана квота.
3. GPT/DALL·E (`gpt-image-*`, `dall-e-*`) — только если ID есть в `/v1/models`; `gemini-3.8-flash` — text/vision, не генератор.

До публикации убедись, что изображение не содержит приватных данных, секретов или внутренних интерфейсов. Оба хостинга публичные; чувствительные скриншоты передавай только через `MEDIA:`.

1. **Основной — jpg.wtf** (анонимно, до 30 МБ):
   `curl -s --max-time 30 -F file=@file https://jpg.wtf/api/upload.php | jq -r 'select(.status=="ok") | .url // empty'`. Выводи только `.url`, не допускай утечки `delete_url`; используй URL `www.jpg.wtf` как есть.
2. **Fallback — pixhost** (анонимный API, до 10 МБ):
   `curl -s --max-time 30 -H 'Accept: application/json' -F img=@file -F content_type=0 -F max_th_size=150 https://api.pixhost.to/images`. Используй прямой URL `imgN.pixhost.to/images/...`, не thumbnail.
3. Нет `status == ok` и `.url`, ошибка или таймаут jpg.wtf → pixhost. Pixhost тоже недоступен → `MEDIA:`. Доступность/условия хостингов меняются.
4. Проверь HTTP 200 без редиректа, `Content-Type: image/jpeg|png|webp` и `Content-Length` ≤ 5 МБ (ограничение Telegram для фото по URL). Нет длины или больше 5 МБ (до 10 МБ) → `MEDIA:`.
5. Вставь `![](https://…)` отдельным блоком в то же rich-сообщение. Не публикуй путь ФС, `file://` или `file/botTOKEN/...`.

### Brand custom emoji

Для бренда в дайджесте:

```html
<tg-emoji emoji-id="…">fallback</tg-emoji> BrandName
```

- Используй ID только из явной карты, не угадывай их.
- После emoji обязательно укажи имя бренда обычным текстом.
- Не изменяй code fences, URL, email и уже вставленные `<tg-emoji>`.

Практические cron-примеры: skill `telegram-cron-image-conventions`.

## Procedure

1. Выбери контракт: GFM для gateway или Rich HTML/builder для явной интеграции. Закрой теги, fences и таблицы; выбери ровно одно поле `html`/`markdown`/`blocks` и валидируй builder-пейлоад.
2. Используй короткие абзацы, списки и ясные подписи. Команды и пути пиши в code fence/inline code; копируемые значения не прячь в таблицах.
3. Для медиа проверь смысл, конфиденциальность, MIME и доступность URL. Локальный файл передавай через `MEDIA:/abs`.

## Pitfalls

- Не экранируй GFM вручную как MarkdownV2. Для Rich HTML экранируй данные или используй builder.
- Rich-триггеры выше — особенность локального Hermes v0.22.0, не ограничение API; проверь версию, настройку и guards.
- Спецификация поддерживает формулу внутри `<details>`. Обход возможного сбоя TDesktop/CJK — версионная мера адаптера.
- Для подсветки кода используй markdown fence или `<pre><code class="language-python">`; standalone `<code>` язык не задаёт.
- `hermes send` и прямой `sendRichMessage` — разные механизмы; не переноси ограничения одного на другой.
- Изменение gateway-конфигурации может требовать рестарта; сверяйся с установленным адаптером.

## Verification

- Скопируй [пример builder](../examples/rich-message.mjs) в проект с установленным `tg-rich-messages@0.4.0` и запусти его. Он выводит JSON, не отправляя запрос.
- End-to-end доставку и рендер проверяй отдельно в целевом Telegram-клиенте. Payload не доказывает рендер; task checkbox сам по себе не реализует workflow.
- Для проверки gateway изучи журнал rejection/fallback и учитывай версию адаптера.
- Отличай inline HTTPS-медиа в rich-пузыре от отдельного вложения `MEDIA:/abs`.

## References

- [Rich HTML и builder](rich-html.md) — синтаксис, безопасность и пример.
- [Telegram Rich Messages](https://core.telegram.org/bots/api/rich-messages.md) — первичная спецификация.
- [Hermes adapter internals](adapter-internals.md) — архивный снимок v0.18.2; актуальные правила проверяй в установленной версии.
