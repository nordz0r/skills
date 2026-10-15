# AmneziaWG: протокол и параметры обфускации (AWG 1.0 → 3.1)

Справочник по полям `[Interface]` / `[Peer]` конфига `awg` / `awg-quick`.
Первичный источник — README и исходники `amnezia-vpn/amneziawg-go`
(теги `v3.1.*` на 2026-10) и `amnezia-vpn/amneziawg-linux-kernel-module`.
Пометка «по исходникам» = в официальном README поля нет, поведение взято из кода/вторичных разборов.

## Версии протокола

| Версия | Что добавила | Совместимость |
|---|---|---|
| 1.0 | `Jc/Jmin/Jmax`, `S1/S2`, фиксированные `H1–H4` | любые AWG-клиенты |
| 1.5 | `I1–I5` (custom signature packets, CPS) | клиенты 2024+ |
| 2.0 | `S3`, `S4`; `H1–H4` как диапазоны `x-y` | amneziawg-go/kmod 2.x+ |
| 3.0 | `HeaderProtectionKey`, `ContentPaddingAddition`, таймеры-диапазоны | amneziawg-go/kmod 3.0+ |
| 3.1 | `RandomTrailers`, `DisableCookies` (по исходникам) | только 3.1 на обеих сторонах |

Неизвестный устройству ключ → `awg setconf: Invalid argument`, интерфейс не поднимается.
Версию выравнивай по самой старой стороне (обычно — роутер/сервер).

## Что обязано совпадать

| Параметр | Scope | Совпадать? |
|---|---|---|
| `H1–H4` | shared | **да**, иначе пакеты молча отбрасываются |
| `S1–S4` | shared | **да** |
| `HeaderProtectionKey` | shared | **да** |
| `RandomTrailers` (3.1) | shared | **да** — приёмник без него режет удлинённые handshake |
| `Jc/Jmin/Jmax` | sender | нет (обычно только на клиенте) |
| `I1–I5` | sender | нет (рекомендация upstream — только клиент) |
| `ContentPaddingAddition` | sender | нет (upstream: желательно на обеих) |
| Таймеры 3.0, `DisableCookies` | local | нет |

Пустой параметр = 0 (README).

## Параметры

- `Jc` — сколько junk-пакетов перед каждым handshake. Upstream: **4–12**. Ядро допускает 1–128 (на go-клиентах генераторы держат ≤10). Большие значения замедляют старт, на мобильных сетях заметно.
- `Jmin` ≤ `Jmax` — размер junk-пакетов. `Jmax` < MTU пути, иначе фрагментация (заметна для DPI). Безопасно `Jmax` ≤ 1280.
- `S1` (init, база 148 Б), `S2` (response, база 92 Б), `S3` (cookie, 64 Б), `S4` (transport). Не допускай `S1 + 56 == S2` — init и response снова одинаковой длины. `S4` ≤ 32 по протоколу. Малые `S4` экономят MTU.
- `H1–H4` — uint32 тип сообщения (init/response/cookie/transport). Не используй 1–4 (это значения ванильного WireGuard → по сути без обфускации заголовков). Диапазоны (2.0+) **не должны пересекаться**. Старые Windows-клиенты < 2.0.2 и wg-easy принимают только ≤ 2147483647 — держи значения ниже, если такие клиенты есть.
- `I1–I5` — пакеты-маскировка перед handshake. Теги (README): `<b 0xHEX>` статические байты, `<r N>` случайные байты, `<rc N>` случайные буквы, `<rd N>` случайные цифры, `<t>` 4-байтовый unix-time. `<c>` (счётчик) есть только в модуле ядра; `<d>/<ds>/<dz>` — только в amneziawg-go и в 3.0.x фактически не используются. **Незнакомый тег отвергает весь пакет** → в общих конфигах используй только `b, t, r, rc, rd`.
  Ограничение модуля ядра: вся цепочка I1–I5 уходит одним netlink-сообщением; длинные цепочки (>~3.2 КБ суммарно) дают `awg show: Message too long`.
- `HeaderProtectionKey` (3.0) — ключ ChaCha20 для заголовков, генерируется `awg genkey`. Требует **все S1–S4 ≥ 12** (nonce берётся из паддинга), иначе `Invalid argument`. В Amnezia VPN ключ управляется приложением (галочка в настройках протокола) и в экспортируемый конфиг может не попадать.
- `ContentPaddingAddition` (3.0) — `uint32` или диапазон, случайный паддинг транспорта вместо выравнивания по 16 Б.
- Таймеры (3.0): `RekeyAfterTime`, `RekeyTimeout`, `RejectAfterTime`, `KeepaliveTimeout`, `MaxHandshakeAttempts`, а также `PersistentKeepalive` в `[Peer]` — число или диапазон. Держи `RekeyAfterTime < RejectAfterTime` и `RejectAfterTime > KeepaliveTimeout + RekeyTimeout`, иначе периодические обрывы.
- `RandomTrailers` / `DisableCookies` (3.1, по исходникам): хвосты удлиняют пакеты → разумно MTU 1280; при хвостах широкие H1–H3 ведут к потерям транспортных пакетов — держи их узкими. `DisableCookies` может рвать keepalive за NAT под нагрузкой.

## MTU

1420 — дефолт WireGuard; 1280 — если «пинг идёт, тяжёлые страницы висят» (PMTU-проблемы, мобильные/PPPoE), и для 3.1 с хвостами.

## Шаблон (значения — пример, сгенерируй свои; ключи — плейсхолдеры)

```ini
[Interface]
PrivateKey = <client-private>
Address = 10.8.1.2/32
DNS = 1.1.1.1
MTU = 1280
Jc = 5
Jmin = 50
Jmax = 1000
S1 = 68
S2 = 149        # 68+56=124 ≠ 149
S3 = 32
S4 = 16
H1 = 1023476589-1023496589
H2 = 1734522114-1734542114
H3 = 2016884455-2016904455
H4 = 2122091873-2142091873
# AWG 1.5+ (только client-side, теги b/t/r/rc/rd):
I1 = <b 0xc0000000010800><r 64><t>

[Peer]
PublicKey = <server-public>
PresharedKey = <psk>
Endpoint = vpn.example.com:443
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

`I1` выше — синтетический пример; реальные профили мимикрии (QUIC/DNS/SIP/STUN) собирай генератором или из захвата трафика.

## Траблшутинг (быстро)

1. `Invalid argument` при `awg setconf`/`awg-quick up` → ключи новее версии устройства; S<12 при HeaderProtectionKey; пересечение H.
2. Интерфейс есть, handshake нет → сверь H1–H4/S1–S4/HPK/RandomTrailers на обеих сторонах; затем порт UDP, firewall, `Endpoint`.
3. `Message too long` в `awg show` (kmod) → укороти I1–I5.
4. Долгое подключение → уменьши `Jc` до 2–4, `Jmax`.
5. Работало и перестало → сначала таймеры 3.0, затем смена профиля I1/параметров (сигнатура могла попасть в блок-лист).
