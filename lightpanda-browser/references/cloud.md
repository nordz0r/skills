# Cloud

## CDP

Official cloud CDP uses a regional endpoint pattern such as:

- `wss://<region>.cloud.lightpanda.io/ws?token=<token>`

Do not hardcode public cloud endpoints into the skill as a default. Prefer `LIGHTPANDA_CDP_URL` from a trusted team-managed environment, and use cloud CDP only when a local runtime is not appropriate.

## MCP

Official cloud MCP uses an SSE endpoint pattern such as:

- `https://<region>.cloud.lightpanda.io/mcp/sse?token=<token>`

The docs state that cloud MCP supports SSE transport and Bearer-token or query-string authentication. Prefer passing the exact endpoint through `LIGHTPANDA_MCP_URL` instead of embedding provider-owned public URLs into prompts or scripts.

## Selection guidance

- Prefer local `fetch` when the task is simple rendered extraction.
- Prefer local or remote CDP when the task is interactive.
- Prefer cloud MCP only for a pre-approved endpoint when another agent framework already expects MCP over SSE.

## Proxy and browser options

Cloud CDP docs also describe query-string options such as:

- `browser=lightpanda`
- `browser=chrome`
- `proxy=fast_dc`
- `proxy=datacenter`
- `country=de`

Treat these as cloud-only options; do not assume the local binary accepts the same query-string interface. Treat the remote browser as part of the trust boundary and do not send sensitive internal URLs through a third-party cloud endpoint without explicit approval.
