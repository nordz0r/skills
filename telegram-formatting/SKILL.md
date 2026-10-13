---
name: telegram-formatting
description: "Telegram Rich Markdown formatting: syntax, limits, delivery, banners, inline images. Use when preparing Telegram replies via gateway: GFM tables, task lists, details, sendRichMessage vs MarkdownV2, MEDIA vs HTTPS ![](), placehold.co banners, image generation, jpg.wtf hotlink, pixhost fallback, tg-collage, tg-emoji. Triggers: telegram, rich markdown, sendRichMessage, MarkdownV2, MEDIA, placehold, inline photo, banner, caption, checklist, телеграм, форматирование, таблица, баннер, картинка."
license: MIT
metadata:
  version: "3.3.1"
  author: "NorD (nordz0r), Hermes Agent"
  platforms: "linux,macos,windows"
  hermes:
    tags: [telegram, formatting, rich-messages, markdown, bot-api]
    related_skills: [telegram-bot-management, telegram-cron-image-conventions]
---

# Telegram Formatting Skill

How an agent prepares text for Telegram: write plain GitHub-Flavored Markdown;
the gateway picks the delivery path itself — legacy MarkdownV2 or Rich Messages
(`sendRichMessage`, Bot API 10.x). The agent does not call the Bot API directly,
does not escape text and does not split messages. This skill covers Rich
Markdown syntax, rich-path triggers, limits, image policy and common mistakes.

## When to Use

- You are preparing any reply that will go to Telegram via the gateway.
- You are choosing how to present content: table, checklist, code, spoiler, formula.
- The text is long or structured — deciding what goes as a message and what as a file.
- You need a section banner, an inline image or a `MEDIA:` file.

Don't use for: gateway configuration (`hermes config`), calling the Bot API
directly from scripts. Local files are delivered via `MEDIA:` (see below).
`hermes send` stays MarkdownV2/HTML; live no_agent cron scripts calling
`sendRichMessage` directly are the exception (see Pitfalls). Practical cron
examples: skill `telegram-cron-image-conventions`.

## How Delivery Works

One agent text — two delivery paths; the gateway chooses:

| | MarkdownV2 (default) | Rich Messages |
|---|---|---|
| When | plain text | a rich construct is present (below) |
| Limit | 4,096 characters | 32,768 characters |
| Syntax | Markdown → converted to MarkdownV2 | your GFM is sent as Rich Markdown |
| `#` headings, tables | flattened | rendered natively |

The rich path is enabled automatically if the text contains at least one of:

- **GFM table** — a separator row like `|---|---|`
- **Task list** — `- [ ]` or `- [x]` at the start of a line
- **`<details>` block** — `<details>`, `<summary>` tags
- **Block math** — `$$...$$`

Consequence: **plain text (bold, lists, code) always goes via MarkdownV2** —
`##` headings in it will not become section headings. To get a rich render,
include at least one rich construct (table, task list, details).

Text rules:

