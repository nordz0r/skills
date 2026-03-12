# PBR: сценарии и ограничения

## Что умеют политики

Политики можно строить по:

- source IP / subnet / local device name
- source MAC
- source port
- destination IP / subnet
- destination domain
- destination port
- protocol
- DSCP

Также есть DNS policies и custom user files.

## Когда особенно полезен `dnsmasq.nftset`

- Когда policies строятся по доменам.
- Когда много доменов и нужно избегать долгого resolve на старте.
- Когда важны wildcard-like эффекты на поддомены.

## DNS policies

DNS policies позволяют отправлять DNS-запросы от конкретных устройств/IP/MAC через заданный DNS path.

Важно:

- DNS policy override-ит local DNS hijacking;
- domain-based policies для этих клиентов могут перестать работать, если они больше не спрашивают локальный `dnsmasq`.

## Custom user files

Используй их, если:

- доменов или IP слишком много для ручного UCI;
- нужно подкачать большие списки;
- нужно кастомно дописать `nft` или ucode logic.

Поддерживаются:

- shell scripts (`.sh` или без расширения)
- `ucode` scripts (`.uc`)

Из готовых upstream examples есть:

- `pbr.user.dnsprefetch`
- `pbr.user.aws.uc`
- `pbr.user.netflix.uc`

## WireGuard server special cases

По умолчанию `pbr` старается сохранить доступность WireGuard server даже если default gateway это туннель.

Сценарии:

- Нужно таргетировать WG server в policies: добавь интерфейс в `supported_interface`.
- Нужно убрать принудительную отправку server traffic через WAN: добавь интерфейс в `ignored_interface`.
- Нужно и то и другое: добавь в оба списка.

## Ограничения

- `pbr` не поддерживает broken "killswitch router mode" с разрушенной стандартной схемой OpenWrt.
- Если default route идет через VPN tunnel, некоторые сценарии WireGuard server по UDP нельзя корректно перехватить rules alone.
- Для physical device policies могут понадобиться дополнительные пакеты:
  - `kmod-br-netfilter`
  - `kmod-ipt-physdev`
  - `iptables-mod-physdev`

## Важные DNS caveats

- При `dnsmasq.nftset` очисти DNS cache на клиентах, иначе domain policies могут казаться "нерабочими".
- Browser DoH может полностью обходить `dnsmasq`, и тогда domain routing не сработает так, как ожидается.
