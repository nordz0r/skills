# Podkop: proxy URL-строки

Podkop принимает строковые proxy-конфиги и использует их как вход для генерации outbound в `sing-box`.

Основной upstream reference: `String-example.md`.

## Поддерживаемые схемы

- `socks4://`
- `socks4a://`
- `socks5://`
- `ss://`
- `vless://`
- `trojan://`
- `hysteria2://`
- `hy2://`

## Что важно помнить

- Для `VLESS` и `Trojan` upstream приводит примеры для `tcp`, `kcp`, `ws`, `grpc`, `httpupgrade`, `xhttp`.
- Для `tls/reality/ech` важны query-параметры вроде `sni`, `fp`, `pbk`, `sid`, `alpn`, `ech`.
- Для `hysteria2` важны `sni`, `obfs`, `obfs-password`, `insecure`.
- Часть валидаторов frontend живет в `fe-app-podkop/src/validators/`.

## Практическое правило

Если задача про "почему Podkop не принимает строку", сверяй одновременно:

1. `String-example.md`
2. frontend validators
3. shell/backend обработку outbound

И не предполагай, что любая Xray/V2Ray-строка автоматически совместима с текущей реализацией Podkop.
