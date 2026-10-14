# Telegram Rich Messages: HTML mode

`tg-rich-messages` builds Telegram Rich Messages in **HTML mode**. This is distinct from this skill's gateway-delivery guidance: ordinary gateway sends use the gateway's Markdown formatting rules; do not treat this builder's HTML output as Markdown or send it through a Markdown parser. For Bot API `sendRichMessage`, pass the builder's payload as `rich_message` (the object contains `html`, not `text` or `markdown`). The builder does not send requests.

Use Node.js `^22.0.0 || >=24.0.0`. Install explicitly in the consuming project with `npm install tg-rich-messages@0.4.0`; the package is not globally auto-installed by this skill.

## Builder coverage

The package builds escaped HTML with `doc(...).toHTML()` or an
`InputRichMessage` with `doc(...).toInputRichMessage(...)`. `fmtRich` is a
tagged-template alternative: inline runs are grouped into paragraphs,
whitespace/newlines collapse within a paragraph, and embedded blocks/documents
are accepted. Serialization does not automatically validate; call `validate()`
first.

- Inline: bold, italic, underline, strike, spoiler, code, marked, subscript, superscript, `<br>`, LaTeX math; links, e-mail, phone, user mentions, anchors and anchor links, references and reference links, custom emoji, and formatted time.
- Blocks: paragraphs; headings h1–h6; preformatted code (optional language); footer, divider, block math; standalone anchor; pullquote; blockquote with optional credit and expandable mode; details with optional initially-open state; map with optional caption/credit; button rows with alignment; and document/media blocks.
- Lists: unordered or ordered; ordered-list `start`, `type` (`1`, `a`, `A`, `i`, `I`), and `reversed`; per-item `value` and `type`; checkbox and checked state.
- Tables: bordered, striped, compact, caption; cell content, header cells, `colspan`, `rowspan`, horizontal `align` (`left`, `center`, `right`) and vertical `valign` (`top`, `middle`, `bottom`). Telegram permits at most **20 columns**; cells contain inline content only.
- Media: photo, video, animation, audio, voice note, document, collage and slideshow. Media options provide caption and credit; individual photo/video/animation options support spoilers; gallery items accept photo/video type and per-item spoiler. Captions render in `<figcaption>` and credits in `<cite>`. Animation renders as video (use a suitable GIF/MP4 URL); voice renders as audio (typically OGG). Media URLs must be HTTP(S) for Telegram media blocks.

Buttons are inline `<tg-button>` nodes or grouped in `<tg-button-row align="left|center|right">`. Supported types: `url` (requires `url`), `callback_data` (requires `data`), `web_app` (requires `url`, available in private chats only), `login_url` (requires `url`; domain must be configured via @BotFather; optional `forwardText` and `requestWriteAccess`), `switch_inline_query`, `switch_inline_query_current_chat`, and `switch_inline_query_chosen_chat` (optional `query`; chosen-chat accepts `allowUserChats`, `allowBotChats`, `allowGroupChats`, `allowChannelChats` flags), `copy_text` (requires `text`), and `disabled`. Optional styles are `danger`, `success`, `primary`, `link`. The builder serializes supplied attributes but does not enforce type-specific requirements or contextual constraints; ensure the required fields and Telegram availability rules yourself.

The builder also exposes `<tg-thinking>` via `thinking()`, but Telegram documents it for `sendRichMessageDraft`, not regular `sendRichMessage`.

## Safety and validation

Normal builder text and attribute values are escaped. `unsafeRawInline(input)` is the exception: it inserts bytes as HTML without escaping; only use constant/trusted HTML. It is not a Markdown parser or sanitizer. Validate any externally supplied URLs, identifiers, labels, and other semantic values for your application before building. Escaping prevents HTML injection in generated markup; it does not establish that a URL, button action, or ID is safe or authorized.

Call `message.validate()` before serialization. The upstream validator checks approximate text length (32,768 Unicode code points; it heuristically strips markup/entities), media attachments (50), blocks (500 including nested/list/table children), and nesting depth (16). Telegram also documents a 20-column table limit. Validation is not comprehensive HTML/API/business-rule validation: text counting is approximate, and its internal depth walk is blind to inline-node nesting, so a deeply nested chain of inline builders may evade that depth check. Do not rely on it as complete hostile-input protection. `toInputRichMessage({ isRtl, skipEntityDetection })` produces an `InputRichMessage`: it sets the `html` field plus optional `is_rtl` and `skip_entity_detection`. `isRtl` controls right-to-left display; `skipEntityDetection` controls Telegram's automatic entity detection.

## Runnable example

Copy the example into a consuming project that has installed the package, then
run it there so Node.js resolves that project's `node_modules`:

```sh
npm install tg-rich-messages@0.4.0
node examples/rich-message.mjs
```

The example writes only the JSON `InputRichMessage` payload to stdout. It
performs no network request and includes no token or chat ID.

## Sources (pinned)

- [`tg-rich-messages` v0.4.0 README](https://github.com/vdistortion/tg-rich-messages/blob/b0715933db1658d70808ce42b022761d12e41128/README.md)
- [Builder source: blocks.ts](https://github.com/vdistortion/tg-rich-messages/blob/b0715933db1658d70808ce42b022761d12e41128/src/blocks.ts)
- [Builder source: inline.ts](https://github.com/vdistortion/tg-rich-messages/blob/b0715933db1658d70808ce42b022761d12e41128/src/inline.ts)
- [Builder source: media.ts](https://github.com/vdistortion/tg-rich-messages/blob/b0715933db1658d70808ce42b022761d12e41128/src/media.ts)
- [Builder source: document.ts](https://github.com/vdistortion/tg-rich-messages/blob/b0715933db1658d70808ce42b022761d12e41128/src/document.ts)
- [Official Telegram Rich Messages specification](https://core.telegram.org/bots/api/rich-messages.html)
