# Чек-лист проверки конфигов (AWG .conf, vpn://, vless://)

Основа — правила валидатора генератора Architect (`Vadim-Khristenko/Any-Tech-ARCHITECT`
@ 0b9d3b7, 2026-10-08: `src/engines/awg/rules.ts`, `src/engines/keys/validate.ts`,
`src/engines/xray/validate.ts`, `src/engines/xray/parse.ts`), каждое правило сверено
с первоисточниками (версии — `awg-protocol.md`, `versions-compat.md`).
Статусы: **E** — устройство/ядро отвергнет (ошибка), **W** — работает, но плохо/заметно,
✅ подтверждено кодом upstream, ✏️ исправлено относительно Architect, ❔ правило Architect без подтверждения.

## AWG `.conf`

Структура:
- [E ✅] есть `[Interface]` с `PrivateKey`; у каждого `[Peer]` — `PublicKey`; ключи = 32 байта base64 (44 символа).
- [W] у клиента нет `Endpoint host:port` — подключаться некуда.
- [W] нет ни одного `Jc/S/H/I` — это обычный WireGuard, обфускации нет.

Версия:
- [E ✅] ключи новее устройства (3.0-ключи на 2.x, `RandomTrailers`/`DisableCookies` на 3.0) → `invalid UAPI device key` / `Line unrecognized`.
- [E ✅] H как диапазон `x-y` на 1.x-устройстве не разбирается.

Junk:
- [W ✅] `Jmin > Jmax` — README требует `Jmin ≤ Jmax`. ✏️ Architect требует строго `<`.
- [W ✅] `Jmax ≥ MTU` → фрагментация (README).
- [W] `Jc` большой (Architect: ≥ 64) — медленный старт. ❔ предел 128 в Architect — в коде go/kmod `uint16`, жёсткого 128 нет.

Паддинг:
- [E ✅] `HeaderProtectionKey` задан и любой `S1–S4 < 12` → `Invalid argument` (go `uapi.go`, kmod `netlink.c`).
- [W] одинаковая длина двух типов: `S2 = S1+56`, `S3 = S1+84`, `S3 = S2+28` (вывод из 148/92/64).
- [W] `S4 = 0` — транспорт не паддится.
- ✏️ «S4 ≤ 32» и «S1 ≤ 1132 / S2 ≤ 1188» из Architect — в upstream таких проверок нет; ориентир — чтобы пакет влезал в MTU пути.

Заголовки:
- [E ✅] H1–H4 пересекаются → `headers must not overlap`.
- [W] H в 1–4 при **пустом** `HeaderProtectionKey` = типы ванильного WG, заголовки не скрыты. С заданным HPK не предупреждать: H 1/2/3/4 — **рекомендация** docs.amnezia.org (2026-10-15).
- [W ✅] при `RandomTrailers` широкие H1–H3 дают ложную классификацию транспортных пакетов (≈ ΣW/2³²; `receive.go`) — держи узкими или (с HPK) ставь 1/2/3/4; с `RandomTrailers` docs рекомендуют S1 = S2 = S3 = S4.
- [W ❔] клиент-специфичные потолки (Windows < 2.0.2 — H ≤ 2147483647 ✅ release notes; wg-easy — ❔).

CPS `I1–I5`:
- [E ✅] синтаксис: последовательность тегов `<b 0x…>`, `<t>`, `<r N>`, `<rc N>`, `<rd N>` (+`<c>` только kmod, `<d>/<ds>/<dz>` только go); незнакомый тег ломает цепочку.
- [W ✅] длинная цепочка на kmod → `-EMSGSIZE` при чтении (`awg show`). ❔ бюджет 3200 байт — оценка Architect.

AWG 3.x:
- [E] `HeaderProtectionKey` — 32 байта base64 (`awg genkey`).
- [W] `ContentPaddingAddition = 0` — добавки нет; формат — число или `мин-макс`.
- [W] таймеры: формат число/диапазон, `мин ≤ макс`; `RekeyAfterTime < RejectAfterTime`; `RejectAfterTime > KeepaliveTimeout + RekeyTimeout`; `MaxHandshakeAttempts ≥ 1` (вывод из логики таймеров WG; ❔ точные пороги Architect).
- [E ✅] `RandomTrailers` должен совпадать на обеих сторонах.

## Ключ `vpn://` (Amnezia)

- [E ✅] base64url → `qCompress` (4 байта длины + zlib) → JSON; битая строка не распакуется.
- [W] нет `containers[]` / пустой контейнер / `defaultContainer` указывает на несуществующий.
- [W] дубль контейнера — Architect: клиент возьмёт первый (❔ не сверено в amnezia-client).
- [W] контейнер назван одним протоколом, а поля другого; `last_config` не JSON; поле в контейнере противоречит копии в `last_config`.
- [E ✅] в контейнере AWG задан `HeaderProtectionKey` и `S < 12`.
- Подписочный ключ (сервисный) туннеля не содержит — править нечего.

## Ссылка `vless://`

- [E] начинается с `vless://`, есть `UUID@host:port`, порт 1–65535; UUID — пароль (другой формат ядро захеширует).
- [E] `security` ∈ `none|tls|reality`; при `reality` обязателен `pbk`; `type` — известный транспорт.
- [W] при `reality` нет `sni` или `fp`; `pbk` без `reality`; `flow` при `security=none`.
- [E ✅] `flow` только `xtls-rprx-vision` (`-udp443` — клиентский суффикс).
- [W] неизвестный параметр — клиент проигнорирует (стандарт — discussion #716).

## Xray `config.json`

Ошибки ядра и их причины — `troubleshooting.md` (тексты из кода v26.10.10).
Дополнительно из Architect, сверено: `xver` ∈ 0/1/2 ✅; `shortIds` hex чётной длины ≤ 16 ✅;
`spiderX` начинается с `/` ✅; `mldsa65Seed` 32 байта и ≠ `privateKey` ✅; `mldsa65Verify` из `xray mldsa65`;
путь XHTTP начинается с `/` (❔ проверка Architect).
