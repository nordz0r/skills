// Record an animated (SMIL) SVG into PNG frames, deterministically.
// usage: node record.mjs <in.svg> <framesDir> <seconds> <fps> <cssWidth> [bg]
import { chromium } from 'playwright';
import fs from 'node:fs';
const [, , svg, out, secs, fps, width, bg = '#0d1117'] = process.argv;
if (!svg || !out || !secs || !fps || !width) { console.error('usage: node record.mjs in.svg framesDir seconds fps cssWidth [bg]'); process.exit(2); }
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +width, height: 400 }, deviceScaleFactor: 2 });
await page.setContent(`<html><body style="margin:0;background:${bg}">${fs.readFileSync(svg, 'utf8')}</body></html>`);
const h = await page.evaluate((w) => {
  const s = document.querySelector('svg'); const vb = s.viewBox.baseVal;
  const h = Math.round(w * vb.height / vb.width);
  s.setAttribute('width', w); s.setAttribute('height', h); s.style.display = 'block';
  s.pauseAnimations(); return h;
}, +width);
await page.setViewportSize({ width: +width, height: h });
const n = Math.round(+secs * +fps);
for (let i = 0; i < n; i++) {
  await page.evaluate((t) => document.querySelector('svg').setCurrentTime(t), i / +fps);
  await page.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.png` });
}
await browser.close();
