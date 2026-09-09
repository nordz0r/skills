# Rich Message Adapter Internals (Hermes v0.18.2)

Reference from the live adapter at `plugins/platforms/telegram/adapter.py` (9110 lines).

## Config Reading

```python
# Line 594 — read at adapter init, NOT re-read mid-session
self._rich_messages_enabled: bool = self._coerce_bool_extra("rich_messages", False)
self._rich_drafts_enabled: bool = self._coerce_bool_extra("rich_drafts", False)
```

`_coerce_bool_extra` (line 1339) reads from `self.config.extra` — which comes from `gateway.platforms.telegram.extra` in config.yaml. A top-level `telegram.extra` key is silently dropped.

## Eligibility Gate: `_needs_rich_rendering()` (line 1460)

Rich delivery is NOT used for every message. Only these constructs trigger it:

1. **Pipe tables** — any line matching `_TABLE_SEPARATOR_RE` (GFM `|---|---|` pattern)
2. **Task lists** — `- [ ]` or `- [x]` at line start
3. **`<details>` blocks** — `<details>`, `</details>`, `<summary>`, `</summary>` tags
4. **Block math** — `$$` delimiters

Ordinary prose (bold, italic, lists, code fences, links) stays on MarkdownV2.

## Full Eligibility Chain: `_rich_eligible()` (line 1486)

All must pass:
1. `_rich_delivery_enabled()` — `_rich_messages_enabled` is True
2. `_rich_send_disabled` is False (not latched off)
3. Content is non-empty
4. `_needs_rich_rendering(content)` — one of the 4 triggers above
5. NOT `_has_telegram_desktop_details_math_crash_shape` — math inside `<details>` crashes TDesktop 6.9.1
6. NOT `_has_telegram_desktop_cjk_rich_garble_shape` — CJK text garbles on rich drafts
7. `_content_fits_rich_limits(content)` — ≤ 32,768 UTF-8 chars
8. `_bot_supports_rich()` — `do_api_request` is an async coroutine function

## Capability Latch (line 1699, 1800)

If `sendRichMessage` fails with a **capability error** (EndpointNotFound, 404, "method not found"), `_rich_send_disabled` is set to True for the adapter's lifetime. Per-message BadRequest errors do NOT latch — the next message may succeed.

## PTB Version Check

```python
# Line 1402
def _bot_supports_rich(self) -> bool:
    return inspect.iscoroutinefunction(getattr(self._bot, "do_api_request", None))
```

PTB 22.6 passes this check (`do_api_request` is a coroutine function). Older versions without the method fail and rich is never attempted.

## Gateway Restart Blocker

The gateway process blocks `hermes gateway restart` and `systemctl --user restart hermes-gateway` from within its own process tree — SIGTERM would kill the calling process. The user must restart from a separate terminal.

## Rich Message Payload (line 1549)

```python
def _rich_message_payload(self, content, *, skip_entity_detection=False):
    return {"markdown": _rich_normalize_linebreaks(content)}
```

Uses RAW markdown (not MarkdownV2-converted). Single newlines are normalized to hard breaks. The `markdown` field maps to `InputRichMessage.markdown` in the Bot API.

## Streaming Overflow Limit (line 1530)

When rich is available, `streaming_overflow_limit` returns 32,768 (vs the default 4,096 MarkdownV2 limit), so rich-eligible streams aren't fragmented at the old limit.
