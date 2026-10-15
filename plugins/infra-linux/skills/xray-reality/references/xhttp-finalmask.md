# XHTTP и FinalMask

## XHTTP (`network: "xhttp"`, бывш. SplitHTTP)

Трафик заворачивается в обычные HTTP-запросы (H2/H3, через CDN тоже).

| mode | Суть | Когда |
|---|---|---|
| `packet-up` | каждая порция uplink — отдельный POST | CDN/посредники, не любящие долгие запросы |
| `stream-up` | uplink одним долгим POST (с gRPC-заголовком по умолчанию) | экономнее; с `downloadSettings` |
| `stream-one` | один запрос в обе стороны (с v24.11.30) | REALITY напрямую |
| `auto` | клиент: REALITY → `stream-one`; задан `downloadSettings` → `stream-up`; иначе `packet-up` | по умолчанию |

Правила:
- `path` (и `host`, если задан) совпадают на клиенте и сервере, иначе 404.
- `headers` не может содержать `host`.
- `xPaddingBytes` — диапазон, обе границы > 0 (отключить нельзя).
- Расширенные ручки (с v26.2.6 — «options for bypassing CDN detection», доработаны в v26.6.x): `xPaddingObfsMode`, `xPaddingPlacement`/`Key`/`Header`/`Method`, `sessionIDPlacement`/`Key`/`Length`/`Table` (до v26.6.22 — `sessionPlacement`…), `seqPlacement`/`Key`, `uplinkDataKey`, `noGRPCHeader`, `noSSEHeader`, `scMaxEachPostBytes`. Должны совпадать на обеих сторонах; некоторые размещения (cookie/header) и метод GET — только для `packet-up`. Проверяй имена по документации своей версии ядра, сверяй `xray run -test`.
- `downloadSettings` — отдельный транспорт под downlink (например, uplink через CDN, downlink напрямую через REALITY).
- Vision (`flow`) с XHTTP не используется.

## FinalMask (`finalmask` в streamSettings)

Обфускация «под» транспортом — ближайший аналог AWG-джанка. Маски (на v26.3.27+):
`noise` (UDP-мусор перед пакетами), `fragment` (резка ClientHello), `sudoku`,
`header-*`, `header-custom`, `mkcp-*`, `xdns`, `xicmp`, `salamander` (Hysteria) и др.
Маска должна совпадать на обеих сторонах. Маски `xdns/xicmp/xmc/realm/header-custom`
требуют собственной инфраструктуры/описания — генераторы их не выдумывают.
В share-ссылках — параметр `fm`.

## Hysteria 2

Транспорт/outbound Hysteria 2 (UDP/QUIC, port hopping `udphop`, `congestion`:
`reno|bbr|brutal|force-brutal`) — с v26.1.23. На старших ядрах ниже — `unknown transport protocol`.
