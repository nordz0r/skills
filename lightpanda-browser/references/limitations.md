# Limitations

## Open-source caveats

Base guidance on the current repo, not on idealized browser behavior.

- Local `Page.captureScreenshot` in the open-source CDP implementation currently returns an embedded placeholder PNG, not a real page capture.
- `Browser.setDownloadBehavior` exists in the CDP domain, but the current implementation is a no-op.
- Playwright compatibility is explicitly described by Lightpanda as partial and evolving; feature detection in Playwright can change behavior across versions.
- Lightpanda is positioned as beta software in the project README.

## What to promise

Promise confidently:

- rendered extraction through `fetch`
- CDP connectivity
- Playwright or Puppeteer control for supported flows
- MCP browsing and extraction
- markdown, links, semantic tree, interactive elements, and structured data extraction

Treat as best-effort:

- screenshot-heavy visual validation
- download persistence workflows
- arbitrary Playwright feature parity with Chromium
- pixel-perfect UI test suites

## Fallback rule

If the task is primarily about screenshots, download handling, or Chromium-specific browser automation reliability, switch to `playwright-skill` and say why.
