# amneziawg — kernel module (DKMS): установка и проверка

Используй kernel module (`kmod`) всегда, когда хост позволяет ставить DKMS-модули.
`amneziawg-go` — userspace-fallback для контейнеров без привилегий или экзотических ядер.

## Источник

- Репозиторий: `github.com/amnezia-vpn/amneziawg-linux-kernel-module`
- Тег сборки: **v3.1.20260906** (`git clone --branch v3.1.20260906`).
- `modinfo amneziawg | grep ^version` покажет `3.1.20260812` — это нормально:
  в `Makefile` зашита дата кодовой базы, не тег выпуска.

## Требования

```bash
# Заголовки под ЗАПУЩЕННОЕ ядро:
apt install linux-headers-$(uname -r) build-essential dkms
```

Если для текущего ядра заголовков в репозитории нет (например, Debian 12 с
устаревшим `6.1.0-9`) — см. раздел «Подводные камни» ниже.

## Установка

```bash
git clone --depth 1 --branch v3.1.20260906 \
    https://github.com/amnezia-vpn/amneziawg-linux-kernel-module.git
cd amneziawg-linux-kernel-module

# Раскладывает исходники в /usr/src/amneziawg-1.0.0 и dkms.conf:
make -C src DESTDIR=/ dkms-install

dkms add -m amneziawg -v 1.0.0

# Собрать под каждое установленное ядро:
for KDIR in /lib/modules/*/build; do
    KVER=$(basename "$(dirname "$KDIR")")
    dkms build  -m amneziawg -v 1.0.0 -k "$KVER"
    dkms install -m amneziawg -v 1.0.0 -k "$KVER"
done

modprobe amneziawg
echo amneziawg > /etc/modules-load.d/amneziawg.conf
```

Проверить статус DKMS:

```bash
dkms status amneziawg
modinfo amneziawg | grep -E '^version|^filename'
```

## Amnezia Docker-контейнер после установки модуля

Официальный контейнер (`amnezia-awg2` и аналоги) запускается `--privileged`
с bind-mount `/lib/modules`, поэтому `awg-quick` внутри автоматически
подхватывает модуль хоста.

После установки kmod достаточно перезапустить контейнер:

```bash
docker restart amnezia-awg2
```

Простой ≈ 10 с; клиенты переподключаются самостоятельно. Конфиги и ключи
в `/opt/amnezia` при рестарте сохраняются — ничего не теряется.

## Проверка: kernel vs userspace

На хосте:

```bash
lsmod | grep amneziawg        # есть строка — модуль загружен
```

Внутри контейнера или напрямую:

```bash
ip -d link show awg0          # тип "amneziawg" → kernel
ps aux | grep amneziawg-go    # строк нет → kernel
```

Признак userspace — процесс `amneziawg-go awg0` в `ps`. Тогда тип
интерфейса в `ip -d link` будет `tun type tun`, а не `amneziawg`.

## Подводные камни

### (a) Нет заголовков под текущее ядро

Debian 12 может держать ядро `6.1.0-9`, для которого `linux-headers-6.1.0-9-amd64`
уже удалён из репозитория. Решение: обновиться до актуального ядра и перезагрузиться.

```bash
apt install linux-image-amd64 linux-headers-amd64
# проверить, что ядра действительно новее:
ls /boot/vmlinuz-*
reboot
# после загрузки в новое ядро — повторить установку dkms build/install
```

Контейнеры с `restart=always` поднимутся автоматически. Суммарный простой
при перезагрузке хоста ≈ 40 с (против ≈ 10 с для docker restart без reboot).

### (b) Мало места на корневом разделе

При диске, заполненном более чем на ≈ 85–90%, сборка DKMS упадёт. Освободи
место, удалив старые ядра (оставь запущенное и следующее):

```bash
dpkg --list 'linux-image-*' | grep '^ii'
apt purge linux-image-<старая-версия> linux-headers-<старая-версия>
```

### (c) После обновления ядра DKMS не пересобирается без заголовков

При штатном `apt upgrade` может прийти новое ядро. Если `linux-headers-<новое>`
не был установлен заранее — DKMS не пересоберёт модуль и после reboot
интерфейс не поднимется. Заголовки нужно ставить **до** перезагрузки в новое ядро.

Проверить, под какие ядра есть сборки:

```bash
dkms status amneziawg
```

### (d) I1–I5 — только для amneziawg-go

В конфигах AWG 3.1 параметры обфускации I1–I5 принимают теги:
`b`, `t`, `r`, `rc`, `rd`, `<c>`, `<d>`, `<ds>`, `<dz>`.
Теги `<d>`, `<ds>`, `<dz>` поддерживаются **только** userspace `amneziawg-go`;
kernel module их не принимает.

Перед переключением на kmod проверь конфиги:

```bash
grep -E '<(d|ds|dz)>' /etc/amnezia/amneziawg/*.conf
```

Если строки есть — удали или замени поля I1–I5 совместимыми тегами
(или оставь сервер на userspace, пока клиенты не обновятся).

У Amnezia-сервера (Docker-стек) I-строки в серверном конфиге обычно
закомментированы — этого конфликта не будет.

### (e) Версия в modinfo отличается от тега

```
modinfo amneziawg | grep ^version
# → version: 3.1.20260812
```

Это нормально: версия в коде зафиксирована как `3.1.20260812`; тег репозитория
`v3.1.20260906` — более поздний выпуск той же кодовой базы. Не воспринимай
это как ошибку сборки.

## Эффект на производительность

Предварительные ручные замеры одного канала (не контролируемый эксперимент: разное время суток,
порядок не рандомизирован, повторов мало):

- Сервер 1 vCPU; userspace (`amneziawg-go`): 50–145 Мбит/с вниз к клиенту.
- Тот же сервер, kmod: 190–277 Мбит/с вниз (скриптовый замер, 3 повтора на точку).

Загрузка CPU под kmod **не измерялась**, причина разницы не установлена. Ожидаемо, что модуль
ядра избавляет от копирования через tun и переключений контекста, но на твоём железе и сети
эффект надо измерять самому (скрипт бенчмарка — в отчёте по тюнингу AWG 3.1).
