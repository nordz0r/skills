#!/usr/bin/env node

/**
 * Validates the repository structure for:
 * 1. Claude Code Marketplace & Plugin specifications (.claude-plugin/marketplace.json & plugin.json)
 * 2. SKILL.md YAML frontmatter validity and completeness
 * 3. agents/openai.yaml existence and schema
 *
 * Usage:
 *   node scripts/validate-skills.js
 *   node scripts/validate-skills.js --generate-openai-yaml
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const CLAUDE_PLUGIN_DIR = path.join(ROOT_DIR, '.claude-plugin');
const MARKETPLACE_JSON_PATH = path.join(CLAUDE_PLUGIN_DIR, 'marketplace.json');
const PLUGIN_JSON_PATH = path.join(CLAUDE_PLUGIN_DIR, 'plugin.json');
const CODEX_SYNC_SCRIPT = path.join(ROOT_DIR, 'scripts', 'sync-codex-plugins.js');

const generateOpenAiYaml = process.argv.includes('--generate-openai-yaml');

let errorCount = 0;
let warningCount = 0;

function logError(msg) {
  console.error(`❌ ERROR: ${msg}`);
  errorCount++;
}

function logWarn(msg) {
  console.warn(`⚠️  WARN: ${msg}`);
  warningCount++;
}

function logOk(msg) {
  console.log(`✅ OK: ${msg}`);
}

// 1. Discover all skill directories (directories containing SKILL.md)
const entries = fs.readdirSync(ROOT_DIR, { withFileTypes: true });
const skillDirs = entries
  .filter(e => e.isDirectory() && !e.name.startsWith('.') && e.name !== 'node_modules' && e.name !== 'scripts' && e.name !== 'tools' && e.name !== 'experiments')
  .filter(e => fs.existsSync(path.join(ROOT_DIR, e.name, 'SKILL.md')))
  .map(e => e.name)
  .sort();

console.log(`\n🔍 Found ${skillDirs.length} skill directories with SKILL.md\n`);

// 2. Validate SKILL.md frontmatter for all skills
const skillMetadata = new Map();

for (const dir of skillDirs) {
  const skillMdPath = path.join(ROOT_DIR, dir, 'SKILL.md');
  const content = fs.readFileSync(skillMdPath, 'utf8');

  // Parse YAML frontmatter
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) {
    logError(`[${dir}] SKILL.md missing YAML frontmatter (---)`);
    continue;
  }

  const frontmatter = match[1];
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const descMatch = frontmatter.match(/^description:\s*(?:>|\|)?\s*\r?\n?\s*([^\r\n]+(?:\r?\n\s+[^\r\n]+)*)/m);

  if (!nameMatch) {
    logError(`[${dir}] SKILL.md frontmatter missing 'name'`);
  } else {
    const name = nameMatch[1].trim().replace(/^["']|["']$/g, '');
    if (name !== dir) {
      logWarn(`[${dir}] SKILL.md frontmatter name '${name}' differs from directory name '${dir}'`);
    }
  }

  if (!descMatch) {
    logError(`[${dir}] SKILL.md frontmatter missing 'description'`);
  } else {
    const description = descMatch[1].trim().replace(/^["']|["']$/g, '').replace(/\r?\n\s*/g, ' ');
    skillMetadata.set(dir, {
      name: nameMatch ? nameMatch[1].trim().replace(/^["']|["']$/g, '') : dir,
      description: description
    });
  }

  // 3. Check agents/openai.yaml
  const openaiYamlDir = path.join(ROOT_DIR, dir, 'agents');
  const openaiYamlPath = path.join(openaiYamlDir, 'openai.yaml');

  if (!fs.existsSync(openaiYamlPath)) {
    if (generateOpenAiYaml) {
      if (!fs.existsSync(openaiYamlDir)) {
        fs.mkdirSync(openaiYamlDir, { recursive: true });
      }
      const displayName = dir
        .split('-')
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');
      const desc = skillMetadata.get(dir)?.description || `${displayName} skill`;
      const shortDesc = desc.length > 80 ? desc.slice(0, 77) + '...' : desc;

      const yamlContent = `interface:\n  display_name: "${displayName}"\n  short_description: "${shortDesc.replace(/"/g, '\\"')}"\n  default_prompt: "Use $${dir} to assist with ${dir.replace(/-/g, ' ')} tasks."\n`;
      fs.writeFileSync(openaiYamlPath, yamlContent, 'utf8');
      logOk(`[${dir}] Generated agents/openai.yaml`);
    } else {
      logWarn(`[${dir}] Missing agents/openai.yaml (run with --generate-openai-yaml to create)`);
    }
  }
}

