---
name: administering-linux
description: "Практическая Linux-админка systemd-хоста: journalctl, systemctl, unit, drop-in, failed-service after reboot, OOM, df, ssh, Ubuntu Debian. Не Docker и не Ansible. Триггеры: journalctl, unit file, drop-in, oom killer, disk full, sshd, ubuntu server, failed unit, vendor unit, host troubleshooting."
---

# Administering Linux

Рабочий skill для эксплуатации Linux-сервера. Цель — починить хост командами,
которые можно копировать, а не пересказывать man pages.

Не используй этот skill как основной для Docker, GitLab CI, Ansible, Amnezia
или policy routing: там свои skills (`docker-ops`, `gitlab-ci`,
`ansible-playbook`, `amnezia-vpn`, `linux-routing`).

## Когда использовать

- Сервис не стартует, падает, не слушает порт, не поднимается после reboot.
- Нужен unit file, timer, drop-in override, logrotate.
- Разбор CPU/RAM/IO/disk full/OOM/load.
- Пользователи, sudo, SSH, пакеты, базовый firewall.
- «Почему хост тормозит / не пускает / не резолвит DNS».

## Workflow

1. Зафиксируй distro и роль хоста: `source /etc/os-release; hostnamectl; uptime`.
2. Отдели симптом: сервис, диск, память, сеть, auth.
3. Смотри факты, не гипотезы: `systemctl --failed`, `journalctl -xe`, `df -h`,
   `free -h`, `ss -lntup`.
4. Меняй один слой за раз. Для unit-файлов — drop-in, не правь vendor unit.
5. После фикса проверь: статус сервиса, порт, лог, reboot-persistence (`enable`).

## Быстрые факты

```bash
source /etc/os-release
systemctl --failed
journalctl -p err -b --no-pager | tail -n 80
df -hT
free -h
ss -lntup
```

- Ubuntu/Debian: `apt`, netplan, часто `ufw`.
- RHEL/Rocky/Alma: `dnf`, NetworkManager, часто `firewalld` + SELinux.
- Не убивай процесс через `kill -9`, пока не исчерпан `systemctl stop` / SIGTERM.
- Не рестартуй `sshd` в единственной сессии без проверенного `sshd -t` и
  запасного канала.

## Companion skills

- Docker-демон, compose, контейнер не стартует → `docker-ops`.
- Плейбуки и идемпотентность → `ansible-playbook`.
- `ip rule`, fwmark, nft NAT, policy routing → `linux-routing`.
- Pipeline/runner → `gitlab-ci`.

## References

- `references/systemd-journal.md` — unit files, drop-in, timers, journalctl.
- `references/diagnosis.md` — CPU/RAM/IO/disk/OOM/сеть/SSH, готовые команды.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: linux systemd journalctl systemctl sshd unit file disk full oom load average apt dnf ubuntu debian rhel rocky host troubleshooting
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
