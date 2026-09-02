# Integrations

## CDP clients

Prefer CDP when the task needs interactive automation, selectors, evaluation, forms, or client-side navigation.

Confirmed client families:

- Playwright via `chromium.connectOverCDP(...)`
- Puppeteer via `puppeteer.connect({ browserWSEndpoint })`
- chromedp via a remote allocator

Use the skill helper:

```bash
node scripts/run-cdp-task.js --client playwright --task "$TASK_FILE"
```

Task file contract:

```js
module.exports = async ({ page, context, browser, clientName, endpoint, helpers }) => {
  await page.goto('https://example.com');
  console.log(await page.title());
};
```

## `@lightpanda/browser`

Official docs also show `@lightpanda/browser` for starting a Lightpanda process directly from Node before connecting Playwright or Puppeteer. This skill does not depend on that package by default because it is designed to work first with a local binary, Docker, or a remote endpoint.

Use the package only when the task explicitly needs the npm-managed process lifecycle shown in the docs.

## MCP surface

The local repo exposes these MCP tools:

- `goto`
- `markdown`
- `links`
- `evaluate`
- `semantic_tree`
- `interactiveElements`
- `structuredData`
- `click`
- `fill`
- `scroll`

The local MCP resources exposed in source are:

- `mcp://page/html`
- `mcp://page/markdown`

Use MCP when the task is LLM-first and the caller already has an MCP transport, not when a plain CLI `fetch` or CDP client is simpler.
