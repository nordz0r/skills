---
name: telegram-formatting
description: "Telegram Rich Markdown and Rich HTML formatting, tg-rich-messages TypeScript builder, sendRichMessage payloads and validation. Use when preparing Telegram gateway replies or implementing rich bot messages: GFM tables, task lists, details, advanced HTML tables and lists, buttons, references, media captions and credits, MarkdownV2 vs Rich Messages, MEDIA vs HTTPS images, placehold.co banners, jpg.wtf and pixhost fallback. Triggers: telegram, rich markdown, rich html, tg-rich-messages, sendRichMessage, MarkdownV2, MEDIA, inline photo, caption, checklist, телеграм, форматирование, таблица, баннер, картинка."
license: MIT
metadata:
  version: "3.4.0"
  author: "NorD (nordz0r), Hermes Agent"
  platforms: "linux,macos,windows"
  hermes:
    tags: [telegram, formatting, rich-messages, markdown, bot-api]
    related_skills: [telegram-bot-management, telegram-cron-image-conventions]
---

# Telegram Formatting Skill

Prepare Telegram content in the format supported by the sender. For a Hermes
gateway reply, write plain GitHub-Flavored Markdown and let the gateway choose
MarkdownV2 or Rich Messages. For an explicitly requested bot integration, use
Rich HTML or the `tg-rich-messages` TypeScript builder. These are different
delivery contracts: Rich HTML is not `sendMessage(parse_mode="HTML")`.

## When to Use

- You are preparing any reply that will go to Telegram via the gateway.
- You are choosing how to present content: table, checklist, code, spoiler, formula.
- The text is long or structured — deciding what goes as a message and what as a file.
- You need a section banner, an inline image or a `MEDIA:` file.
- You are building Rich HTML with advanced tables, lists, media or buttons.
- You need a validated `InputRichMessage` payload from `tg-rich-messages`.

Don't use for gateway administration, bot credentials or callback-handler
implementation. Do not call the Bot API just to deliver an ordinary agent
reply. Local-file delivery via `MEDIA:` is a gateway convention, not Telegram
markup. See [Rich HTML and builder reference](references/rich-html.md) for
explicit bot integrations and [the runnable example](examples/rich-message.mjs).

## InputRichMessage Contract

`InputRichMessage` requires exactly **one** of `markdown`, `html` or `blocks`.
Send it as `rich_message` to `sendRichMessage`, not as `text` with a parse mode.
Optional `is_rtl` selects right-to-left display; `skip_entity_detection`
disables automatic entity detection. Uploaded media references require the
separate `media` field. The builder emits `html`; it does not parse Markdown,
upload files or send requests.

## Hermes Gateway Profile

The routing rules below describe the locally installed Hermes v0.22.0 adapter
tree (install stamp commit `e06df9c2eae6901f4c88f464e0ae6e753c0428b8`,
`dirty: true`). The commit is only its baseline; local modifications may affect
behavior. This is not a claim about every Hermes release. Rich delivery is
opt-in and can still be declined by capability, content-shape, size or other
eligibility guards.

One agent text — two delivery paths; the gateway chooses:

| | MarkdownV2 (default) | Rich Messages |
|---|---|---|
| When | ordinary prose | recognized rich constructs, if eligible |
| Limit | 4,096 characters | 32,768 characters |
| Syntax | gateway converts Markdown | Rich Markdown |
| `#` headings, tables | may be flattened | rendered structurally |

In the local v0.22.0 adapter, rich triggers include:

- GFM pipe table;
- task list with `-` or `*`, checkbox state space, `x` or `X`;
- `<details>` / `<summary>` tags or block math `$$`;
- `PRLENS:` line, standalone HTTPS Markdown image, or `<tg-emoji emoji-id=…>`.

These constructs request rich rendering; they do not guarantee it. The adapter
also requires opt-in and API support, and applies safety/size guards. Ordinary
prose, bold, lists, code and headings alone do not trigger this path. Never add
meaningless markup just to force transport.

Text rules:

- Do not pre-escape a gateway reply as MarkdownV2; the gateway converts it.
  Ordinary Markdown escaping is still valid for literal Markdown punctuation.
  In direct HTML, escape text and attribute values or use the builder.
- Rich Markdown is GFM-compatible "where possible", so `**bold**` and
  `*italic*` are safe on both paths. The gateway normalizes single line breaks
  into hard line breaks.

