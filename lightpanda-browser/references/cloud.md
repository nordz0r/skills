# Cloud

## CDP

Official cloud CDP endpoints are documented in regional form:

- `wss://euwest.cloud.lightpanda.io/ws?token=TOKEN`
- `wss://uswest.cloud.lightpanda.io/ws?token=TOKEN`

Use CDP cloud endpoints for remote browser automation with Playwright, Puppeteer, or chromedp when no local runtime should be started.

## MCP

Official cloud MCP is documented as an SSE endpoint:

- `https://euwest.cloud.lightpanda.io/mcp/sse?token=TOKEN`
- `https://uswest.cloud.lightpanda.io/mcp/sse?token=TOKEN`

The docs state that cloud MCP supports SSE transport and Bearer-token or query-string authentication.

## Selection guidance

- Prefer local `fetch` when the task is simple rendered extraction.
- Prefer local or remote CDP when the task is interactive.
- Prefer cloud MCP when another agent framework already expects MCP over SSE.

## Proxy and browser options

Cloud CDP docs also describe query-string options such as:

- `browser=lightpanda`
- `browser=chrome`
- `proxy=fast_dc`
- `proxy=datacenter`
- `country=de`

Treat these as cloud-only options; do not assume the local binary accepts the same query-string interface.
