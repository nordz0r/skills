#!/usr/bin/env node

const fs = require('fs');
const net = require('net');
const os = require('os');
const path = require('path');
const { spawn, spawnSync } = require('child_process');

const DEFAULT_DOCKER_IMAGE = process.env.LIGHTPANDA_DOCKER_IMAGE || 'lightpanda/browser:nightly';
const DEFAULT_HOST = process.env.LIGHTPANDA_HOST || '127.0.0.1';
const DEFAULT_PORT = parseInt(process.env.LIGHTPANDA_PORT || '9222', 10);
const DEFAULT_TIMEOUT = parseInt(process.env.LIGHTPANDA_TIMEOUT || '10', 10);
const DEFAULT_CLOUD_REGION = process.env.LIGHTPANDA_CLOUD_REGION || 'euwest';

function isWSL() {
  if (process.platform !== 'linux') {
    return false;
  }

  if (process.env.WSL_DISTRO_NAME || process.env.WSL_INTEROP) {
    return true;
  }

  try {
    return fs.readFileSync('/proc/version', 'utf8').toLowerCase().includes('microsoft');
  } catch {
    return false;
  }
}

function commandExists(command) {
  const checker = process.platform === 'win32' ? 'where' : 'which';
  const result = spawnSync(checker, [command], { stdio: 'ignore' });
  return result.status === 0;
}

function deriveCloudUrls() {
  const token = process.env.LIGHTPANDA_TOKEN;
  if (!token) {
    return { cdpUrl: null, mcpUrl: null };
  }

  const region = DEFAULT_CLOUD_REGION;
  return {
    cdpUrl: `wss://${region}.cloud.lightpanda.io/ws?token=${encodeURIComponent(token)}`,
    mcpUrl: `https://${region}.cloud.lightpanda.io/mcp/sse?token=${encodeURIComponent(token)}`,
  };
}

function resolveBinaryPath() {
  const envPath = process.env.LIGHTPANDA_BIN;
  if (envPath) {
    return envPath;
  }

  if (commandExists('lightpanda')) {
    return 'lightpanda';
  }

  if (process.platform === 'win32' && commandExists('lightpanda.exe')) {
    return 'lightpanda.exe';
  }

  return null;
}

function resolveRuntime() {
  const platform = process.platform;
  const wsl = isWSL();
  const binaryPath = resolveBinaryPath();
  const envCdpUrl = process.env.LIGHTPANDA_CDP_URL || null;
  const envMcpUrl = process.env.LIGHTPANDA_MCP_URL || null;
  const derivedCloud = deriveCloudUrls();
  const cdpUrl = envCdpUrl || derivedCloud.cdpUrl;
  const mcpUrl = envMcpUrl || derivedCloud.mcpUrl;
  const dockerAvailable = commandExists('docker');

  let strategy = 'unavailable';
  let reason = 'No Lightpanda binary, Docker runtime, or cloud endpoint was found.';

  if (envCdpUrl || envMcpUrl) {
    strategy = 'cloud';
    reason = 'Using explicit Lightpanda cloud endpoint from environment variables.';
  } else if (binaryPath) {
    strategy = 'binary';
    reason = 'Using Lightpanda binary from LIGHTPANDA_BIN or PATH.';
  } else if (dockerAvailable) {
    strategy = 'docker';
    reason = 'Using Docker image for local Lightpanda runtime.';
  } else if (cdpUrl || mcpUrl) {
    strategy = 'cloud';
    reason = 'Using derived Lightpanda cloud endpoint from LIGHTPANDA_TOKEN.';
  }

  return {
    platform,
    isWSL: wsl,
    tempDir: os.tmpdir(),
    strategy,
    reason,
    binaryPath,
    dockerImage: DEFAULT_DOCKER_IMAGE,
    dockerAvailable,
    defaultHost: DEFAULT_HOST,
    defaultPort: DEFAULT_PORT,
    defaultTimeoutSeconds: DEFAULT_TIMEOUT,
    cdpUrl,
    mcpUrl,
  };
}

function normalizeFlag(flag) {
  return flag.replace(/_/g, '-').replace(/^--/, '');
}

