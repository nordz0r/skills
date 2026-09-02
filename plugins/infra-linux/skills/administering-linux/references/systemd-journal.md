# systemd и journald

## Статус и управление

```bash
systemctl status nginx --no-pager -l
systemctl cat nginx.service
systemctl show nginx.service -p ActiveState,SubState,MainPID,FragmentPath,DropInPaths
systemctl list-units --type=service --state=failed
systemctl list-unit-files nginx.service
systemctl daemon-reload
systemctl enable --now nginx
systemctl restart nginx
systemctl reload nginx
```

`reload` только если unit объявил `ExecReload=`. Иначе это no-op или ошибка.

## Drop-in вместо правки vendor unit

```bash
systemctl edit nginx.service
```

Пишет `/etc/systemd/system/nginx.service.d/override.conf`:

```ini
[Service]
LimitNOFILE=65535
Environment=NGINX_ENTRYPOINT_QUIET_LOGS=1
```

Снять override:

```bash
systemctl revert nginx.service
```

Полный custom unit — только в `/etc/systemd/system/`. Не правь `/lib/systemd/system/` и `/usr/lib/systemd/system/`.

## Шаблон service

```ini
[Unit]
Description=Example app
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/app
EnvironmentFile=-/etc/app/env
ExecStart=/usr/bin/app --config /etc/app/config.yaml
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=3
TimeoutStopSec=20
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/app /var/log/app

[Install]
WantedBy=multi-user.target
```

После записи:

```bash
systemd-analyze verify /etc/systemd/system/app.service
systemctl daemon-reload
systemctl enable --now app
```

`Type=` выбирай по факту:

| Type | Когда |
|------|--------|
| `simple` | процесс на переднем плане |
| `forking` | классический daemon с PIDFile |
| `oneshot` | скрипт, который должен завершиться |
| `notify` | сервис шлёт READY=1 через sd_notify |

## Timers вместо cron

`/etc/systemd/system/backup.service`:

```ini
[Unit]
Description=Nightly backup

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/backup.sh
```

`/etc/systemd/system/backup.timer`:

```ini
[Unit]
Description=Run backup nightly

[Timer]
OnCalendar=*-*-* 02:15:00
Persistent=true
RandomizedDelaySec=5min

[Install]
WantedBy=timers.target
```

```bash
systemctl enable --now backup.timer
systemctl list-timers --all
```

## journalctl

```bash
journalctl -u nginx -e --no-pager
journalctl -u nginx -f
journalctl -u nginx --since "10 min ago"
journalctl -u nginx -p err..alert
journalctl -b -p err --no-pager
journalctl -k -b          # kernel / OOM
journalctl --disk-usage
journalctl --vacuum-time=14d
```

Persistent journal:

```bash
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald
```

Конфиг: `/etc/systemd/journald.conf.d/size.conf`

```ini
[Journal]
SystemMaxUse=1G
MaxRetentionSec=14day
```
