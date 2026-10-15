# AmneziaWG: протокол и параметры (AWG 1.0 → 3.1)

Сверено 2026-10-15 по коду и релизам:

| Источник | Версия / коммит |
|---|---|
| `amnezia-vpn/amneziawg-go` (README, `device/*.go`) | `v3.1.20260828` (b5928ef) |
| `amnezia-vpn/amneziawg-linux-kernel-module` (`src/netlink.c`, `junk.c`, `uapi/wireguard.h`) | `v3.1.20260906` (4569c4c) |
| `amnezia-vpn/amneziawg-tools` (`src/config.c`, `wg-quick/linux.bash`) | `v3.1.20260812` (ee0f0a9) |
| `amnezia-vpn/amnezia-client` (`client/core/utils/constants/protocolConstants.h`, release notes) | `5.0.3.0` (2026-09-18) |

Статусы: **[код]** — подтверждено исходниками; **[README]** — официальная документация;
**[вывод]** — следует из размеров сообщений WireGuard, в коде не проверяется.

## Версии протокола и минимальные версии

| AWG | Что добавила | Сервер (go / kmod / tools) | Клиенты (минимум) |
|---|---|---|---|
| 1.0 | `Jc, Jmin, Jmax, S1, S2, H1–H4` | любые | любые AmneziaWG |
| 1.5 | `I1–I5` | — | Amnezia VPN 4.8.8.3; AmneziaWG Windows 2.0.0 |
| 2.0 | `S3, S4`; `H1–H4` диапазонами | 2.x | Amnezia VPN 4.8.12.7; AmneziaWG Android 2.0.0; Windows 2.0.0 (H > 2147483647 подсвечивались ошибкой до 2.0.2) |
| 3.0 | `HeaderProtectionKey`, `ContentPaddingAddition`, таймеры-диапазоны | 3.0.x | Amnezia VPN 5.0.0.2; AmneziaWG Android 3.0.1 (по версии встроенного awg-go) |
| 3.1 | `RandomTrailers`, `DisableCookies` | 3.1.x (go, kmod, tools) | Amnezia VPN 5.0.1.5; AmneziaWG Android v3.1.20260814; Windows 3.1.0 |

Клиентские версии — из release notes соответствующих репо (`amnezia-client`,
`amneziawg-android`, `amneziawg-windows-client`). Для iOS/macOS (`amneziawg-apple`)
релизов на GitHub нет — проверяй версию в App Store.

Неизвестный ключ: go — `invalid UAPI device key` **[код]**; итог — `awg setconf`/`awg-quick up` падает.
Выравнивай версию по самой старой стороне.

## Что обязано совпадать

| Параметр | Совпадать? | Основание |
|---|---|---|
| `H1–H4` | да | тип пакета определяется по заголовку **[код]** |
| `S1–S4` | да | приём проверяет `size == padding + MessageSize` **[код]** `device/receive.go` |
| `HeaderProtectionKey` | да | README: «server-side» **[README]** |
| `RandomTrailers` | да | приёмник принимает длину > ожидаемой только если `randomTrailers` включён у него **[код]** `receive.go:618` |
| `Jc/Jmin/Jmax`, `I1–I5` | нет | README: «no need to specify on both sides», рекомендуется на клиенте **[README]** |
| `ContentPaddingAddition` | нет (README советует на обеих) | **[README]** |
| Таймеры, `PersistentKeepalive` | нет, «client-side» | **[README]** |
| `DisableCookies` | нет, локальное поведение | **[код]** `receive.go:372` |

Пустой параметр трактуется как 0 **[README]**.

## Параметры

- `Jc` — число junk-пакетов перед каждым handshake; README: рекомендуется **4–12**. Тип `uint16` (tools/kmod), жёсткого предела 128 в коде нет **[код]**.
- `Jmin` ≤ `Jmax` **[README]**. `Jmax` ≥ системного MTU → фрагментация, заметная цензору **[README]**.
- `S1/S2/S3/S4` — паддинг init / response / cookie / transport **[README]**. В коде ограничения «S4 ≤ 32» нет **[код]** (kmod/tools — `uint16`); большой `S4` просто съедает MTU каждого пакета данных.
  Не допускай `S1 + 56 == S2` (init 148 Б, response 92 Б → одинаковая длина) **[вывод]**.
- `H1–H4` — `uint32`, число или диапазон `x-y` (2.0+) **[README]**. Диапазоны **не должны пересекаться**: go — `headers must not overlap` **[код]** `uapi.go`. Значения 1–4 = заголовки ванильного WireGuard, т.е. без обфускации заголовков **[вывод]** (это же «выключенные» дефолты в `amnezia-client`).
- `I1–I5` — пакеты перед handshake, порядок I1…I5, пустые пропускаются **[README]**. Теги:
  - `<b 0xHEX>`, `<r N>`, `<rc N>`, `<rd N>`, `<t>` — **[README]**, поддерживаются и go, и kmod **[код]**;
  - `<c>` — только kmod (`junk.c`) **[код]**;
  - `<d>`, `<ds>`, `<dz>` — только go (`device/obf.go`) **[код]**, в README не описаны — не используй в переносимых конфигах.
  Незнакомый тег = ошибка разбора всей цепочки (go: ошибки `obfBuilders` возвращаются из `newObfChain`) **[код]**.
