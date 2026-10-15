# XHTTP, FinalMask, Hysteria 2

Сверено 2026-10-15 по `XTLS/Xray-core` v26.10.10 / main 0888beb:
`transport/internet/splithttp/dialer.go`, `infra/conf/transport_method.go`,
`infra/conf/transport_finalmask.go`, `infra/conf/transport_internet.go`.
Официальная страница `xtls.github.io/config/transports/xhttp` — заглушка «XHTTP: Beyond REALITY» со ссылкой на discussion #4113; поэтому источник — код и `XTLS/Xray-examples/VLESS-XHTTP-Reality`.

## XHTTP (`"network": "xhttp"`, алиас `splithttp`)

| mode | Суть |
|---|---|
| `packet-up` | uplink — отдельными POST |
| `stream-up` | uplink — одним долгим запросом |
| `stream-one` | один запрос в обе стороны; `downloadSettings` с ним **запрещён** |
| `auto` / пусто | клиент: `packet-up`; при REALITY — `stream-one`; при REALITY + `downloadSettings` — `stream-up` (`dialer.go`) |

Проверки ядра (иначе не стартует), `transport_method.go`:
- `mode` ∈ `auto|packet-up|stream-up|stream-one`;
- `headers` не может содержать `host` (используй отдельное поле `host`);
- `xPaddingBytes` нельзя отключить;
- `xPaddingPlacement` ∈ `queryInHeader` (дефолт) `|cookie|header|query`; `xPaddingMethod` ∈ `repeat-x` (дефолт) `|tokenish`;
- `uplinkDataPlacement` не-дефолтный и `uplinkHTTPMethod: GET` — только в `packet-up`;
- `sessionIDTable`/`sessionIDLength` — с коммита 2026-06-09 (#6258, v26.6.22); там же `session*` переименованы в `sessionID*`.

Прочие поля (v26.10.10): `path`, `host`, `xPaddingObfsMode`, `xPaddingKey`, `xPaddingHeader`,
`sessionIDPlacement`, `sessionIDKey`, `seqPlacement`, `seqKey`, `uplinkDataKey`, `uplinkChunkSize`,
`noGRPCHeader`, `noSSEHeader`, `scMaxEachPostBytes`, `scMinPostsIntervalMs`, `scMaxBufferedPosts`,
`scStreamUpServerSecs`, `serverMaxHeaderBytes`, `xmux`, `downloadSettings`, `extra`.
`path`/`host` и все placement/key-поля должны совпадать на клиенте и сервере.

Vision (`flow`) с XHTTP не задаётся: XTLS требует TLS/REALITY «directly» (`proxy/vless/*`: «XTLS only supports TLS and REALITY directly for now»).

## FinalMask (`streamSettings.finalmask`)

Обфускация под транспортом (аналог junk-пакетов AWG). Типы в v26.10.10:
TCP — `header-custom`, `fragment`, `sudoku`; UDP — `xmc`, `header-custom`, `mkcp-legacy`,
`noise`, `salamander`, `sudoku`, `xdns`, `xicmp`, `realm`, `udphop`; плюс `header-*`
(`dns`, `dtls`, `srtp`, `utp`, `wechat`, `wireguard`). Маска должна совпадать на обеих сторонах;
`xdns`/`xicmp`/`xmc`/`realm` требуют своих резолверов/адресов/хостов. В ссылках — параметр `fm`.

## Hysteria 2

`"network": "hysteria"` и outbound `hysteria` (`"version": 2` обязателен), `udphop`,
`congestion` ∈ `""|reno|bbr|brutal|force-brutal` — с v26.1.23.