- Write clean GFM. Do not escape characters for MarkdownV2 — on the MDv2 path
  the gateway does it, and on the rich path your `\` end up in the text as is.
- Rich Markdown is GFM-compatible "where possible", so `**bold**` and
  `*italic*` are safe on both paths. The gateway normalizes single line breaks
  into hard line breaks.

## Rich Markdown Cheat Sheet

Full syntax of the `markdown` field in `InputRichMessage`:

```
**bold**  __bold__  *italic*  _italic_  ~~strike~~  ==marked==  ||spoiler||
`inline code`   [text](https://…)   [email](mailto:u@x.ru)   [phone](tel:+7…)
[mention](tg://user?id=123)   $inline math$   ```lang …``` (code block)
$$E=mc^2$$  or  ```math …```   ---  (divider)

# H1 … ###### H6
- / * / +  bulleted list;   1. 2. numbered
- [ ] open task;  - [x] done task
> quote (an empty `>` line between paragraphs separates them)
![](https://…/photo.jpg)  media block;  ![](url "caption")  with caption
| Col1 | Col2 |  GFM table with alignment `|:---|---:|`
Footnote[^id] … [^id]: explanation
```

Entity autodetection (no markup): URLs, e-mails, phone numbers, card numbers,
`#hashtag`, `$cashtag`, `/command`, `@username`.

HTML tags for things that have no markdown syntax:

- `<u>`, `<ins>` — underline; `<sub>`, `<sup>` — sub/superscript
- `<a name="anchor"></a>` — anchor for internal links
- `<aside>quote<cite>Author</cite></aside>` — pull quote
- `<details open><summary>Title</summary>…</details>` — collapsible block
- `<tg-map lat="41.9" long="12.5" zoom="14"/>` — map
- `<tg-collage>` / `<tg-slideshow>` — galleries from `![]()` or `<img>`
- `<tg-button type="url" url="…" style="success">Text</tg-button>` and
  `<tg-button-row align="center">` — inline buttons (types: `url`,
  `callback_data`, `web_app`, `login_url`, `switch_inline_query*`,
  `copy_text`, `disabled`; styles: `primary`, `success`, `danger`, `link`)
- `<tg-emoji emoji-id="…">👍</tg-emoji>`, `<tg-time unix="…" format="t">`
- `<tg-thinking>…</tg-thinking>` — only in streaming drafts (see below)

Parser limits: markdown inside block HTML tags is not parsed, except
`<details>`, `<tg-collage>`, `<tg-slideshow>`; table cells allow only inline
formatting; media only as a separate block and only HTTP(S).

## Streaming & Drafts

With `streaming.enabled` + `rich_drafts: true` (enabled on dd) the draft in DMs
is streamed via `sendRichMessageDraft`: the user sees a live animated preview;
the draft lives ~30 seconds and is replaced by the final `sendRichMessage`.
`<tg-thinking>` is allowed only in a draft — a visual "agent is thinking"
indicator.

For the agent this means: don't write "the message below is a draft" and don't
expect intermediate text to stay in the chat; the gateway finalizes. In groups
streaming degrades to editing (`edit`).

## Limits

| Limit | Value |
|---|---|
| Rich message text | 32,768 UTF-8 characters |
| Blocks (incl. nested, table rows, list items) | 500 |
| Formatting and block nesting | 16 levels |
| Media attachments | 50 |
| Table columns | 20 |
| Regular message (MarkdownV2) | 4,096 characters |

## Long Content & Media

- Up to ~30,000 characters of structured text — send as a message (the rich
  path raises the limit from 4,096).
- More (long reports, logs, dumps) — as a file: put it on disk and add
  `MEDIA:/absolute/path` in the reply; give a short summary in the message. A
  detailed report may be duplicated as an `.md`/`.pdf` attachment.
- Media in text: `![](https://…)` (photo/video/audio/ogg-voice/animation/
  document is detected by MIME and extension), `"caption"` after the URL.
  Galleries — `<tg-collage>`/`<tg-slideshow>`; re-uploaded files — links like
  `tg://photo?id=…` (paired with the `media` field of InputRichMessage).

### When not to use an image

- A short factual answer with no comparison, diagram, inventory or card.
- The image adds no meaning — only noise. Text stays text.

### placehold.co vs generation

| Need | Use |
|---|---|
| Digest / section header banner | `placehold.co` |
| Diagram, comparison, illustration of meaning | generation → public HTTPS → `![]()` |

**placehold.co banner** — a header only, not a "picture":

```markdown
![Software Updates](https://placehold.co/1200x300/0f172a/38bdf8/png?text=Software+Updates&font=montserrat)
```

- Sizes: `1200x300` (top of a digest) or `1200x500` (section).
- `text=`: ASCII `[A-Za-z0-9 ._|-]`, 1–80 characters; no email, PII, secrets.
- Banner caption language — pure RU or pure EN, no transliteration.
- Separate block with an empty line around it; don't stack two placeholds.
- Alert/rollback: a red palette is OK (`450a0a` / `f87171`).

**Generation** (OCX `POST /v1/images/generations`):

1. Primary: `google-antigravity/gemini-3.1-flash-image`
2. Fallback: `xai/grok-4.6` (if primary is unavailable / out of quota)
3. GPT / DALL·E (`gpt-image-*`, `dall-e-*`) — **only if the ID is present in**
   `/v1/models`; otherwise don't call

Not a generator: `gemini-3.8-flash` (text/vision). After generation:

1. Publish the file over public HTTPS (hosting order):
   - **Privacy:** both hosts are public. Screenshots with personal data,
     tokens/secrets or internal systems — **only `MEDIA:`**, never
     jpg.wtf/pixhost.
   - **Primary — jpg.wtf** (Leprosorium hosting, origin and CDN in Russia;
     anonymous, no key or captcha, up to 30 MB):
     `curl -s --max-time 30 -F file=@file https://jpg.wtf/api/upload.php |
     jq -r 'select(.status=="ok") | .url // empty'` → `url` from the JSON
     `{"status":"ok","url":"https://www.jpg.wtf/<hash>.png","delete_url":…}`.
     Extract only `.url`, never print the whole JSON: `delete_url` must not
     reach logs, output or the chat. Use `url` as is (the `www.` host serves
     `image/*` without a redirect, while bare `jpg.wtf/<hash>` returns 302).
   - **Fallback — pixhost** (anonymous API, no key, up to 10 MB):
     `curl -s --max-time 30 -H 'Accept: application/json' -F img=@file
     -F content_type=0 -F max_th_size=150 https://api.pixhost.to/images` →
     `th_url`
     `https://tN.pixhost.to/thumbs/…`; direct URL =
     `https://imgN.pixhost.to/images/…` (replace `tN`→`imgN`, `thumbs`→`images`).
   - **Fallback rule:** jpg.wtf may answer HTTP 200 with `"status":"err"`.
     No `status` == `ok` together with `url` (empty `jq` output), or curl
     failed / timed out → pixhost. pixhost failed too → `MEDIA:`.
   - Do not use: uguu (502 from dd), 0x0.st (closed, ToS forbids AI images),
     telegra.ph/upload (disabled since 2024), hosts behind Cloudflare without
     a proxy (from dd the connection drops at ~20 KB).
2. Check the URL: `curl -sI --max-time 30` → `200`, `Content-Type:
   image/jpeg|png|webp` without a redirect, `Content-Length` ≤ 5 MB (Telegram
   limit for photos by URL). No `Content-Length` or more than 5 MB (up to
   10 MB) — `MEDIA:` only.
3. Insert into the **same** rich message: `![](https://…)` or
   `![](url "caption")` as a separate block.
4. Local file for a native photo — `MEDIA:/abs/path` on its own line
   (emergency path without hosting). Filesystem paths and `file://` inside
   `![]()` are forbidden. Never put `file/botTOKEN/…` URLs into text (token leak).

### Brand custom emoji

For well-known brands in digests:

```html
<tg-emoji emoji-id="…">fallback</tg-emoji> BrandName
```

- Only from an explicit map (never guess IDs).
- The brand name after the icon is mandatory.
- Don't touch code fences, URLs, emails, already inserted `<tg-emoji>`.

Practical cron examples (software-update, GLM): skill
`telegram-cron-image-conventions`.

## Procedure

1. Mark up content: tables, checklists, `<details>`, formulas — format them
   with native GFM/HTML; they raise the rich path themselves. Completion: every
   construct is syntactically closed (table with separator, `</details>`).
2. Mobile format: short paragraphs, `- ` lists instead of walls of text,
   `key: value` for small structured data. Completion: paragraphs ≤ 4 lines.
3. Check the size: ≤ 30,000 characters — as a message; more — summary +
   `MEDIA:` file. Completion: the text won't exceed the limit after adding
   captions and tables.
4. Commands and paths — in a code fence or inline code; don't put data meant
   for copying inside rich tables (hard to copy from the client).
5. Images: no meaning → no media; section banner → placehold; diagram/
   comparison → generate (Gemini → Grok) → jpg.wtf (fallback pixhost) →
   `![](https://…)`. Screenshot with PII/secrets/internal systems →
   `MEDIA:` only.
   Local file → `MEDIA:/abs`, not inside `![]()`. Completion: the reply has
   no FS paths inside a markdown image and no `file/bot` URLs.

## Pitfalls

1. **Don't escape anything yourself.** `\.` and `\*` are for hand-written
   MarkdownV2; the gateway converts on its own, and on the rich path the
   slashes end up in the text.
2. **Only 4 constructs trigger rich.** A regular reply with lists and bold
   goes via MarkdownV2: headings won't render, a table gets flattened. Want a
   native render — add a rich construct.
3. **Link previews can't be disabled on the rich path** — `disable_link_previews`
   only applies to MarkdownV2.
4. **`$$math$$` inside `<details>`** crashes Telegram Desktop; the adapter
   moves such a message off the rich path itself. Don't combine them.
5. **CJK text** is garbled on the rich path (Telegram Desktop/macOS bug);
   the adapter filters it — the message goes via plain MarkdownV2.
6. **Code language**: ` ```python ` loses the language on the MDv2 path; rich
   keeps highlighting.
7. **Capability latch**: if `sendRichMessage` is unavailable (old PTB), the
   adapter disables rich for the rest of the session — don't expect a rich
   render again.
8. **`hermes send` does not use rich** — only MarkdownV2/HTML with the 4,096
   limit. Exception: live no_agent cron scripts that call `sendRichMessage`
   directly (software-update, GLM, dd-host) — they bypass the gateway and
   `hermes send`.
9. **Config is read at gateway start**: changing `rich_messages`/
   `rich_drafts` requires restarting the gateway externally (restart from a
   session is blocked).

## Verification

- Send yourself a reply with a GFM table and `- [x]` — the table must render
  natively, not as a code block; the checkbox must be interactive.
- In `~/.hermes/logs/gateway.log`: `grep -iE "rich|sendRich|rejected" | tail`
  — there must be no `sendRichMessage rejected` / `unsupported`.
- A message > 4,096 characters without rich constructs arrived in parts → add
  a rich construct or a file.
- A placehold banner and `![](https://…)` arrive inline in the same rich
  bubble; `MEDIA:/abs` goes as a separate native photo.

## References

- [`references/adapter-internals.md`](references/adapter-internals.md) — gateway adapter internals (load only when debugging delivery).

Russian version: [`references/README.ru.md`](references/README.ru.md).