- `HeaderProtectionKey` (3.0) — ключ из `awg genkey` **[README]**. Требует **S1–S4 ≥ 12** (nonce ChaCha20 = 12 байт), иначе go и kmod возвращают `EINVAL` **[код]** (`HeaderCipherNonceSize`, `HEADER_PROTECTION_NONCE_SIZE = 12`).
- `ContentPaddingAddition` (3.0) — `uint32` или диапазон, «client-side» **[README]**.
- Таймеры (3.0): `RekeyAfterTime`, `RekeyTimeout`, `RejectAfterTime`, `KeepaliveTimeout`, `MaxHandshakeAttempts`, `PersistentKeepalive` — число или диапазон **[README]**. Логично держать `RekeyAfterTime < RejectAfterTime` **[вывод]** (как у WireGuard: 120 / 180 с).
- `RandomTrailers` (3.1) — **[код]** go/kmod/tools (`random_trailers`). Каждый исходящий handshake/cookie/транспорт получает случайный хвост длиной `rand(0, udpWindow − size)`, где `udpWindow` стартует с `DefaultUdpWindow = 500` и растёт по наблюдаемым пакетам пира. В README не описан.
- `DisableCookies` (3.1) — **[код]**: под нагрузкой устройство не отправляет Cookie Reply (защита WireGuard от DoS отключается). В README не описан.

## Рекомендуемые дефолты (amnezia-client 5.0.3.0, `protocolConstants.h`)

| Параметр | Значение в приложении |
|---|---|
| Порт AWG | 55424/udp |
| MTU | 1280 (Android, iOS, macOS NE), 1376 (остальные) |
| `Jc / Jmin / Jmax` | 3 / 10 / 30 (UI: размер junk ≥ 12) |
| `S1–S4` | 12 (UI-пределы: S1, S2 ≤ 150; S3 ≤ 64) |
| `I1` | DNS-подобный пакет `<r 2><b 0x8580…>`; `I2–I5` пусто |
| `ContentPaddingAddition` | `10-100` |
| `RekeyAfterTime / RekeyTimeout / RejectAfterTime` | `100-120` / `3-7` / `150-180` |
| `KeepaliveTimeout / MaxHandshakeAttempts / PersistentKeepalive` | `5-15` / `15-20` / `25-35` |
| `RandomTrailers / DisableCookies` | `on` / `on` |
| `H1–H4` константы | 1, 2, 3, 4 (fallback; задавай свои непересекающиеся значения/диапазоны) |

`awg-quick` без `MTU` ставит MTU = MTU маршрута − 80 (обычно 1420) **[код]** `linux.bash`.
Отдельного «MTU 1280 для 3.1» в протоколе нет: 1280 — дефолт мобильных клиентов Amnezia; при хвостах пакеты длиннее, поэтому меньший MTU снижает риск фрагментации **[вывод]**.

## Шаблон (значения — пример, ключи — плейсхолдеры)

```ini
[Interface]
PrivateKey = <client-private>
Address = 10.8.1.2/32
DNS = 1.1.1.1
MTU = 1280
Jc = 5
Jmin = 40
Jmax = 70
S1 = 24
S2 = 37          # 24+56=80 ≠ 37
S3 = 18
S4 = 12
H1 = 100000000-100100000
H2 = 200000000-200100000
H3 = 300000000-300100000
H4 = 400000000-480000000
I1 = <r 2><b 0x858000010001000000000669636c6f756403636f6d0000010001c00c000100010000105a00044d583737>
# AWG 3.x (обе стороны 3.x):
HeaderProtectionKey = <awg genkey>
ContentPaddingAddition = 10-100
# AWG 3.1 (обе стороны 3.1):
RandomTrailers = on
DisableCookies = on

[Peer]
PublicKey = <server-public>
PresharedKey = <psk>
Endpoint = vpn.example.com:55424
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

`I1` — дефолт `amnezia-client` (DNS-ответ). Генераторы профилей мимикрии существуют
(например, architect.vai-rice.space), но их выход проверяй сам: см. ограничения тегов выше.

## Траблшутинг

1. `Invalid argument` при подъёме → ключ новее версии устройства; S1–S4 < 12 при `HeaderProtectionKey`; пересечение H; незнакомый тег I. **[код]**
2. Интерфейс есть, handshake нет → H1–H4/S1–S4/`HeaderProtectionKey`/`RandomTrailers` на обеих сторонах; затем UDP-порт, firewall, `Endpoint`.
3. `awg show` на kmod падает с `Message too long` → атрибуты устройства (включая `I1–I5`) уходят в одном netlink-сообщении, при переполнении `netlink.c` возвращает `-EMSGSIZE` **[код]**; точный порог не измерен — сократи цепочку.
4. Долгий старт → меньше `Jc`/`Jmax`.
5. Периодические обрывы на 3.x → проверь диапазоны таймеров.
