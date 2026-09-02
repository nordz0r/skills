#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const {
  buildLocalCommand,
  parseCliArgs,
  resolveRuntime,
  spawnCommand,
  toWebSocketUrl,
  waitForPort,
} = require('./lib/runtime');

function usage() {
  console.log(`Usage:
  node scripts/run-cdp-task.js --client playwright --task <task-file> [--endpoint ws://127.0.0.1:9222] [--dry-run]

Task file contract:
  module.exports = async ({ browser, context, page, clientName, endpoint, helpers }) => { ... }`);
}

function toBool(value) {
  return value === true || value === 'true' || value === '1';
}

async function connectPlaywright(endpoint) {
  const { chromium } = require('playwright-core');
  const browser = await chromium.connectOverCDP(endpoint);
  const context = await browser.newContext({});
  const page = await context.newPage();
  return { browser, context, page };
}

async function connectPuppeteer(endpoint) {
  const puppeteer = require('puppeteer-core');
  const browser = await puppeteer.connect({ browserWSEndpoint: endpoint });
  const context = await browser.createBrowserContext();
  const page = await context.newPage();
  return { browser, context, page };
}

function loadTask(taskPath) {
  const resolved = path.resolve(taskPath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`Task file not found: ${resolved}`);
  }

  const task = require(resolved);
  if (typeof task !== 'function') {
    throw new Error('Task file must export an async function via module.exports');
  }
  return { task, resolved };
}

async function startLocalServer(options) {
  const spec = buildLocalCommand('serve', {
    host: options.host,
    port: options.port,
    timeout: options.timeout,
    logLevel: options['log-level'] || 'warn',
    logFormat: options['log-format'] || 'logfmt',
  });
  const child = spawnCommand(spec, { stdio: 'inherit' });
  const host = options.host || resolveRuntime().defaultHost;
  const port = parseInt(options.port || `${resolveRuntime().defaultPort}`, 10);
  await waitForPort(host, port, 15000);
  return { child, endpoint: toWebSocketUrl(host, port) };
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv.includes('--help')) {
    usage();
    return;
  }

  const { options } = parseCliArgs(argv);
  const clientName = options.client || 'playwright';
  const taskPath = options.task;
  if (!taskPath) {
    throw new Error('Missing --task');
  }

  const runtime = resolveRuntime();
  const endpoint = options.endpoint || runtime.cdpUrl || null;
  const dryRun = toBool(options['dry-run']);
  const executionPlan = {
    client: clientName,
    task: path.resolve(taskPath),
    endpoint: endpoint || `ws://${options.host || runtime.defaultHost}:${options.port || runtime.defaultPort}`,
    runtimeStrategy: endpoint ? runtime.strategy : runtime.strategy,
    usesLocalServer: !endpoint,
  };

  if (dryRun) {
    console.log(JSON.stringify(executionPlan, null, 2));
    return;
  }

  let server = null;
  let session = null;
  const { task, resolved } = loadTask(taskPath);

  try {
    let effectiveEndpoint = endpoint;
    if (!effectiveEndpoint) {
      server = await startLocalServer(options);
      effectiveEndpoint = server.endpoint;
    }

    if (clientName === 'playwright') {
      session = await connectPlaywright(effectiveEndpoint);
    } else if (clientName === 'puppeteer') {
      session = await connectPuppeteer(effectiveEndpoint);
    } else {
      throw new Error(`Unsupported client: ${clientName}`);
    }

    const helpers = {
      resolvedTaskPath: resolved,
      saveJson(filePath, value) {
        fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
      },
    };

    await task({
      browser: session.browser,
      context: session.context,
      page: session.page,
      clientName,
      endpoint: effectiveEndpoint,
      helpers,
    });
  } finally {
    if (session) {
      try {
        if (session.page) {
          await session.page.close();
        }
      } catch {}
      try {
        if (session.context) {
          await session.context.close();
        }
      } catch {}
      try {
        if (clientName === 'playwright') {
          await session.browser.close();
        } else {
          await session.browser.disconnect();
        }
      } catch {}
    }

    if (server && server.child && !server.child.killed) {
      server.child.kill('SIGTERM');
    }
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
