---
name: administering-linux
description: "Hands-on Linux administration of a systemd host: journalctl, systemctl, unit, drop-in, failed-service after reboot, OOM, df, ssh, Ubuntu Debian. Not Docker and not Ansible. Triggers: journalctl, unit file, drop-in, oom killer, disk full, sshd, ubuntu server, failed unit, vendor unit, host troubleshooting, сервер, диск заполнен, служба не стартует, логи, линукс."
---

# Administering Linux

Working skill for operating a Linux server. The goal is to fix the host with commands
that can be copied, not to retell man pages.

Do not use this skill as the primary one for Docker, GitLab CI, Ansible, Amnezia
or policy routing: they have their own skills (`docker-ops`, `gitlab-ci`,
`ansible-playbook`, `amnezia-vpn`, `linux-routing`).

## When to use

- A service does not start, crashes, does not listen on its port, does not come up after reboot.
- You need a unit file, timer, drop-in override, logrotate.
- CPU/RAM/IO/disk full/OOM/load analysis.
- Users, sudo, SSH, packages, basic firewall.
- "Why is the host slow / refusing logins / not resolving DNS".

## Workflow

1. Pin down the distro and the host's role: `source /etc/os-release; hostnamectl; uptime`.
2. Isolate the symptom: service, disk, memory, network, auth.
3. Look at facts, not hypotheses: `systemctl --failed`, `journalctl -xe`, `df -h`,
   `free -h`, `ss -lntup`.
4. Change one layer at a time. For unit files use a drop-in; do not edit the vendor unit.
5. After the fix verify: service status, port, log, reboot persistence (`enable`).

## Quick facts

```bash
source /etc/os-release
systemctl --failed
journalctl -p err -b --no-pager | tail -n 80
df -hT
free -h
ss -lntup
```

- Ubuntu/Debian: `apt`, netplan, often `ufw`.
- RHEL/Rocky/Alma: `dnf`, NetworkManager, often `firewalld` + SELinux.
- Do not `kill -9` a process until `systemctl stop` / SIGTERM is exhausted.
- Do not restart `sshd` in your only session without a passing `sshd -t` and
  a fallback channel.

## Companion skills

- Docker daemon, compose, container will not start → `docker-ops`.
- Playbooks and idempotency → `ansible-playbook`.
- `ip rule`, fwmark, nft NAT, policy routing → `linux-routing`.
- Pipeline/runner → `gitlab-ci`.

## References

- `references/systemd-journal.md` — unit files, drop-in, timers, journalctl.
- `references/diagnosis.md` — CPU/RAM/IO/disk/OOM/network/SSH, ready-made commands.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: linux systemd journalctl systemctl sshd unit file disk full oom load average apt dnf ubuntu debian rhel rocky host troubleshooting
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->

Russian version: [`references/README.ru.md`](references/README.ru.md).