function addFlagArgs(target, options, mappings) {
  for (const mapping of mappings) {
    const rawValue = options[mapping.key];
    if (rawValue === undefined || rawValue === null || rawValue === false || rawValue === '') {
      continue;
    }

    const name = `--${mapping.flag || mapping.key.replace(/[A-Z]/g, (match) => `_${match.toLowerCase()}`)}`;
    if (rawValue === true) {
      target.push(name);
      continue;
    }

    target.push(name, String(rawValue));
  }
}

function buildLocalCommand(subcommand, options = {}) {
  const runtime = resolveRuntime();
  const host = options.host || runtime.defaultHost;
  const port = options.port || runtime.defaultPort;
  const args = [subcommand];

  if (subcommand === 'fetch') {
    addFlagArgs(args, options, [
      { key: 'dump', flag: 'dump' },
      { key: 'stripMode', flag: 'strip_mode' },
      { key: 'withBase', flag: 'with_base' },
      { key: 'withFrames', flag: 'with_frames' },
      { key: 'obeyRobots', flag: 'obey_robots' },
      { key: 'httpProxy', flag: 'http_proxy' },
      { key: 'proxyBearerToken', flag: 'proxy_bearer_token' },
      { key: 'httpMaxConcurrent', flag: 'http_max_concurrent' },
      { key: 'httpMaxHostOpen', flag: 'http_max_host_open' },
      { key: 'httpTimeout', flag: 'http_timeout' },
      { key: 'httpConnectTimeout', flag: 'http_connect_timeout' },
      { key: 'httpMaxResponseSize', flag: 'http_max_response_size' },
      { key: 'insecureDisableTlsHostVerification', flag: 'insecure_disable_tls_host_verification' },
      { key: 'logLevel', flag: 'log_level' },
      { key: 'logFormat', flag: 'log_format' },
      { key: 'userAgentSuffix', flag: 'user_agent_suffix' },
    ]);
    args.push(options.url);
  } else if (subcommand === 'serve') {
    addFlagArgs(args, {
      host,
      port,
      timeout: options.timeout || runtime.defaultTimeoutSeconds,
      cdpMaxConnections: options.cdpMaxConnections,
      cdpMaxPendingConnections: options.cdpMaxPendingConnections,
      obeyRobots: options.obeyRobots,
      httpProxy: options.httpProxy,
      proxyBearerToken: options.proxyBearerToken,
      httpMaxConcurrent: options.httpMaxConcurrent,
      httpMaxHostOpen: options.httpMaxHostOpen,
      httpTimeout: options.httpTimeout,
      httpConnectTimeout: options.httpConnectTimeout,
      httpMaxResponseSize: options.httpMaxResponseSize,
      insecureDisableTlsHostVerification: options.insecureDisableTlsHostVerification,
      logLevel: options.logLevel,
      logFormat: options.logFormat,
      userAgentSuffix: options.userAgentSuffix,
    }, [
      { key: 'host', flag: 'host' },
      { key: 'port', flag: 'port' },
      { key: 'timeout', flag: 'timeout' },
      { key: 'cdpMaxConnections', flag: 'cdp_max_connections' },
      { key: 'cdpMaxPendingConnections', flag: 'cdp_max_pending_connections' },
      { key: 'obeyRobots', flag: 'obey_robots' },
      { key: 'httpProxy', flag: 'http_proxy' },
      { key: 'proxyBearerToken', flag: 'proxy_bearer_token' },
      { key: 'httpMaxConcurrent', flag: 'http_max_concurrent' },
      { key: 'httpMaxHostOpen', flag: 'http_max_host_open' },
      { key: 'httpTimeout', flag: 'http_timeout' },
      { key: 'httpConnectTimeout', flag: 'http_connect_timeout' },
      { key: 'httpMaxResponseSize', flag: 'http_max_response_size' },
      { key: 'insecureDisableTlsHostVerification', flag: 'insecure_disable_tls_host_verification' },
      { key: 'logLevel', flag: 'log_level' },
      { key: 'logFormat', flag: 'log_format' },
      { key: 'userAgentSuffix', flag: 'user_agent_suffix' },
    ]);
  } else if (subcommand === 'mcp') {
    addFlagArgs(args, options, [
      { key: 'obeyRobots', flag: 'obey_robots' },
      { key: 'httpProxy', flag: 'http_proxy' },
      { key: 'proxyBearerToken', flag: 'proxy_bearer_token' },
      { key: 'httpMaxConcurrent', flag: 'http_max_concurrent' },
      { key: 'httpMaxHostOpen', flag: 'http_max_host_open' },
      { key: 'httpTimeout', flag: 'http_timeout' },
      { key: 'httpConnectTimeout', flag: 'http_connect_timeout' },
      { key: 'httpMaxResponseSize', flag: 'http_max_response_size' },
      { key: 'insecureDisableTlsHostVerification', flag: 'insecure_disable_tls_host_verification' },
      { key: 'logLevel', flag: 'log_level' },
      { key: 'logFormat', flag: 'log_format' },
      { key: 'userAgentSuffix', flag: 'user_agent_suffix' },
    ]);
  }

  if (Array.isArray(options.extraArgs) && options.extraArgs.length > 0) {
    args.push(...options.extraArgs);
  }

  if (runtime.strategy === 'binary') {
    return {
      runtime,
      command: runtime.binaryPath,
      args,
      env: { ...process.env, LIGHTPANDA_DISABLE_TELEMETRY: process.env.LIGHTPANDA_DISABLE_TELEMETRY || 'true' },
    };
  }

  if (runtime.strategy === 'docker') {
    const dockerArgs = ['run', '--rm'];
    if (subcommand === 'serve') {
      dockerArgs.push('-p', `${host}:${port}:${port}`);
    }
    if (subcommand === 'mcp') {
      dockerArgs.push('-i');
    }
    dockerArgs.push('-e', `LIGHTPANDA_DISABLE_TELEMETRY=${process.env.LIGHTPANDA_DISABLE_TELEMETRY || 'true'}`);
    dockerArgs.push(runtime.dockerImage, subcommand);

    if (subcommand === 'serve') {
      const dockerServeArgs = args.slice(1).map((value, index, input) => {
        if (input[index - 1] === '--host') {
          return '0.0.0.0';
        }
        return value;
      });
      dockerArgs.push(...dockerServeArgs);
    } else {
      dockerArgs.push(...args.slice(1));
    }

    return {
      runtime,
      command: 'docker',
      args: dockerArgs,
      env: { ...process.env },
    };
  }

  throw new Error(`Lightpanda local command is unavailable. ${runtime.reason}`);
}

