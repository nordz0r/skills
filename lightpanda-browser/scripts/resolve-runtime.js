#!/usr/bin/env node

const { resolveRuntime } = require('./lib/runtime');

const runtime = resolveRuntime();

if (process.argv.includes('--json')) {
  process.stdout.write(`${JSON.stringify(runtime, null, 2)}\n`);
  process.exit(0);
}

console.log(`strategy: ${runtime.strategy}`);
console.log(`reason: ${runtime.reason}`);
console.log(`platform: ${runtime.platform}${runtime.isWSL ? ' (WSL)' : ''}`);
console.log(`binary: ${runtime.binaryPath || 'not found'}`);
console.log(`docker: ${runtime.dockerAvailable ? runtime.dockerImage : 'not found'}`);
console.log(`cdp: ${runtime.cdpUrl || 'not configured'}`);
console.log(`mcp: ${runtime.mcpUrl || 'not configured'}`);
