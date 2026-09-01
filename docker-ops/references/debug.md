# Диагностика Docker

## Состояние

```bash
docker info
docker compose ps -a
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}'
docker inspect --format '{{.State.Status}} {{.State.ExitCode}} {{.State.Error}}' CONTAINER
docker inspect --format '{{json .State.Health}}' CONTAINER | jq
```

`Restarting (1)` — процесс сразу выходит. Сначала `logs`, потом `inspect.Config.Cmd`.

## Логи

```bash
docker logs --tail 200 --timestamps CONTAINER
docker compose logs --tail=200 --timestamps api
journalctl -u docker -e --no-pager
```

Если логов нет: процесс пишет не в stdout или logging driver другой.

## Почему unhealthy / Restarting

1. `Cmd`/`Entrypoint` неверный или бинаря нет.
2. Конфиг/ENV не смонтированы.
3. Volume permissions vs `USER`.
4. Healthcheck бьёт не в тот адрес (`localhost` vs `0.0.0.0`, IPv6).
5. Зависимость не healthy, но сервис стартовал без `condition:`.

```bash
docker compose exec api sh -c 'id; ls -l /app; env | sort'
docker compose exec api wget -S -O- http://127.0.0.1:8080/health
```

## Сеть и порты

```bash
docker port CONTAINER
ss -lntup | grep 8080
docker network inspect app-net
docker compose exec api ping -c1 postgres
```

Порт в `ports:` опубликован, но `ss` пустой → контейнер не слушает.
Слушает только IPv6 или другой bind.

`network_mode: host` обходит compose DNS и публикует все порты процесса.

## Диск overlay2

```bash
docker system df -v
du -sh /var/lib/docker
docker builder prune
docker image prune -f
```

Не делай `docker system prune -a --volumes` на проде без явного запроса:
снесутся unused images и anonymous volumes.

## Daemon и socket

```bash
systemctl status docker --no-pager -l
journalctl -u docker -b --no-pager | tail -n 80
ls -l /var/run/docker.sock
```

Permission denied на socket → пользователь не в группе `docker`, либо
rootless vs rootful mismatch.

`daemon.json` минимум:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true
}
```

После правки: `systemctl reload docker` или `restart`. `live-restore`
не переживает рестарт daemon для всех кейсов — проверяй контейнеры.

## Частые ошибки

| Симптом | Куда смотреть |
|---------|----------------|
| `port is already allocated` | `ss -lntup`, старый контейнер, host service |
| `Bind for 0.0.0.0:80 failed` | nginx/angie на хосте |
| `no such file or directory` | Windows CRLF в entrypoint.sh, нет `chmod +x` |
| `permission denied` в volume | UID в образе vs owner на bind-mount |
| DNS в контейнере мёртв | `172.17.0.1:53`, `iptables`/`nft`, DNS на хосте |
| Image pull 401 | `docker login`, CI job token vs deploy token |
