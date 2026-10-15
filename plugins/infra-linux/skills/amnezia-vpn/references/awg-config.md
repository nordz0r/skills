# AmneziaWG: оптимальная конфигурация (шаблоны и рецепты)

Параметры и их точная семантика — `awg-protocol.md`; официальное описание 3.1 — docs.amnezia.org/documentation/amnezia-wg (сверено 2026-10-15) (источники: amneziawg-go v3.1.20260828,
kmod v3.1.20260906, amneziawg-tools v3.1.20260812, amnezia-client 5.0.3.0; сверка 2026-10-15).
Рецепты ниже — **[рекомендация]**: собраны из этих фактов, не из официального гайда (его нет);
каждое числовое ограничение помечено источником.

## Порядок выбора

1. **Версия протокола** = минимум из того, что умеют сервер и *все* клиенты (таблица версий — `awg-protocol.md`).
   Нет уверенности в клиентах → AWG 2.0. Все клиенты свежие (Amnezia VPN ≥ 5.0.1.5, AmneziaWG ≥ 3.1) → 3.1.
2. **Shared-набор на сервер** (один на всех клиентов): S1–S4, H1–H4, при 3.x — HeaderProtectionKey, при 3.1 — RandomTrailers.
3. **Sender-набор на каждое устройство**: Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition — можно и полезно разнообразить.
4. **MTU** под сеть клиента.
5. Прогнать `config-checklist.md`.

## Генерация значений

- `S1–S4`: при HeaderProtectionKey все ≥ 12 **[код]**. С `RandomTrailers` официальная документация рекомендует **одинаковые S1 = S2 = S3 = S4** (меньше риск неверно определить тип пакета) **[docs.amnezia.org]**. Без трейлеров — случайные, но без `S2 = S1+56`, `S3 = S1+84`, `S3 = S2+28` **[вывод]**. Держи `S4` небольшим (12–32): он добавляется к каждому пакету данных.
- `H1–H4`: с HeaderProtectionKey официально рекомендовано **H1–H4 = 1/2/3/4** — механизм заголовков выключен, тип пакета скрывает Header Protection **[docs.amnezia.org; так же делает Amnezia]**. Без HeaderProtectionKey (1.x/2.0) — четыре непересекающихся значения/диапазона вне 1–4 **[код: overlap → ошибка]**, диапазоны шириной в десятки–сотни тысяч.
  Совместимость: если есть AmneziaWG Windows < 2.0.2 — все H ≤ 2147483647 **[release notes]**.
- `Jc/Jmin/Jmax`: Jc 4–12 **[README]**, Jmin ≤ Jmax < MTU пути **[README]**.
- `HeaderProtectionKey`: `awg genkey` **[README]**.
- Секреты генерируй на устройстве; в доки/чаты — плейсхолдеры.

## Рецепты по сценариям

| Сценарий | Версия | Ключевые настройки |
|---|---|---|
| **Сильный DPI** (блок по сигнатуре/статистике) | 3.1 (или 3.0) | HeaderProtectionKey, ContentPaddingAddition `10-100`, таймеры-диапазоны (дефолты Amnezia), RandomTrailers on, S1 = S2 = S3 = S4, H1–H4 = 1/2/3/4, I1 — мимикрия популярного UDP-протокола сети, Jc 4–8 |
| **Мобильные сети** | 2.0–3.1 | MTU 1280 (дефолт Amnezia на мобильных), Jc 4–6 (нижняя граница рекомендации README 4–12), Jmax ≤ 200, I1 только (без I2–I5), PersistentKeepalive 25 (`25-35` на 3.x), DisableCookies — off, если рвётся за CGNAT [❔ наблюдение] |
| **Роутер с модулем ядра** (OpenWrt, kmod) | по версии kmod-пакета | только теги `b, t, r, rc, rd` (+`<c>` можно, это kmod); короткая цепочка I1–I5 (иначе `-EMSGSIZE` при чтении) **[код]**; умеренный Jc |
| **Старые клиенты** | 1.5 или 2.0 | без ключей 3.x (иначе интерфейс не поднимется) **[код]**; H ≤ 2147483647 для Windows < 2.0.2; I1–I5 только если клиент ≥ 1.5 (Amnezia VPN 4.8.8.3) |
| **Максимальная совместимость** | 1.0 | Jc/Jmin/Jmax, S1/S2, H одиночные |

