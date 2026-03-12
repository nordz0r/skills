# Podkop: эксплуатация

## Совместимость и ограничения

- Podkop рассчитан на OpenWrt `24.10`.
- README требует минимум `25 MB` свободного места; install script отдельно проверяет lower bound по overlay.
- Проект в бете и может менять формат конфига между релизами.
- Dashboard завязан на HTTP и не работает корректно при HTTPS или доступе по доменному имени.
- IPv6 пока не реализован.

## Важные конфликты и prerequisites

- Конфликтующие пакеты из `podkop/Makefile`: `https-dns-proxy`, `nextdns`, `luci-app-passwall`, `luci-app-passwall2`.
- README отдельно требует удалить `Getdomains`.
- Основные runtime зависимости пакета:
  - `sing-box`
  - `curl`
  - `jq`
  - `kmod-nft-tproxy`
  - `coreutils-base64`
  - `bind-dig`

## Установка и обновление

Upstream-скрипт установки/обновления:

```sh
sh <(wget -O - https://raw.githubusercontent.com/itdoginfo/podkop/refs/heads/main/install.sh)
```

Скрипт:

- сам определяет `opkg` или `apk`;
- тянет последние релизные `ipk/apk` с GitHub Releases;
- проверяет DNS, свободное место, версию OpenWrt и rate limit GitHub;
- обновляет `podkop` и `luci-app-podkop`.

## Миграция конфига 0.7.0

Начиная с `0.7.0` структура `/etc/config/podkop` несовместима со старыми значениями.

Если обновление делается вручную, безопасная последовательность такая:

```sh
mv /etc/config/podkop /etc/config/podkop-070
wget -O /etc/config/podkop \
  https://raw.githubusercontent.com/itdoginfo/podkop/refs/heads/main/podkop/files/etc/config/podkop
```

После этого Podkop нужно настроить заново через LuCI или UCI.

## Основные файлы на роутере

- `/etc/config/podkop`: главный UCI-конфиг.
- `/etc/init.d/podkop`: procd service wrapper.
- `/usr/bin/podkop`: основной CLI/оркестратор.
- `/usr/lib/podkop/*`: shell-библиотеки, генерация `sing-box`, `nft`, rulesets, logging.
- `/etc/sing-box/config.json`: рабочий конфиг `sing-box`, который Podkop может переписывать.
- `/tmp/sing-box/cache.db`: кэш `sing-box`.

## Модель конфига

Базовый конфиг состоит минимум из:

- `config settings 'settings'`
- одной или нескольких секций `config section '<name>'`

В `settings` важны:

- `dns_type`
- `dns_server`
- `bootstrap_dns_server`
- `source_network_interfaces`
- `enable_output_network_interface`
- `output_network_interface`
- `enable_yacd`
- `disable_quic`
- `update_interval`
- `dont_touch_dhcp`
- `config_path`
- `cache_path`
- `log_level`

В `section` важны:

- `connection_type`
- `proxy_config_type`
- `proxy_string`
- `community_lists`
- `user_domains`
- `user_subnets`
- `local_domain_lists`
- `local_subnet_lists`
- `remote_domain_lists`
- `remote_subnet_lists`
- `fully_routed_ips`
- `mixed_proxy_enabled`

## CLI команды Podkop

Основные lifecycle-команды:

```sh
podkop start
podkop stop
podkop reload
podkop restart
```

Команды диагностики:

```sh
podkop list_update
podkop check_proxy
podkop check_nft_rules
podkop check_sing_box
podkop check_logs
podkop check_sing_box_logs
podkop check_fakeip
podkop show_config
podkop show_sing_box_config
podkop show_system_info
podkop global_check
```

## Что проверять первым при поломке

1. Совместима ли версия OpenWrt.
2. Не установлен ли конфликтующий пакет.
3. Есть ли рабочий outbound в секциях `config section`.
4. Существует ли сервис `sing-box` и подходит ли его версия.
5. Не остались ли старые значения в `/etc/config/podkop` после апдейта.
6. Не сломан ли `dnsmasq` после вмешательства Podkop.
