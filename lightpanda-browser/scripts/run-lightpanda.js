#!/usr/bin/env node

const fs = require('fs');
const { spawnCommand, buildLocalCommand, parseCliArgs, resolveRuntime } = require('./lib/runtime');

function printUsage() {
  console.log(`Usage:
  node scripts/run-lightpanda.js fetch --url <url> [--dump markdown] [--out file] [--dry-run]
  node scripts/run-lightpanda.js serve [--host 127.0.0.1] [--port 9222] [--timeout 10] [--dry-run]
  node scripts/run-lightpanda.js mcp [--dry-run]
  node scripts/run-lightpanda.js describe`);
}

function toBool(value) {
  return value === true || value === 'true' || value === '1';
}

function parseCommonOptions(options) {
  return {
    obeyRobots: toBool(options['obey-robots']),
    httpProxy: options['http-proxy'],
    proxyBearerToken: options['proxy-bearer-token'],
    httpMaxConcurrent: options['http-max-concurrent'],
    httpMaxHostOpen: options['http-max-host-open'],
    httpTimeout: options['http-timeout'],
    httpConnectTimeout: options['http-connect-timeout'],
    httpMaxResponseSize: options['http-max-response-size'],
    insecureDisableTlsHostVerification: toBool(options['insecure-disable-tls-host-verification']),
    logLevel: options['log-level'],
    logFormat: options['log-format'],
    userAgentSuffix: options['user-agent-suffix'],
  };
}

function printSpec(spec) {
  console.log(JSON.stringify({
    command: spec.command,
    args: spec.args,
    envOverrides: {
      LIGHTPANDA_DISABLE_TELEMETRY: spec.env.LIGHTPANDA_DISABLE_TELEMETRY,
    },
  }, null, 2));
}

async function runFetch(options, positionals) {
  const url = options.url || positionals[0];
  if (!url) {
    throw new Error('Missing --url for fetch');
  }

  const runtime = resolveRuntime();
  if (runtime.strategy === 'cloud') {
    throw new Error('Cloud runtime exposes CDP/MCP endpoints, not the local fetch CLI. Use a local binary or Docker for fetch.');
  }

  const spec = buildLocalCommand('fetch', {
    ...parseCommonOptions(options),
    url,
    dump: options.dump,
    out: options.out,
    stripMode: options['strip-mode'],
    withBase: toBool(options['with-base']),
    withFrames: toBool(options['with-frames']),
  });

  if (toBool(options['dry-run'])) {
    printSpec(spec);
    return;
  }

  if (options.out) {
    const child = spawnCommand(spec, { stdio: ['inherit', 'pipe', 'inherit'] });
    const chunks = [];
    child.stdout.on('data', (chunk) => chunks.push(chunk));
    await new Promise((resolve, reject) => {
      child.on('exit', (code) => {
        if (code === 0) {
          resolve();
          return;
        }
        reject(new Error(`Lightpanda fetch exited with code ${code}`));
      });
      child.on('error', reject);
    });
    fs.writeFileSync(options.out, Buffer.concat(chunks));
    console.log(`Saved output to ${options.out}`);
    return;
  }

  const child = spawnCommand(spec);
  await new Promise((resolve, reject) => {
    child.on('exit', (code) => (code === 0 ? resolve() : reject(new Error(`Lightpanda fetch exited with code ${code}`))));
    child.on('error', reject);
  });
}

async function runServe(options) {
  const runtime = resolveRuntime();
  if (runtime.strategy === 'cloud') {
    throw new Error(`Cloud endpoint already exists: ${runtime.cdpUrl}. A remote endpoint cannot be started with local serve.`);
  }

  const spec = buildLocalCommand('serve', {
    ...parseCommonOptions(options),
    host: options.host,
    port: options.port,
    timeout: options.timeout,
    cdpMaxConnections: options['cdp-max-connections'],
    cdpMaxPendingConnections: options['cdp-max-pending-connections'],
  });

  if (toBool(options['dry-run'])) {
    printSpec(spec);
    return;
  }

  const child = spawnCommand(spec);
  const signals = ['SIGINT', 'SIGTERM'];
  const forwardSignal = (signal) => {
    if (!child.killed) {
      child.kill(signal);
    }
  };

  for (const signal of signals) {
    process.on(signal, () => forwardSignal(signal));
  }

  await new Promise((resolve, reject) => {
    child.on('exit', (code, signal) => {
      if (signal || code === 0) {
        resolve();
        return;
      }
      reject(new Error(`Lightpanda serve exited with code ${code}`));
    });
    child.on('error', reject);
  });
}

async function runMcp(options) {
  const runtime = resolveRuntime();
  if (runtime.strategy === 'cloud') {
    throw new Error(`Use remote MCP endpoint directly: ${runtime.mcpUrl}`);
  }

  const spec = buildLocalCommand('mcp', parseCommonOptions(options));
  if (toBool(options['dry-run'])) {
    printSpec(spec);
    return;
  }

  const child = spawnCommand(spec);
  await new Promise((resolve, reject) => {
    child.on('exit', (code) => (code === 0 ? resolve() : reject(new Error(`Lightpanda mcp exited with code ${code}`))));
    child.on('error', reject);
  });
}

async function main() {
  const [subcommand, ...rest] = process.argv.slice(2);
  if (!subcommand || subcommand === '--help' || subcommand === 'help') {
    printUsage();
    return;
  }

  if (subcommand === 'describe') {
    console.log(JSON.stringify(resolveRuntime(), null, 2));
    return;
  }

  const { options, positionals } = parseCliArgs(rest);

  if (subcommand === 'fetch') {
    await runFetch(options, positionals);
    return;
  }

  if (subcommand === 'serve') {
    await runServe(options);
    return;
  }

  if (subcommand === 'mcp') {
    await runMcp(options);
    return;
  }

  throw new Error(`Unknown subcommand: ${subcommand}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
