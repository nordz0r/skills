# FAQ по конфигурации: AmneziaWG, Xray, ключи Amnezia

Перенос FAQ генератора architect.vai-rice.space/faq (78 вопросов; сверено с исходником `Vadim-Khristenko/Any-Tech-ARCHITECT` `src/data/faq.ts` @ 0b9d3b7, 2026-10-08), переписано своими словами
и сверено с первоисточниками (версии — как в `awg-protocol.md` и `versions-compat.md`):
amneziawg-go v3.1.20260828, kmod v3.1.20260906, amneziawg-tools v3.1.20260812, amnezia-client 5.0.3.0,
Xray-core v26.10.10. Детали параметров не дублируются — ссылки на профильные файлы.

Статусы: ✅ подтверждено (источник) · ✏️ на сайте было неточно, здесь исправлено · ❔ не проверяемо по
официальным источникам (сторонний продукт / наблюдение) · 🛠 особенность генератора (только когда влияет на конфиг).

## Основы

1. **AmneziaWG vs WireGuard.** Форк WireGuard с той же криптографией Noise; меняется только внешний вид: заголовки, паддинг, junk/сигнатурные пакеты. Ванильный WG узнаётся по типу сообщения 1–4 и размерам 148/92 байта. ✅ README amneziawg-go, `device/constants.go`.
2. **Версии 1.0 / 1.5 / 2.0 / 3.0 / 3.1.** Таблица — `awg-protocol.md`. ✏️ Сайт писал, что в 1.5 I1–I5 «работают только на клиенте»; по README их можно задать на любой стороне, просто рекомендуют на клиенте.
3. **Что совпадает на сервере и клиенте.** H1–H4, S1–S4, HeaderProtectionKey, RandomTrailers — обязаны; Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition, таймеры, DisableCookies — нет. ✅ `receive.go` (`DeterminePacketTypeAndPadding`), README. Таблица — `awg-protocol.md`.
4. **Два движка (AWG / Xray) — что выбрать.** Ставь то, что уже стоит на сервере. Выбор протокола — `SKILL.md`, шаг 2.

## Ключи и форматы

5. **`vpn://`.** Не шифрование: `qCompress` (4 байта длины big-endian + zlib) JSON → base64url. Внутри `containers[]`, `defaultContainer`, `hostName`, `dns1/dns2`, `description`; контейнер на протокол. ✅ `amnezia-client` (`exportController.cpp`, `apiUtils.cpp`: `qCompress` + `Base64UrlEncoding`). Ключи сервиса (Amnezia Premium/API) — подписочные, туннель внутри не лежит. ❔ формат подписи не разбирался.
6. **`vless://`.** Стандарт — XTLS/Xray-core discussion #716: `vless://UUID@host:port?type=…&security=…&sni=…&pbk=…&sid=…&fp=…&flow=…#name`; IPv6 в `[]`; для ML-DSA — `pqv`, для FinalMask — `fm`. ✅ release notes v25.7.26, v26.3.27. Пример — `xray-config.md`.
7. **`vpn://` vs `vless://`.** `vless://` — одно подключение; `vpn://` — набор контейнеров Amnezia, и `xray`-контейнер внутри по сути несёт те же поля. ✅ (по структуре JSON).
8. **Что секретно.** `PrivateKey`, `PresharedKey`, `HeaderProtectionKey`; в `vless://` — UUID. `pbk`/`password` — публичный. base64/zlib ничего не скрывают. ✅
9. **Поменять обфускацию в готовом ключе без сервера.** Можно только sender-параметры (Jc/Jmin/Jmax, I1–I5, ContentPaddingAddition); H/S/HPK/ключи — только синхронно с сервером. ✅ по `receive.go`/README.

## Xray и REALITY

