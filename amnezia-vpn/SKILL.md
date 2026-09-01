---
name: amnezia-vpn
description: >-
  Практическая работа с Amnezia VPN и AmneziaWG на Linux/VPS/Docker: стек
  контейнеров /opt/amnezia, awg/awg-quick, kernel module amneziawg,
  userspace amneziawg-go, Jc/Jmin/Jmax/S1/S2/H1-H4, Xray/Reality рядом со
  стеком, диагностика handshake. Используй этот skill, когда задача про
  AmneziaVPN, amnezia-awg, docker amnezia, Linux AWG-сервер, не OpenWrt.
  Для OpenWrt UCI/LuCI бери amneziawg-openwrt-guide. Триггеры: amnezia,
  amnezia vpn, amneziawg, awg-quick, awg0, /opt/amnezia, amneziawg-go,
  Jc Jmin Jmax, obfuscation, amnezia docker, VPS VPN.
---

# Amnezia VPN (Linux / Docker)

Skill про Amnezia на Linux-сервере и Docker-стеке приложения.
Это не OpenWrt-интеграция: UCI/LuCI/`kmod-amneziawg` на роутере —
`amneziawg-openwrt-guide`.

Селективный routing на OpenWrt через podkop — `podkop-openwrt-guide`.
Policy routing на Linux-хосте — `linux-routing`.

## Когда использовать

- Поднять или чинить AmneziaVPN на VPS (официальный Docker-стек).
- Linux AWG без GUI: `awg`, `awg-quick`, kernel module vs `amneziawg-go`.
- Нет handshake, неверный Jc/Jmin/Jmax/S1/S2/H1-H4, порт закрыт.
- Контейнеры `amnezia-*`, данные `/opt/amnezia`, docker logs.
- Соседние протоколы стека: WireGuard, Xray/Reality, OpenVPN, Cloak, SS —
  только в контексте Amnezia, не как отдельный продукт.

## Workflow

1. Раздели сценарий:
   - GUI AmneziaVPN → Docker-контейнеры на VPS.
   - Голый AWG → `awg0` + `awg-quick` / kernel module.
   - OpenWrt роутер → другой skill.
2. Не логируй PrivateKey, preshared key, obfuscation secrets целиком.
   В ответах — плейсхолдеры.
3. Handshake = ключи + одинаковые obfuscation params + UDP порт + endpoint.
4. После изменений: `awg show` / `docker ps` / `ss -ulnp` / ping внутри туннеля.

## Что есть в стеке

Официальное приложение поднимает Docker на сервере. Данные обычно в
`/opt/amnezia`. Контейнеры именуются с префиксом `amnezia-`.

Голый AmneziaWG совместим с WireGuard по модели ключей, но пакеты не
пройдут, если junk/header params не совпали на обеих сторонах.

| Слой | Зачем |
|------|--------|
| `kmod amneziawg` | kernel datapath, низкий overhead |
| `amneziawg-go` | userspace fallback, если модуля нет |
| `awg` / `awg-quick` | как `wg` / `wg-quick` |

## Companion skills

- OpenWrt AWG → `amneziawg-openwrt-guide`.
- Docker engine/compose синтаксис → `docker-ops`.
- `ip rule`/nft для split-tunnel на Linux → `linux-routing`.
- Host systemd/disk/ssh → `administering-linux`.

## References

- `references/linux-awg.md` — awg-quick, kernel/userspace, диагностика.
- `references/docker-stack.md` — контейнеры AmneziaVPN на VPS.

<!-- A-EVOLVE-ROUTING-SIGNALS:START -->
## Routing signals: amnezia amneziavpn amneziawg awg-quick awg0 opt/amnezia docker vpn jc jmin jmax handshake amneziawg-go vps
<!-- A-EVOLVE-ROUTING-SIGNALS:END -->