function spawnCommand(spec, spawnOptions = {}) {
  return spawn(spec.command, spec.args, {
    cwd: spawnOptions.cwd || process.cwd(),
    env: spec.env || process.env,
    stdio: spawnOptions.stdio || 'inherit',
    shell: false,
  });
}

function waitForPort(host, port, timeoutMs) {
  const startedAt = Date.now();

  return new Promise((resolve, reject) => {
    function attempt() {
      const socket = net.createConnection({ host, port });
      socket.once('connect', () => {
        socket.end();
        resolve();
      });
      socket.once('error', () => {
        socket.destroy();
        if (Date.now() - startedAt >= timeoutMs) {
          reject(new Error(`Timed out waiting for ${host}:${port}`));
          return;
        }
        setTimeout(attempt, 250);
      });
    }

    attempt();
  });
}

function toWebSocketUrl(host, port) {
  return `ws://${host}:${port}`;
}

function parseCliArgs(argv) {
  const options = {};
  const positionals = [];

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (!value.startsWith('--')) {
      positionals.push(value);
      continue;
    }

    const stripped = normalizeFlag(value);
    const next = argv[index + 1];
    if (!next || next.startsWith('--')) {
      options[stripped] = true;
      continue;
    }

    options[stripped] = next;
    index += 1;
  }

  return { options, positionals };
}

function makeTempTaskPath(name = 'lightpanda-task.js') {
  return path.join(os.tmpdir(), name);
}

module.exports = {
  DEFAULT_CLOUD_REGION,
  DEFAULT_DOCKER_IMAGE,
  DEFAULT_HOST,
  DEFAULT_PORT,
  DEFAULT_TIMEOUT,
  addFlagArgs,
  buildLocalCommand,
  commandExists,
  deriveCloudUrls,
  isWSL,
  makeTempTaskPath,
  normalizeFlag,
  parseCliArgs,
  resolveRuntime,
  spawnCommand,
  toWebSocketUrl,
  waitForPort,
};