## Rich Markdown Cheat Sheet

Common syntax of the `markdown` field in `InputRichMessage`
([official specification](https://core.telegram.org/bots/api/rich-messages.md#rich-markdown-style)):

````markdown
**bold**  __bold__  *italic*  _italic_  ~~strike~~  ==marked==  ||spoiler||
`inline code`   [text](https://…)   [email](mailto:u@x.ru)   [phone](tel:+7…)
[mention](tg://user?id=123)   $inline math$   ```lang …``` (code block)
![👍](tg://emoji?id=5368324170671202286)
![date/time](tg://time?unix=1647531900&format=wDT)
$$E=mc^2$$  or  ```math …```   ---  (divider)

# H1 … ###### H6
- / * / +  bulleted list;   1. 2. numbered
- [ ] open task;  - [x] done task
> quote (an empty `>` line between paragraphs separates them)
![](https://…/photo.jpg)  media block;  ![](url "caption")  with caption
| Col1 | Col2 |  GFM table with alignment `|:---|---:|`
Footnote[^id] … [^id]: explanation
````

Entity autodetection (no markup): URLs, e-mails, phone numbers, card numbers,
`#hashtag`, `$cashtag`, `/command`, `@username`.

Rich HTML extensions (usable in Rich Markdown where supported):

- `<u>`, `<ins>` — underline; `<sub>`, `<sup>` — sub/superscript
- `<a name="anchor"></a>` — anchor for internal links
- `<a href="#anchor">Jump</a>`; `<tg-reference name="note">Text</tg-reference>`
  with `<a href="#note">Note</a>` — anchors and referenced text
- `<aside>quote<cite>Author</cite></aside>` — pull quote
- `<blockquote expandable>Quote<cite>Author</cite></blockquote>` — expandable quote
- `<footer>Source note</footer>`, `<br>`, `<tg-math>` / `<tg-math-block>`
- `<ol start="3" type="a" reversed>` and per-item `value` / `type`;
  `<input type="checkbox" checked>` inside `<li>`
- `<table bordered striped compact>` with `<caption>`, cell `colspan` /
  `rowspan`, `align` and `valign` — beyond GFM tables
- `<figure>` + `<figcaption>` + `<cite>` — media captions and credit;
  `tg-spoiler` on visual media; `<tg-document src="https://…">` for documents
- `<details open><summary>Title</summary>…</details>` — collapsible block
- `<tg-map lat="41.9" long="12.5" zoom="14"/>` — map
- `<tg-collage>` / `<tg-slideshow>` — galleries from `![]()` or `<img>`
- `<tg-button type="url" url="…" style="success">Text</tg-button>` and
  `<tg-button-row align="center">` — inline buttons (types: `url`,
  `callback_data`, `web_app`, `login_url`, `switch_inline_query*`,
  `copy_text`, `disabled`; styles: `primary`, `success`, `danger`, `link`)
- `<tg-emoji emoji-id="…">👍</tg-emoji>`, `<tg-time unix="…" format="t">`
- `<tg-thinking>…</tg-thinking>` — only in streaming drafts (see below)

See [the full HTML/builder reference](references/rich-html.md) for supported
attributes, button prerequisites and examples. `tg://emoji` and `tg://time`
are inline entities, not HTTP media. Time formats match `r|w?[dD]?[tT]?`:
`r` is relative and cannot be combined; `wDT` is weekday, long date, long time.
Use real custom emoji IDs with emoji fallback text; never invent IDs.

Parser limits: Markdown inside block HTML tags is not parsed, except
`<details>`, `<tg-collage>`, `<tg-slideshow>`; use HTML children in other block
tags. Inline tags can contain Markdown. Table cells allow only inline
formatting. Media are separate blocks with HTTP(S) URLs, or explicit
`tg://photo|video|document|audio?id=…` references backed by `media`.

## Streaming & Drafts

In the documented Hermes profile, `streaming.enabled` + `rich_drafts: true`
allows rich draft streaming in private chats when the SDK/API supports it.
`<tg-thinking>` is draft-only: never put it in the final payload. Drafts are
temporary previews, not persisted messages; the sender must deliver a final
message. Group fallback and draft refresh timing depend on the adapter.

Do not claim a draft is the final delivered reply. The HTML builder's
`thinking()` only emits markup; it neither starts streaming nor finalizes it.

## Limits

| Limit | Value |
|---|---|
| Rich message text | 32,768 UTF-8 characters |
| Blocks (incl. nested, table rows, list items) | 500 |
| Formatting and block nesting | 16 levels |
| Media attachments | 50 |
| Table columns | 20 |
| Regular message (MarkdownV2) | 4,096 characters |

Text includes custom emoji fallback text and raw formula source; the limit is
characters, not UTF-8 bytes. For the builder, explicitly call `validate()`
before `toInputRichMessage()`: neither serialization method validates for you.
Its text count is approximate and its depth walk is not a complete check of
inline formatting. Passing validation is not proof of server acceptance or
identical rendering across clients.

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

1. Choose the contract: gateway GFM, or explicitly requested Rich HTML/builder.
   Use native constructs for the content; close tags, fences and table syntax.
   For a bot payload, use exactly one input field and validate before sending.
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

1. **Escaping depends on the contract.** Do not pre-escape gateway GFM as
   MarkdownV2. Direct Rich HTML needs escaped data; builder strings are escaped
   automatically. `unsafeRawInline()` is only for trusted HTML, never user data.
2. **Rich syntax does not guarantee rich transport.** The local Hermes trigger
   set is listed above; opt-in, SDK capability, content guards and send mode
   still decide eligibility.
3. **Link previews, CJK and math guards are adapter-specific.** Local Hermes
   v0.22.0 passes `disable_link_previews` to rich sends. CJK normally falls back
   to MarkdownV2; `allow_cjk_rich_messages` opts in. Details/math crash guards
   apply to matching shapes; the Rich spec itself supports math inside details.
4. **Code language:** use a language fence in Markdown or nested
   `<pre><code class="language-python">…</code></pre>` in HTML. Standalone
   `<code>` cannot declare a language; fallback conversion may lose it.
5. **Capability latch:** in the snapshot, missing-method/404 capability errors
   disable rich for the adapter lifetime. A transient or payload error is not
   the same as a permanent capability failure.
6. **HTML modes differ:** Rich HTML tables, media and details are not supported
   by regular `sendMessage(parse_mode="HTML")`. Callback buttons also require
   a functioning bot handler; markup alone does not implement an action.
7. **`hermes send` is separate:** the local standalone CLI sender uses regular
   Telegram send, not the gateway's rich-send path. Do not transfer one path's
   limits or formatting behavior to the other.
8. **Drafts depend on API/profile:** both rich messages and rich-draft settings
   are opt-in in the local adapter. A draft is temporary; the caller must send
   the final message. Streaming transport/group behavior is adapter-specific.
9. Gateway configuration changes may require an external restart; check the
   installed adapter rather than assuming a session can reload it.

## Verification

- For HTML generation, copy [the example](examples/rich-message.mjs) into a
  consuming project with the pinned package installed; run it there. Expect JSON
  containing `html`, with no token, request or automatic send. The builder's
  `validate()` is not a complete server/client validation.
- For end-to-end delivery, send an authorized message with a meaningful GFM
  table and task list. Check native table/checkbox rendering in the target
  client; do not assume checkboxes implement a mutable task workflow.
- Inspect the gateway log for rich rejection, capability fallback and ordinary
  splitting. A long message delivered in parts is not proof of rich delivery.
- Check the image is inline in the same rich bubble; `MEDIA:/abs` is a separate
  attachment. Payload generation alone does not verify client rendering.

## References

- [`references/adapter-internals.md`](references/adapter-internals.md) — archived Hermes v0.18.2 adapter snapshot, not current truth for v0.22.0.
- [Rich HTML and tg-rich-messages](references/rich-html.md) — advanced syntax,
  safe builder usage and runnable example; based on upstream v0.4.0.
- [Telegram Rich Messages](https://core.telegram.org/bots/api/rich-messages.md)
  and [InputRichMessage](https://core.telegram.org/bots/api/types/inputrichmessage.md)
  — authoritative formatting and input contract.
- [tg-rich-messages v0.4.0 source](https://github.com/vdistortion/tg-rich-messages/tree/b0715933db1658d70808ce42b022761d12e41128)
  — reviewed baseline; HTML builder, not gateway routing logic.


Russian version: [`references/README.ru.md`](references/README.ru.md).
