# Диагностика Linux-хоста

Снимай факты сверху вниз. Не меняй sysctl/sshd, пока не понял слой поломки.

## 60-секундный осмотр

```bash
uptime
source /etc/os-release; echo "$PRETTY_NAME"
systemctl is-system-running
systemctl --failed --no-pager
free -h
df -hT
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,UUID
ss -lntup
ip -br addr
ip route
```

## CPU и load

```bash
nproc
cat /proc/loadavg
ps aux --sort=-%cpu | head -n 15
pidstat 1 5
```

Load выше числа ядер — смотри D-state и iowait:

```bash
ps -eo pid,stat,wchan:20,cmd | awk '$2 ~ /D/'
vmstat 1 10
```

## Память и OOM

```bash
free -h
ps aux --sort=-%mem | head -n 15
dmesg -T | grep -iE 'oom|killed process' | tail
journalctl -k -b | grep -i oom
```

`oom-kill` почти всегда значит: сервис съел RAM, лимита не было, swap маленький.
Лечи лимитом systemd (`MemoryMax=`) или cgroup, не `swapiness=0` вслепую.

## Диск

```bash
df -hT
df -i
du -xhd1 / | sort -h
lsof +L1 | head                 # удалённые, но открытые файлы
```

`df` полный, `du` маленький → процесс держит удалённый лог. Рестарт сервиса
освобождает inode.

## Сеть хоста

```bash
ip -br link
ip -br addr
ip route get 1.1.1.1
ss -lntup
ss -tnp state established
resolvectl status
ping -c 2 1.1.1.1
ping -c 2 google.com
```

Интерфейс UP, адреса нет → netplan/NM. Порт не слушает → unit failed.
Пакеты уходят не туда → `linux-routing`, не этот файл.

Ubuntu netplan apply держи с запасной сессией:

```bash
netplan try --timeout 30
```

## SSH

```bash
sshd -t
sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|pubkeyauthentication|port |allowusers'
journalctl -u ssh -u sshd --since "30 min ago" --no-pager
```

Меняя `/etc/ssh/sshd_config.d/99-hardening.conf`, не закрывай текущую сессию:

```
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
```

Debian/Ubuntu unit может называться `ssh.service`, RHEL — `sshd.service`.

## Пакеты

Debian/Ubuntu:

```bash
apt update
apt -s install <pkg>     # dry-run
apt-cache policy <pkg>
```

RHEL-семейство:

```bash
dnf makecache
dnf install --assumeno <pkg>
rpm -q <pkg>
```

Не мешай vendor-репозиторий и сторонний pin без фиксации версии.

## Пользователи

```bash
id alice
getent passwd alice
groups alice
sudo -lU alice
```

Сервисный пользователь без login shell:

```bash
useradd --system --home-dir /var/lib/app --shell /usr/sbin/nologin app
```
