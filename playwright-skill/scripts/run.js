#!/usr/bin/env node
/**
 * Universal Playwright Executor for standalone skills
 *
 * Executes Playwright automation code from:
 * - File path: node scripts/run.js /tmp/playwright-test-foo.js
 *
 * Ensures proper module resolution by running from skill directory.
 * Inline and stdin execution are intentionally disabled so the caller reviews
 * a concrete file before execution.
 */

const fs = require('fs');
const path = require('path');

const SKILL_ROOT = path.resolve(__dirname, '..');

// Change to skill root for proper module resolution and predictable cwd
process.chdir(SKILL_ROOT);

/**
 * Check if Playwright is installed
 */
function checkPlaywrightInstalled() {
  try {
    require.resolve('playwright');
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Get code to execute from various sources
 */
function getCodeToExecute() {
  const args = process.argv.slice(2);

  if (args.length !== 1 || !fs.existsSync(args[0])) {
    console.error('❌ This executor only accepts a reviewed script file path');
    console.error('Write your automation to /tmp/playwright-test-*.js and pass that file here');
    console.error('Usage:');
    console.error('  node scripts/run.js /tmp/playwright-test-page.js');
    process.exit(1);
  }

  const filePath = path.resolve(args[0]);
  console.log(`📄 Executing file: ${filePath}`);
  return fs.readFileSync(filePath, 'utf8');
}

/**
 * Clean up old temporary execution files from previous runs
 */
function cleanupOldTempFiles() {
  try {
    const files = fs.readdirSync(SKILL_ROOT);
    const tempFiles = files.filter(f => f.startsWith('.temp-execution-') && f.endsWith('.js'));

    if (tempFiles.length > 0) {
      tempFiles.forEach(file => {
        const filePath = path.join(SKILL_ROOT, file);
        try {
          fs.unlinkSync(filePath);
        } catch (e) {
          // Ignore errors - file might be in use or already deleted
        }
      });
    }
  } catch (e) {
    // Ignore directory read errors
  }
}

/**
 * Wrap code in async IIFE if not already wrapped
 */
function wrapCodeIfNeeded(code) {
  // Check if code already has require() and async structure
  const hasRequire = code.includes('require(');
  const hasAsyncIIFE = code.includes('(async () => {') || code.includes('(async()=>{');

  // If it's already a complete script, return as-is
  if (hasRequire && hasAsyncIIFE) {
    return code;
  }

  // If it's just Playwright commands, wrap in full template
  if (!hasRequire) {
    return `
const { chromium, firefox, webkit, devices } = require('playwright');
const helpers = require('./scripts/lib/helpers');

// Extra headers from environment variables (if configured)
const __extraHeaders = helpers.getExtraHeadersFromEnv();

/**
 * Utility to merge environment headers into context options.
 * Use when creating contexts with raw Playwright API instead of helpers.createContext().
 * @param {Object} options - Context options
 * @returns {Object} Options with extraHTTPHeaders merged in
 */
function getContextOptionsWithHeaders(options = {}) {
  if (!__extraHeaders) return options;
  return {
    ...options,
    extraHTTPHeaders: {
      ...__extraHeaders,
      ...(options.extraHTTPHeaders || {})
    }
  };
}

(async () => {
  try {
    ${code}
  } catch (error) {
    console.error('❌ Automation error:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
})();
`;
  }

  // If has require but no async wrapper
  if (!hasAsyncIIFE) {
    return `
(async () => {
  try {
    ${code}
  } catch (error) {
    console.error('❌ Automation error:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
})();
`;
  }

  return code;
}

/**
 * Main execution
 */
async function main() {
  console.log('🎭 Playwright Skill - Universal Executor\n');

  // Clean up old temp files from previous runs
  cleanupOldTempFiles();

  if (!checkPlaywrightInstalled()) {
    console.error('❌ Playwright is not installed in this skill directory');
    console.error('Run manual setup first:');
    console.error(`  cd ${SKILL_ROOT} && npm run setup`);
    process.exit(1);
  }

  // Get code to execute
  const rawCode = getCodeToExecute();
  const code = wrapCodeIfNeeded(rawCode);

  // Create temporary file for execution
  const tempFile = path.join(SKILL_ROOT, `.temp-execution-${Date.now()}.js`);

  try {
    // Write code to temp file
    fs.writeFileSync(tempFile, code, 'utf8');

    // Execute the code
    console.log('🚀 Starting automation...\n');
    require(tempFile);

    // Note: Temp file will be cleaned up on next run
    // This allows long-running async operations to complete safely

  } catch (error) {
    console.error('❌ Execution failed:', error.message);
    if (error.stack) {
      console.error('\n📋 Stack trace:');
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Run main function
main().catch(error => {
  console.error('❌ Fatal error:', error.message);
  process.exit(1);
});
