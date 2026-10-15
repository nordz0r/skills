# Сторонние инструменты: Architect и awg-containers-and-tools

Оба проекта — **неофициальные** (автор Vadim Khristenko), не связаны с AmneziaVPN.
Разобраны 2026-10-15 по исходникам; ничего не запускалось. Факты протокола — только из
`awg-protocol.md` (upstream); здесь — что полезно и чем рисковать.

## Any-Tech-ARCHITECT (architect.vai-rice.space)

Репо `github.com/Vadim-Khristenko/Any-Tech-ARCHITECT` @ 0b9d3b7 (2026-10-08), Vue SPA, MIT.

Полезно:
- генератор параметров AWG 1.0–3.1 и Xray (`src/engines/awg/generator/*`, `src/engines/xray/*`) — удобен как черновик, но выход **проверяй** по `config-checklist.md`;
- валидатор конфигов — перенесён как `config-checklist.md` (со статусами);
- FAQ — `faq.md`;
- офлайн-генерация без браузера: `scripts/awg-gen.sh` (bash, `/dev/urandom`, флаги `-v 3.0|3.1`, `-p quic|tls|…`, `-n N`); сайт локально — `scripts/serve.sh` / релизный `awg-serve`;
- разбор/сборка/слияние ключей `vpn://` (`src/engines/keys/*`) — на клиенте, без сервера.

Найденные неточности исходника (см. `faq.md`): «S4 ≤ 32» и потолки S1 1132 / S2 1188 с неверной арифметикой;
ряд версий Xray (ML-DSA, VLESS Encryption, Hysteria, FinalMask); последнее ядро в таблице — v26.7.11.

## awg-containers-and-tools

Репо `github.com/Vadim-Khristenko/awg-containers-and-tools` @ 7524a4a (2026-09-25), MIT.
Docker-образы `vaiprog/amnezia-wg-{1,15,2,3,31}` (+ `-dns`, `-status`) и Rust CLI `awg-tool`.

Полезные приёмы (проверены по upstream):
- **Конфиг через UAPI вместо `awg setconf`.** Entrypoint переводит `.conf` в запрос `set=1` и пишет его в сокет
  `/var/run/amneziawg/<iface>.sock` amneziawg-go (через `socat`), проверяя `errno=0`. Так одна схема работает
  для всех поколений. ✅ ключи — из `device/uapi.go`. ✏️ README проекта утверждает, что `amneziawg-tools`
  не понимает ключи 3.x: в tools v3.1.20260812 `config.c` уже разбирает `HeaderProtectionKey`,
  `RandomTrailers`, `DisableCookies` — для актуальных версий обходной путь не обязателен.
- **Сборка amneziawg-go по поколениям** (multi-stage, `golang:1.26-alpine` → `alpine:3.24`): теги
  `v0.2.12` (1.0), `v0.2.14-beta-awg-1.5-1` (1.5), `v0.2.19` (2.0), `v3.0.20260805` (3.0), `v3.1.20260828` (3.1) —
  ✅ все существуют в `amnezia-vpn/amneziawg-go`. Нужен Go ≥ 1.25 для v3.x (по комментарию в Dockerfile, ❔).
- **Compose-шаблон без `privileged`:** `cap_add: [NET_ADMIN]`, `devices: /dev/net/tun`, `sysctls: net.ipv4.ip_forward=1`,
  отдельный unbound-резолвер с `cap_drop: [ALL]`, `read_only`. Хороший минимум прав для userspace-AWG в Docker.
- **Bare-metal план** (`crates/awg-core/src/deploy/prepare.rs`): `/etc/sysctl.d/99-amneziawg-forward.conf`
  вместо `sysctl -w` (переживает reboot), идемпотентные `iptables -C … || iptables -A …` для FORWARD и MASQUERADE.
- Утилиты в образе: `awg-uapi get`, `awg-peer add`, `awg-health`, `awg-leak`, `awg-dump.sh`; self-test с реальным handshake.

### Security-ревью (статический, без запуска)

| Что | Оценка |
|---|---|
| `curl … \| bash` | не найдено |
| Телеметрия / аналитика | не найдено; `awg-tool update` по запросу ходит в `api.github.com/…/releases/latest` и Docker Hub (проверка версий) |
| Бинарники CLI | публикуются с `sha256`-файлом, **без подписи** (README сам предупреждает) |
| Docker-образы | сторонний namespace `vaiprog/*`, в compose `:latest` — **закрепляй digest** или собирай сам из Dockerfile |
| Сборка | `git clone --depth 1 --branch <tag>` без проверки коммита/подписи — тег upstream можно перевесить; пинить SHA |
| Права контейнера | `NET_ADMIN` + `/dev/net/tun`, без `privileged`/`host`-сети — норм |
| SSH-деплой | проверка host key через `known_hosts`, новый ключ — только после явного подтверждения; ✅ |
| Пароли SSH | опционально сохраняются **открытым текстом** в `~/.config/awg-tool` (`SecretFile.passwords`) — не включай, используй ключи |
| Отладка | `AWG_DUMP_REQUEST=1` пишет UAPI-запрос с приватным ключом в `/tmp/uapi-set.req` (opt-in) — не включать в проде |
| Действия на хосте | ставит пакеты, компилирует Go на сервере, пишет systemd unit и iptables-правила — запускать только на выделенном VPS |

Вывод: как источник приёмов (UAPI, compose, сборка по тегам) — полезен; как установщик — допустим при
пиннинге образов/коммитов и без сохранения паролей. Официальные пути — `docker-stack.md`, `linux-awg.md`.
