---
name: telegram-formatting
description: "Telegram Rich Markdown formatting: syntax, limits, delivery, banners, inline images. Use when preparing Telegram replies via gateway: GFM tables, task lists, details, sendRichMessage vs MarkdownV2, MEDIA vs HTTPS ![](), placehold.co banners, image generation, uguu hotlink, tg-collage, tg-emoji. Triggers: telegram, rich markdown, sendRichMessage, MarkdownV2, MEDIA, placehold, inline photo, banner, caption, checklist."
version: 3.2.0
author: NorD (nordz0r), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telegram, formatting, rich-messages, markdown, bot-api]
    related_skills: [telegram-bot-management, telegram-cron-image-conventions]
---

# Telegram Formatting Skill

Как агенту готовить текст для Telegram: пиши обычный GitHub-Flavored Markdown,
gateway сам выбирает путь доставки — legacy MarkdownV2 или Rich Messages
(`sendRichMessage`, Bot API 10.x). Агент не вызывает Bot API напрямую, не
эскейпит текст и не режет сообщения. Скилл описывает синтаксис Rich Markdown,
триггеры rich-пути, лимиты, политику картинок и типовые ошибки.

## When to Use

- Готовишь любой ответ, который уйдёт в Telegram через gateway.
- Выбираешь, как подать контент: таблица, чек-лист, код, спойлер, формула.
- Текст длинный или структурный — решаешь, что отправить сообщением, а что файлом.
- Нужен баннер секции, inline-картинка или `MEDIA:`-файл.

Don't use for: настройку gateway (`hermes config`), вызов Bot API из скриптов
напрямую. Доставка локальных файлов — через `MEDIA:` (см. ниже). `hermes send`
остаётся MarkdownV2/HTML; живые no_agent cron-скрипты с прямым
`sendRichMessage` — исключение (см. Pitfalls). Практические cron-примеры:
skill `telegram-cron-image-conventions`.

## How Delivery Works

Один текст агента — два пути доставки, выбор делает gateway:

| | MarkdownV2 (default) | Rich Messages |
|---|---|---|
| Когда | обычный текст | есть rich-конструкция (ниже) |
| Лимит | 4 096 символов | 32 768 символов |
| Синтаксис | Markdown → конвертация в MarkdownV2 | твой GFM уходит как Rich Markdown |
| Заголовки `#`, таблицы | сплющиваются | рендерятся нативно |

Rich-путь включается автоматически, если в тексте есть хотя бы одно из:

- **GFM-таблица** — строка-разделитель вида `|---|---|`
- **Task list** — `- [ ]` или `- [x]` в начале строки
- **`<details>`-блок** — теги `<details>`, `<summary>`
- **Block math** — `$$...$$`

Следствие: **обычный текст (жирный, списки, код) всегда идёт по MarkdownV2** —
заголовки `##` в нём не станут section headings. Чтобы получить богатый рендер,
включи в ответ хотя бы одну rich-конструкцию (таблицу, task list, details).

Правила текста:

