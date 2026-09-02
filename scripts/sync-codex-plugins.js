#!/usr/bin/env node

/**
 * Generates the Codex plugin layout from .claude-plugin/marketplace.json
 * (single source of truth for bundle grouping).
 *
 * Codex (ChatGPT plugins) requires a different structure than Claude Code:
 * - Repo marketplace:  .agents/plugins/marketplace.json
 * - Each plugin dir:   .codex-plugin/plugin.json  (manifest)
 * - Skills inside:     <plugin>/skills/<skill-name>/SKILL.md
 *
 * This script materializes plugin dirs under plugins/<bundle>/ with skill
 * folders copied from the repo root (node_modules/.venv/tmp never leak in).
 * Re-run after changing any skill or bundle; generated dirs are wiped on
 * each sync, so never hand-edit files under plugins/.
 *
 * Usage:
 *   node scripts/sync-codex-plugins.js            # sync plugins/ + marketplace
 *   node scripts/sync-codex-plugins.js --check    # exit 1 if out of sync (CI)
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const MARKETPLACE_SRC = path.join(ROOT_DIR, '.claude-plugin', 'marketplace.json');
const AGENTS_PLUGINS_DIR = path.join(ROOT_DIR, '.agents', 'plugins');
const CODEX_MARKETPLACE_PATH = path.join(AGENTS_PLUGINS_DIR, 'marketplace.json');
const PLUGINS_OUT_DIR = path.join(ROOT_DIR, 'plugins');
const PLUGIN_MANIFEST_DIR = '.codex-plugin';
const PLUGIN_MANIFEST_NAME = 'plugin.json';

const checkOnly = process.argv.includes('--check');

const marketplace = JSON.parse(fs.readFileSync(MARKETPLACE_SRC, 'utf8'));

const CATEGORY_TO_CODEX = {
  bundle: 'Productivity',
  engineering: 'Developer Tools',
  infrastructure: 'Developer Tools',
  'ai-tools': 'Productivity',
  networking: 'Developer Tools',
  design: 'Design & Creative',
};

// Skill layout constants: known skill subdirectories copied wholesale, unknown
// top-level files with code/doc/config extensions copied as-is (so playwright-
// skill's run.js and atlassian's requirements.txt keep working). Everything
// else is skipped to avoid junk leakage into plugins/.
const COPY_DIRS = new Set(['references', 'scripts', 'agents', 'evals', 'assets', 'lib']);
const COPY_FILES = new Set(['SKILL.md', 'package.json', 'package-lock.json', 'requirements.txt', '.env.example']);
const COPY_EXTRA = new Set(['.js', '.mjs', '.cjs', '.sh', '.md']);
const SKIP_DIRS = new Set(['node_modules', '__pycache__', '.venv', 'tmp']);

function discoverSkillDirs() {
  const skillsByDir = new Map();
  const excluded = new Set(['scripts', 'tools', 'experiments', 'plugins', 'node_modules']);
  for (const entry of fs.readdirSync(ROOT_DIR, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith('.') || excluded.has(entry.name)) continue;
    if (fs.existsSync(path.join(ROOT_DIR, entry.name, 'SKILL.md'))) {
      skillsByDir.set(entry.name, path.join(ROOT_DIR, entry.name));
    }
  }
  return skillsByDir;
}

function copyDirSync(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDirSync(s, d);
    else fs.copyFileSync(s, d);
  }
}

function copySkill(skillPath, destSkillDir) {
  const src = path.join(ROOT_DIR, skillPath);
  fs.mkdirSync(destSkillDir, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    // Explicit allowlist wins over the dotfile rule (e.g. .env.example).
    const allowed = COPY_FILES.has(entry.name);
    if (!allowed && (entry.name.startsWith('.') || SKIP_DIRS.has(entry.name))) continue;
    const s = path.join(src, entry.name);
    const d = path.join(destSkillDir, entry.name);
    if (entry.isDirectory()) {
      if (COPY_DIRS.has(entry.name)) copyDirSync(s, d);
      continue;
    }
    if (allowed || COPY_EXTRA.has(path.extname(entry.name))) {
      fs.copyFileSync(s, d);
    }
  }
}

// Expand a Claude marketplace entry into a Codex bundle definition.
// source "./" with no skills[] list (e.g. "all-skills") means the full set.
function resolveBundles(skillsByDir) {
  const allSkillNames = [...skillsByDir.keys()].sort();
  const bundles = marketplace.plugins
    .filter((p) => p.source === './')
    .map((p) => ({
      ...p,
      skillNames: Array.isArray(p.skills)
        ? p.skills.map((s) => s.replace(/^\.\//, ''))
        : allSkillNames,
    }));

  for (const bundle of bundles) {
    for (const skillName of bundle.skillNames) {
      if (!skillsByDir.has(skillName)) {
        console.error(`❌ ERROR: bundle "${bundle.name}" references skill "${skillName}" but ./${skillName}/SKILL.md is missing`);
        process.exit(1);
      }
    }
  }
  return bundles;
}

function buildCodexMarketplace(bundles) {
  return {
    name: marketplace.name,
    interface: { displayName: 'NorD Skills' },
    plugins: bundles.map((bundle) => ({
      name: bundle.name,
      source: {
        source: 'local',
        path: `./plugins/${bundle.name}`,
      },
      policy: {
        installation: 'AVAILABLE',
        authentication: 'ON_INSTALL',
      },
      category: CATEGORY_TO_CODEX[bundle.category] || 'Productivity',
      interface: {
        displayName: bundle.displayName || bundle.name,
      },
    })),
  };
}

function buildPluginManifest(bundle) {
  const author = marketplace.owner || { name: 'NorD', url: 'https://github.com/nordz0r/skills' };
  const homepage = author.url || 'https://github.com/nordz0r/skills';
  return {
    name: bundle.name,
    version: bundle.version || marketplace.version || '1.0.0',
    description: bundle.description,
    author: { name: author.name, url: author.url },
    homepage,
    repository: homepage,
    license: 'MIT',
    keywords: bundle.tags || [],
    skills: './skills/',
    interface: {
      displayName: bundle.displayName || bundle.name,
      shortDescription: bundle.description,
      longDescription: bundle.description,
      developerName: author.name,
      category: CATEGORY_TO_CODEX[bundle.category] || 'Productivity',
      capabilities: ['Read'],
      websiteURL: homepage,
    },
  };
}

// Render the exact bytes the sync would write for a given bundle.
function renderPluginManifest(bundle) {
  return JSON.stringify(buildPluginManifest(bundle), null, 2) + '\n';
}

// ---- main -----------------------------------------------------------------

const skillsByDir = discoverSkillDirs();
const bundles = resolveBundles(skillsByDir);
const codexMarketplace = buildCodexMarketplace(bundles);
const expectedMarketplace = JSON.stringify(codexMarketplace, null, 2) + '\n';

let hasDiff = false;

if (checkOnly) {
  // Compare expected marketplace + manifests against what is on disk.
  const actualMarketplace = fs.existsSync(CODEX_MARKETPLACE_PATH)
    ? fs.readFileSync(CODEX_MARKETPLACE_PATH, 'utf8')
    : null;
  if (actualMarketplace !== expectedMarketplace) {
    hasDiff = true;
    console.error('❌ .agents/plugins/marketplace.json is out of date — run: node scripts/sync-codex-plugins.js');
  }
  for (const bundle of bundles) {
    const manifestPath = path.join(PLUGINS_OUT_DIR, bundle.name, PLUGIN_MANIFEST_DIR, PLUGIN_MANIFEST_NAME);
    const actual = fs.existsSync(manifestPath) ? fs.readFileSync(manifestPath, 'utf8') : null;
    if (actual !== renderPluginManifest(bundle)) {
      hasDiff = true;
      console.error(`❌ ${manifestPath} is missing or out of date — run: node scripts/sync-codex-plugins.js`);
    }
    for (const skillName of bundle.skillNames) {
      const destSkillDir = path.join(PLUGINS_OUT_DIR, bundle.name, 'skills', skillName);
      const srcSkillDir = skillsByDir.get(skillName);
      if (!skillsMatch(srcSkillDir, destSkillDir)) {
        hasDiff = true;
        console.error(`❌ ${destSkillDir} is missing or out of date — run: node scripts/sync-codex-plugins.js`);
        break; // one message per bundle is enough
      }
    }
  }
  if (hasDiff) process.exit(1);
  console.log(`✅ Codex plugin layout in sync (${bundles.length} bundles, ${bundles.reduce((n, b) => n + b.skillNames.length, 0)} skill copies)`);
  process.exit(0);
}

// Wipe generated plugin dirs — they are fully derived artifacts.
fs.rmSync(PLUGINS_OUT_DIR, { recursive: true, force: true });
fs.mkdirSync(PLUGINS_OUT_DIR, { recursive: true });
fs.mkdirSync(AGENTS_PLUGINS_DIR, { recursive: true });

for (const bundle of bundles) {
  const outDir = path.join(PLUGINS_OUT_DIR, bundle.name);
  fs.mkdirSync(path.join(outDir, PLUGIN_MANIFEST_DIR), { recursive: true });
  fs.mkdirSync(path.join(outDir, 'skills'), { recursive: true });

  for (const skillName of bundle.skillNames) {
    copySkill(path.join(skillName), path.join(outDir, 'skills', skillName));
  }

  fs.writeFileSync(
    path.join(outDir, PLUGIN_MANIFEST_DIR, PLUGIN_MANIFEST_NAME),
    renderPluginManifest(bundle)
  );
}

fs.writeFileSync(CODEX_MARKETPLACE_PATH, expectedMarketplace);

console.log('\n📦 Codex plugin sync complete');
console.log(`   Bundles: ${bundles.map((b) => b.name).join(', ')}`);
console.log(`   Marketplace: ${path.relative(ROOT_DIR, CODEX_MARKETPLACE_PATH)}`);
console.log('\nNext steps:');
console.log('  1. Commit and push:  git add .agents/plugins plugins && git commit');
console.log('  2. Install in Codex: codex plugin marketplace add nordz0r/skills');

// Directory-content equality: every source file exists in dest with identical
// bytes and no extra dest files, applying the same copy rules as copySkill.
function skillsMatch(srcDir, destDir) {
  if (!fs.existsSync(destDir)) return false;
  const srcEntries = fs.readdirSync(srcDir, { withFileTypes: true })
    .filter((e) => {
      const allowed = COPY_FILES.has(e.name);
      if (!allowed && (e.name.startsWith('.') || SKIP_DIRS.has(e.name))) return false;
      return e.isDirectory() ? COPY_DIRS.has(e.name) : (allowed || COPY_EXTRA.has(path.extname(e.name)));
    })
    .map((e) => e.name)
    .sort();
  const destEntries = fs.readdirSync(destDir).sort();
  if (srcEntries.join(',') !== destEntries.join(',')) return false;
  for (const name of srcEntries) {
    const s = path.join(srcDir, name);
    const d = path.join(destDir, name);
    if (fs.statSync(s).isDirectory()) {
      if (!copyDirSyncMatch(s, d)) return false;
    } else if (!fs.readFileSync(s).equals(fs.readFileSync(d))) {
      return false;
    }
  }
  return true;
}

function copyDirSyncMatch(srcDir, destDir) {
  if (!fs.existsSync(destDir)) return false;
  const srcEntries = fs.readdirSync(srcDir, { withFileTypes: true })
    .filter((e) => !SKIP_DIRS.has(e.name))
    .map((e) => e.name)
    .sort();
  const destEntries = fs.readdirSync(destDir).sort();
  if (srcEntries.join(',') !== destEntries.join(',')) return false;
  for (const name of srcEntries) {
    const s = path.join(srcDir, name);
    const d = path.join(destDir, name);
    if (fs.statSync(s).isDirectory()) {
      if (!copyDirSyncMatch(s, d)) return false;
    } else if (!fs.readFileSync(s).equals(fs.readFileSync(d))) {
      return false;
    }
  }
  return true;
}