// 4. Validate .claude-plugin/marketplace.json
if (!fs.existsSync(MARKETPLACE_JSON_PATH)) {
  logError(`Marketplace manifest missing at ${MARKETPLACE_JSON_PATH}`);
} else {
  try {
    const mpRaw = fs.readFileSync(MARKETPLACE_JSON_PATH, 'utf8');
    const mp = JSON.parse(mpRaw);

    if (!mp.name) logError('marketplace.json missing top-level "name"');
    if (!mp.owner || !mp.owner.name) logError('marketplace.json missing "owner.name"');
    if (!Array.isArray(mp.plugins)) logError('marketplace.json missing "plugins" array');
    else {
      logOk(`marketplace.json parsed successfully (${mp.plugins.length} entries)`);
      for (const p of mp.plugins) {
        if (!p.name) logError(`Plugin entry missing "name": ${JSON.stringify(p)}`);
        if (!p.source) logError(`Plugin entry "${p.name}" missing "source"`);
        else if (typeof p.source === 'string') {
          const resolvedPath = path.resolve(ROOT_DIR, p.source);
          if (!fs.existsSync(resolvedPath)) {
            logError(`Plugin entry "${p.name}" source directory does not exist: ${p.source} (${resolvedPath})`);
          }
        }
      }
    }
  } catch (err) {
    logError(`marketplace.json is invalid JSON: ${err.message}`);
  }
}

// 5. Validate .claude-plugin/plugin.json
if (!fs.existsSync(PLUGIN_JSON_PATH)) {
  logError(`Plugin manifest missing at ${PLUGIN_JSON_PATH}`);
} else {
  try {
    const pRaw = fs.readFileSync(PLUGIN_JSON_PATH, 'utf8');
    const p = JSON.parse(pRaw);

    if (!p.name) logError('plugin.json missing top-level "name"');
    if (!Array.isArray(p.skills)) logError('plugin.json missing "skills" array');
    else {
      logOk(`plugin.json parsed successfully (${p.skills.length} skills listed)`);
      for (const s of p.skills) {
        const resolvedPath = path.resolve(ROOT_DIR, s);
        if (!fs.existsSync(resolvedPath)) {
          logError(`plugin.json skill path does not exist: ${s}`);
        }
      }
    }
  } catch (err) {
    logError(`plugin.json is invalid JSON: ${err.message}`);
  }
}

// 6. Validate generated Codex plugin layout (.agents/plugins + plugins/)
if (!fs.existsSync(CODEX_SYNC_SCRIPT)) {
  logWarn(`Codex sync script missing at ${CODEX_SYNC_SCRIPT}`);
} else {
  try {
    execSync('node scripts/sync-codex-plugins.js --check', {
      cwd: ROOT_DIR,
      stdio: 'pipe',
    });
    logOk('Codex plugin layout (.agents/plugins + plugins/) is in sync with marketplace.json');
  } catch (err) {
    const details = (err.stdout || '').toString().trim();
    logError(`Codex plugin layout out of sync with marketplace.json — run: node scripts/sync-codex-plugins.js${details ? `\n         ${details.split('\n').join('\n         ')}` : ''}`);
  }
}

console.log('\n----------------------------------------');
console.log(`Validation finished: ${errorCount} errors, ${warningCount} warnings`);
console.log('----------------------------------------\n');

if (errorCount > 0) {
  process.exit(1);
}