- Пиши чистый GFM. Не экранируй символы под MarkdownV2 — на MDv2-пути это
  делает gateway, а на rich-пути твои `\` уйдут в текст как есть.
- Rich Markdown совместим с GFM «где возможно», поэтому `**bold**` и
  `*italic*` безопасны на обоих путях. Однострочные переносы gateway
  нормализует в жёсткие переводы строк.

## Rich Markdown Cheat Sheet

Полный синтаксис поля `markdown` в `InputRichMessage`:

```
**bold**  __bold__  *italic*  _italic_  ~~strike~~  ==marked==  ||spoiler||
`inline code`   [текст](https://…)   [письмо](mailto:u@x.ru)   [тел](tel:+7…)
[упоминание](tg://user?id=123)   $inline math$   ```lang …``` (блок кода)
$$E=mc^2$$  или  ```math …```   ---  (разделитель)

# H1 … ###### H6
- / * / +  маркированный список;   1. 2. нумерованный
- [ ] незавершённое дело;  - [x] завершённое
> цитата (пустая строка `>` между абзацами разделяет)
![](https://…/photo.jpg)  медиа-блок;  ![](url "подпись")  с caption
| Кол1 | Кол2 |  GFM-таблица с выравниванием `|:---|---:|`
Сноска[^id] … [^id]: расшифровка
```

Автодетект сущностей (без разметки): URL, e-mail, телефоны, номера карт,
`#hashtag`, `$cashtag`, `/command`, `@username`.

HTML-теги для того, у чего нет markdown-синтаксиса:

- `<u>`, `<ins>` — подчёркнутый; `<sub>`, `<sup>` — индексы
- `<a name="anchor"></a>` — якорь для внутренних ссылок
- `<aside>цитата<cite>Автор</cite></aside>` — pull quote
- `<details open><summary>Заголовок</summary>…</details>` — сворачиваемый блок
- `<tg-map lat="41.9" long="12.5" zoom="14"/>` — карта
- `<tg-collage>` / `<tg-slideshow>` — галереи из `![]()` или `<img>`
- `<tg-button type="url" url="…" style="success">Текст</tg-button>` и
  `<tg-button-row align="center">` — inline-кнопки (типы: `url`,
  `callback_data`, `web_app`, `login_url`, `switch_inline_query*`,
  `copy_text`, `disabled`; стили: `primary`, `success`, `danger`, `link`)
- `<tg-emoji emoji-id="…">👍</tg-emoji>`, `<tg-time unix="…" format="t">`
- `<tg-thinking>…</tg-thinking>` — только в черновиках стриминга (см. ниже)

Ограничения парсера: markdown внутри блочных HTML-тегов не парсится, кроме
`<details>`, `<tg-collage>`, `<tg-slideshow>`; в ячейках таблиц — только
inline-форматирование; медиа — только отдельным блоком и только HTTP(S).

## Streaming & Drafts

При `streaming.enabled` + `rich_drafts: true` (на dd включено) черновик в ЛС
стримится через `sendRichMessageDraft`: пользователь видит живой предпросмотр
с анимацией, черновик живёт ~30 секунд и заменяется финальным
`sendRichMessage`. `<tg-thinking>` допустим только в черновике — визуальный
индикатор «агент думает».

Для агента это значит: не пиши «сообщение ниже — черновик» и не рассчитывай,
что промежуточный текст останется в чате; финализирует gateway. В группах
стриминг деградирует до редактирования (`edit`).

## Limits

| Лимит | Значение |
|---|---|
| Текст rich-сообщения | 32 768 UTF-8 символов |
| Блоки (включая вложенные, строки таблиц, пункты списков) | 500 |
| Вложенность форматирования и блоков | 16 уровней |
| Медиа-вложения | 50 |
| Колонок в таблице | 20 |
| Обычное сообщение (MarkdownV2) | 4 096 символов |

## Long Content & Media

- До ~30 000 символов структурного текста — отправляй сообщением (rich-путь
  поднимает лимит с 4 096).
- Больше (длинные отчёты, логи, дампы) — файлом: положи на диск и укажи
  `MEDIA:/абсолютный/путь` в ответе; в сообщении дай краткую выжимку. Подробный
  отчёт может дублироваться приложением `.md`/`.pdf`.
- Медиа в тексте: `![](https://…)` (photo/video/audio/ogg-voice/animation/
  document определяется по MIME и расширению), `"подпись"` после URL — caption.
  Галереи — `<tg-collage>`/`<tg-slideshow>`; повторно загруженные файлы —
  ссылки вида `tg://photo?id=…` (в паре с полем `media` у InputRichMessage).

### Когда картинку не берём

- Короткий фактический ответ без сравнения, схемы, инвентаря или карточки.
- Картинка не добавляет смысла — только шум. Текст остаётся текстом.

### placehold.co vs генерация

| Нужно | Чем |
|---|---|
| Баннер-заголовок дайджеста / секции | `placehold.co` |
| Схема, сравнение, иллюстрация смысла | генерация → публичный HTTPS → `![]()` |

**Баннер placehold.co** — только заголовок, не «рисунок»:

```markdown
![Software Updates](https://placehold.co/1200x300/0f172a/38bdf8/png?text=Software+Updates&font=montserrat)
```

- Размеры: `1200x300` (верх дайджеста) или `1200x500` (секция).
- `text=`: ASCII `[A-Za-z0-9 ._|-]`, 1–80 символов; без почты, PII, секретов.
- Язык подписи на баннере — чисто RU или чисто EN, без транслита.
- Отдельный блок + пустая строка вокруг; не стакать два placehold подряд.
- Алерт/откат: можно красную палитру (`450a0a` / `f87171`).

**Генерация** (OCX `POST /v1/images/generations`):

1. Primary: `google-antigravity/gemini-3.1-flash-image`
2. Fallback: `xai/grok-4.6` (если primary недоступен / квота)
3. GPT / DALL·E (`gpt-image-*`, `dall-e-*`) — **только если ID есть в**
   `/v1/models`; иначе не вызывать

Не генератор: `gemini-3.8-flash` (text/vision). После генерации:

1. Залей файл на публичный hotlink (uguu: `POST https://uguu.se/upload.php`,
   field `files[]` → `https://…/id.jpg`; проверь `image/*` и SOI JPEG).
2. Вставь в **то же** rich-сообщение: `![](https://…)` или
   `![](url "caption")` отдельным блоком.
3. Локальный файл для native photo — `MEDIA:/abs/path` своей строкой.
   Путь ФС и `file://` внутри `![]()` запрещены. URL вида
   `file/botTOKEN/…` в текст не класть (утечка токена).

### Brand custom emoji

Для известных брендов в дайджестах:

```html
<tg-emoji emoji-id="…">fallback</tg-emoji> BrandName
```

- Только из явной карты (не угадывать ID).
- Имя бренда после иконки обязательно.
- Не трогать code fences, URL, email, уже вставленные `<tg-emoji>`.

Практические примеры cron (software-update, GLM): skill
`telegram-cron-image-conventions`.

## Procedure

1. Разметь контент: таблицы, чек-листы, `<details>`, формулы — оформляй их
   нативным GFM/HTML, они сами поднимут rich-путь. Completion: каждая
   конструкция синтаксически закрыта (таблица с разделителем, `</details>`).
2. Мобильный формат: короткие абзацы, `- ` списки вместо простыней, `key:
   value` для мелких структурированных данных. Completion: абзацы ≤ 4 строк.
3. Проверь объём: ≤ 30 000 символов — сообщением; больше — выжимка +
   `MEDIA:`-файл. Completion: текст не превысит лимит после добавления
   подписей и таблиц.
4. Команды и пути — в code fence или inline code; важные для копирования
   данные не клади внутрь rich-таблиц (их неудобно копировать из клиента).
5. Картинки: нет смысла → без медиа; баннер секции → placehold; схема/
   сравнение → generate (Gemini → Grok) → uguu → `![](https://…)`.
   Локальный файл → `MEDIA:/abs`, не внутрь `![]()`. Completion: в ответе
   нет FS-путей внутри markdown-image и нет `file/bot` URL.

## Pitfalls

1. **Не эскейпь ничего сам.** `\.` и `\*` предназначены для ручного
   MarkdownV2; gateway конвертирует сам, а на rich-пути слэши уйдут в текст.
2. **Rich-триггеры — только 4 конструкции.** Обычный ответ со списками и
   жирным уйдёт по MarkdownV2: заголовки не отрисуются, таблица сплющится.
   Хочешь нативный рендер — добавь rich-конструкцию.
3. **Превью ссылок на rich-пути не отключается** — `disable_link_previews`
   действует только на MarkdownV2.
4. **`$$math$$` внутри `<details>`** — краш Telegram Desktop; адаптер сам
   уведёт такое сообщение с rich-пути. Не комбинируй.
5. **CJK-текст** искажается на rich-пути (баг Telegram Desktop/macOS);
   адаптер отфильтрует — сообщение уйдёт обычным MarkdownV2.
6. **Язык кода**: ` ```python ` на MDv2-пути теряет язык; rich сохраняет
   подсветку.
7. **Capability latch**: если `sendRichMessage` недоступен (старый PTB),
   адаптер выключает rich до конца сессии — не жди rich-рендера повторно.
8. **`hermes send` не использует rich** — только MarkdownV2/HTML с лимитом
   4 096. Исключение: живые no_agent cron-скрипты, которые зовут
   `sendRichMessage` напрямую (software-update, GLM, dd-host) — они идут
   мимо gateway и мимо `hermes send`.
9. **Конфиг читается на старте gateway**: смена `rich_messages`/
   `rich_drafts` требует рестарта gateway извне (из сессии рестарт заблокирован).

## Verification

- Отправь себе ответ с GFM-таблицей и `- [x]` — таблица должна отрисоваться
  нативно, а не код-блоком; чекбокс — интерактивным.
- В `~/.hermes/logs/gateway.log`: `grep -iE "rich|sendRich|rejected" | tail`
  — не должно быть `sendRichMessage rejected` / `unsupported`.
- Сообщение > 4 096 символов без rich-конструкций дошло по частям → добавь
  rich-конструкцию или файл.
- Баннер placehold и `![](https://…)` приходят inline в том же rich-пузыре;
  `MEDIA:/abs` уходит отдельным native photo.