10. **REALITY vs AWG.** AWG меняет форму своих UDP-пакетов; REALITY проксирует настоящее TLS-рукопожатие донора и перехватывает соединение, только узнав клиента по ключу; активное зондирование видит донора. ✅ XTLS/REALITY README. От блокировки по IP не спасает ни то, ни другое.
11. **`target` и `serverNames` — один сайт.** Имена должны обслуживаться сертификатом target (тот же домен/SAN). ✅ docs `reality.md`. ✏️ поле теперь `target`, `dest` — алиас (v24.10.31).
12. **Выбор донора.** Официально: зарубежный, TLSv1.3 + H2, без редиректа; плюсы — близкий IP, шифрование после Server Hello, OCSP stapling. ✅ REALITY README. ✏️ «гигантов вроде microsoft.com не брать» — у сайта мнение; у ядра есть явное предупреждение для `apple/icloud/microsoft` и `.ru/.ir/.cn` — `xray-config.md`. География/популярность — ❔ эвристика.
13. **Ключевая пара, shortIds, spiderX.** x25519: приватный на сервере, публичный → `pbk`/`password`; `shortIds` — hex чётной длины ≤16, `""` разрешает пустой sid; `spiderX` — путь для краулера. ✅ `transport_security.go`, docs.
14. **`flow` / Vision / `-udp443`.** Единственное значение `xtls-rprx-vision`; суффикс `-udp443` — только клиент (разрешает UDP/443). Vision только поверх TLS/REALITY напрямую. ✅ `proxy/vless/*`, `infra/conf/vless.go`.
15. **XHTTP и режимы.** ✅ `dialer.go`, `transport_method.go`. Подробно — `xray-xhttp-finalmask.md`.
16. **`fp` (uTLS fingerprint).** Клиент имитирует ClientHello браузера (`chrome`, `firefox`, `safari`, `edge`, …); `unsafe`/`hellogolang` REALITY отклоняет. ✅ `transport_security.go`. «Отпечатки собраны измерениями» — 🛠.
17. **FinalMask.** ✅ `transport_finalmask.go`; список масок — `xray-xhttp-finalmask.md`.
18. **Почему параметры зависят от версии ядра.** Xray парсит JSON без `DisallowUnknownFields` — незнакомое поле молча игнорируется. ✅ (в `infra/conf` не используется). Таблица версий — `versions-compat.md`. ✏️ ряд версий на сайте был неверен (ML-DSA, VLESS Encryption, Hysteria, FinalMask, `minClientVer`) — исправлено там.

## Параметры AWG

19. **Jc/Jmin/Jmax.** ✏️ сайт: «Jc 3–7 обычно достаточно»; README: **4–12**; дефолт Amnezia — 3/10/30. `awg-protocol.md`.
20. **S1–S4 и совпадения длин.** ✅ размеры 148/92/64 (`constants.go`); запрещённые пары — `S2 = S1+56`, `S3 = S1+84`, `S3 = S2+28` (вывод). ✏️ «S4 ≤ 32 байт» (в исходнике сайта ссылка на `amneziawg-tools src/config.c`) — в tools v3.1.20260812, go и kmod такого предела нет; потолки S1 1132/S2 1188 в исходнике сайта обоснованы неверной арифметикой (65535−148 ≠ 1132) — не использовать.
21. **H1–H4, непересечение.** ✅ `headers must not overlap` (`uapi.go`).
22. **I1–I5 и теги.** ✅ README + `device/obf.go` + kmod `junk.c`. Таблица тегов — `awg-protocol.md`.
23. **`<d>/<ds>/<dz>`.** Есть только в amneziawg-go, в README не описаны. ❔ утверждение «в 3.0.1 вызываются с пустой нагрузкой, задел под AWG 4.0 (ветка feature/awg4)» не проверялось — не используй эти теги в переносимых конфигах.
24. **`<c>` — проблемный.** Только в модуле ядра; незнакомый тег ломает всю цепочку. ✅ `junk.c`, `obf.go`.
25. **Что дала 2.0.** S3/S4 и H-диапазоны (значение на каждый пакет). ✅ README.
26. **2.0 или 3.x.** 2.0 — самая совместимая; 3.x требует 3.x на обеих сторонах (мин. версии — `awg-protocol.md`). ✅ release notes клиентов. Остальное — оценка.
27. **Ширина H в 2.0/3.1.** ✅ по `receive.go`: при `RandomTrailers` длина больше не отсекает, и транспортный пакет сначала примеряется к H1/H2/H3 — доля ложных срабатываний ≈ (W1+W2+W3)/2³². Поэтому на 3.1 H1–H3 держи узкими; официально с HeaderProtectionKey рекомендуют H1–H4 = 1/2/3/4, а с RandomTrailers — одинаковые S1–S4 (docs.amnezia.org, 2026-10-15). Точные числа сайта (CPU, «до 100M», «~20k») — ❔.

## AWG 3.0 / 3.1