## MTU

- `awg-quick` без `MTU` = MTU маршрута − 80 (обычно 1420) **[код wg-quick/linux.bash]**.
- Amnezia: 1280 на Android/iOS/macOS, 1376 на десктопе **[protocolConstants.h]**.
- Симптом «пинг идёт, тяжёлые страницы висят» → снижай до 1280. С RandomTrailers пакеты длиннее — ниже MTU безопаснее **[вывод]**.
- Учитывай: S4 и ContentPaddingAddition съедают полезную нагрузку пакета.

## I1–I5: мимикрия

- Шлются перед каждым handshake в порядке I1…I5 **[README]**; получатель их отбрасывает — совпадать не нужно.
- I1 несёт «узнаваемый» заголовок протокола (`<b 0x…>`), I2–I5 — энтропия (`<r N>`, `<rc N>`, `<t>`).
- Выбирай протокол, обычный для сети: DNS (дефолт Amnezia — DNS-ответ), QUIC Initial там, где много HTTP/3, STUN/DTLS — где много видеозвонков. Эффективность профилей — **[❔ наблюдение]**, официальных рекомендаций нет.
- Размер каждого I-пакета < MTU (README: иначе фрагментация).
- Генераторы профилей (например, architect.vai-rice.space, `scripts/awg-gen.sh` в его репо) — черновик; проверяй по `config-checklist.md`.

## Шаблон сервера

```ini
[Interface]
Address = 10.8.1.1/24
ListenPort = 443              # пример скилла; дефолт Amnezia — 55424
PrivateKey = <server-private>
# Shared — 1:1 с клиентами:
S1 = 24
S2 = 24
S3 = 24
S4 = 24          # 3.1 + RandomTrailers: одинаковые S (docs)
H1 = 1
H2 = 2
H3 = 3
H4 = 4           # с HeaderProtectionKey (docs); для 2.0 — свои непересекающиеся диапазоны
# AWG 3.x:
HeaderProtectionKey = <awg genkey>
# AWG 3.1:
RandomTrailers = on
# Jc/Jmin/Jmax и I1–I5 — sender-only, на сервере не обязательны.

[Peer]
PublicKey = <client-public>
PresharedKey = <psk>
AllowedIPs = 10.8.1.2/32
```

## Шаблон клиента

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
S2 = 24
S3 = 24
S4 = 24          # 3.1 + RandomTrailers: одинаковые S (docs)
H1 = 1
H2 = 2
H3 = 3
H4 = 4           # с HeaderProtectionKey (docs); для 2.0 — свои непересекающиеся диапазоны
I1 = <r 2><b 0x858000010001000000000669636c6f756403636f6d0000010001c00c000100010000105a00044d583737>
HeaderProtectionKey = <тот же, что на сервере>
ContentPaddingAddition = 10-100
RandomTrailers = on
DisableCookies = on
# AWG 2.0: убрать HeaderProtectionKey, ContentPaddingAddition, RandomTrailers, DisableCookies;
# задать H1–H4 непересекающимися диапазонами (например 100000000-100100000 … 400000000-480000000) и разные S.

[Peer]
PublicKey = <server-public>
PresharedKey = <psk>
Endpoint = vpn.example.com:443
AllowedIPs = 0.0.0.0/0, ::/0     # split-tunnel — перечисли подсети
PersistentKeepalive = 25
```

`I1` — дефолт `amnezia-client` (DNS-ответ).