28. **HeaderProtectionKey.** ✅ README (32-байтный ключ, `awg genkey`, nonce из паддинга). Что handshake/cookie шифруются целиком, а у транспорта — только заголовок — ❔ (по разбору сайта, в README нет).
29. **В Amnezia VPN ключ не виден.** Ключ генерирует приложение при включении опции в настройках протокола сервера. ❔ по UI; в `protocolConstants.h` ключа-дефолта нет.
30. **S ≥ 12 при HPK.** ✅ go `S%d must be more then %d to use headerProtection`, kmod `-EINVAL`.
31. **Таймеры.** WireGuard: 120/5/180 с, keepalive 10 с. ✅ `constants.go`. Условие `RejectAfterTime > RekeyAfterTime` — вывод; дефолты Amnezia — `awg-protocol.md`.
32. **ContentPaddingAddition.** WG выравнивает данные до 16 байт; добавка размывает сетку. ✅ README (тип/диапазон); описание эффекта — вывод.
33. **H1–H4 на 3.x всё ещё нужны.** ✅ `receive.go` сверяет H на каждом пакете при любых флагах.
34. **RandomTrailers / DisableCookies.** ✅ код go/kmod/tools; ✏️ хвост — случайной длины до «окна» пира, а не «до самого большого пакета». Детали — `awg-protocol.md`.
35. **MTU 1280 в 3.1.** ✏️ не правило протокола: 1280 — дефолт мобильных клиентов Amnezia, десктоп 1376, `awg-quick` — MTU маршрута − 80. `awg-protocol.md`.
36. **RandomTrailers обязан совпадать.** ✅ `receive.go:618`.
37. **Кто поддерживает 3.0.** ✅ go/kmod/tools 3.0+; клиенты — `awg-protocol.md`.

## Клиенты

38. **Клиент ≠ движок.** Официальные приложения Amnezia (Android/iOS/Windows/Amnezia VPN) работают на amneziawg-go, OpenWrt и Linux-сервер — на модуле ядра; набор тегов и пределы определяет движок. ✅ README платформ amneziawg-go; движки сторонних клиентов — ❔.
39. **WireSock не шлёт I1–I5.** ❔ закрытый продукт; по сайту — release notes WireSock 3.4.4.1/3.4.5.1. Проверяй у вендора.
40. **Какой клиент лучше.** Официальные клиенты Amnezia первыми получают новые версии протокола. ✅ release notes.
41. **Почему параметры зависят от клиента.** Windows < 2.0.2 не сохранял H > 2147483647. ✅ release notes amneziawg-windows-client 2.0.2 («fix h values highlight»). Теги — движок (п. 26).
42. **Поля экрана AWG в Amnezia VPN.** Соответствуют ключам конфига: подсеть/порт, Jc/Jmin/Jmax, S, H (диапазоны), I1–I5, HPK, ContentPaddingAddition, 5 таймеров, RandomTrailers/DisableCookies. ✅ `protocolConstants.h`.
43. **Параметры на каждое устройство.** Shared — общие на сервер; sender-параметры можно и полезно разнообразить по устройствам. ✅ README (client-side).

## Мимикрия

44. **Профили (QUIC Initial/0-RTT, TLS ClientHello, DTLS 1.2/1.3, HTTP/3, SIP, STUN/TURN, DNS) и выбор.** 🛠/❔ шаблоны генератора; эффективность — наблюдение. Официально подтверждено только: I-пакеты шлются перед каждым handshake, теги — README; дефолт Amnezia — DNS-подобный I1.

## Предупреждения и проблемы

45. **Когда обфускация бессильна.** Блок по IP/ASN или белые списки. ✅ (следует из устройства протоколов).
46. **Анонимность.** Обфускация её не даёт: виден IP сервера, объёмы, время. ✅
47. **Не поднимается.** Сначала shared-параметры и версия; затем порт/firewall. ✅ `troubleshooting.md`.
48. **`Invalid argument`.** S<12 при HPK, пересечение H, ключи чужой версии. ✅ `uapi.go`, `netlink.c`.
49. **`Message too long`.** ✅ механизм (`-EMSGSIZE` в `netlink.c`); ✏️ цифры «3,4 КБ/3200 байт/3820 байт» — ❔ не измерены.
50. **Долгое подключение.** Меньше Jc/Jmax и I-пакетов. ✅ README (отправляются перед каждым handshake).
51. **Работало и перестало.** Таймеры (3.x) или блок сигнатуры; кнопка «Не работает» — 🛠.
52. **Сменил параметры на сервере — всё отвалилось.** Согласования нет: сначала раздай новые конфиги, потом меняй сервер (или второй сервер). ✅ (shared-параметры).
53. **Насколько замедляет.** Разово — Jc×средний размер + I-пакеты; постоянно — S4 и ContentPaddingAddition съедают MTU. ✅ вывод из README.

## Итог переноса

78 вопросов сайта → 53 пунктов. Убраны вопросы про UI/устройство генератора, установщики и сторонние продукты без влияния на конфиг (10 пунктов прошлой редакции); остальное объединено.
