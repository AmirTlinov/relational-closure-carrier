#!/usr/bin/env node
import { createRequire } from 'node:module';
import { existsSync } from 'node:fs';
import { isAbsolute, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const args = process.argv.slice(2);

if (!args.length || args.includes('--help') || args.includes('-h')) {
  console.log('Usage: print-atlas.mjs <atlas-dir> [output.pdf]');
  process.exit(args.length ? 0 : 2);
}

const atlasDir = resolve(args[0]);
const htmlPath = join(atlasDir, 'atlas.html');
const outputPath = args[1]
  ? (isAbsolute(args[1]) ? args[1] : resolve(atlasDir, args[1]))
  : join(atlasDir, 'atlas.pdf');

if (!existsSync(htmlPath)) {
  throw new Error(`Не найден владелец документа: ${htmlPath}`);
}

function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_PATH,
    'playwright-core',
    'playwright',
  ].filter(Boolean);

  const failures = [];
  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch (error) {
      failures.push(`${candidate}: ${error.code || error.message}`);
    }
  }
  throw new Error(`Playwright not found. Run npm ci --prefix theory or set PLAYWRIGHT_PATH.\n${failures.join('\n')}`);
}

const { chromium } = loadPlaywright();
const chromePath = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const launchCandidates = [];
if (process.env.CHROME_PATH) {
  launchCandidates.push({ label: `CHROME_PATH=${chromePath}`, options: { headless: true, executablePath: chromePath } });
} else {
  if (existsSync(chromePath)) {
    launchCandidates.push({ label: chromePath, options: { headless: true, executablePath: chromePath } });
  }
  launchCandidates.push({ label: 'bundled Chromium Playwright', options: { headless: true } });
}

let browser;
const launchFailures = [];
for (const candidate of launchCandidates) {
  try {
    browser = await chromium.launch(candidate.options);
    break;
  } catch (error) {
    launchFailures.push(`${candidate.label}: ${error.message}`);
  }
}

if (!browser) {
  const joined = launchFailures.join('\n\n');
  const permissionBoundary = /MachPort|bootstrap|sandbox|SIGABRT|signal=SIGABRT/i.test(joined);
  const nextStep = permissionBoundary
    ? 'Среда блокирует запуск браузера. Повторите ту же команду с разрешением запуска Chrome; HTML/CSS/SVG менять не нужно.'
    : 'Установите Chromium для Playwright либо задайте рабочий CHROME_PATH.';
  throw new Error(`Не удалось запустить Chromium. ${nextStep}\n\n${joined}`);
}
try {
  const page = await browser.newPage({ viewport: { width: 1190, height: 1684 }, deviceScaleFactor: 1 });
  const runtimeErrors = [];
  page.on('pageerror', (error) => runtimeErrors.push(error.message));

  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    await Promise.all([...document.images].map((img) => {
      if (img.complete && img.naturalWidth > 0) return undefined;
      return new Promise((resolve, reject) => {
        img.addEventListener('load', resolve, { once: true });
        img.addEventListener('error', () => reject(new Error(`Image failed: ${img.src}`)), { once: true });
      });
    }));
  });

  const contract = await page.evaluate(() => {
    const tolerance = 1;
    const sheets = [...document.querySelectorAll('.sheet')];
    const covers = sheets.filter((sheet) => sheet.classList.contains('cover'));
    const chapters = sheets.filter((sheet) => sheet.classList.contains('chapter'));
    const errors = [];

    if (covers.length !== 1) errors.push(`ожидалась одна обложка, найдено ${covers.length}`);
    if (chapters.length < 1) errors.push('нужна хотя бы одна содержательная глава');
    if (!covers[0]?.querySelector('.cover-illustration[alt]')) {
      errors.push('обложка не имеет растровой причинной иллюстрации с alt');
    }
    if (sheets.length !== covers.length + chapters.length) {
      errors.push('каждый .sheet должен быть .cover или .chapter');
    }

    chapters.forEach((sheet, index) => {
      const label = sheet.querySelector('.plate-no')?.textContent.trim() || `глава ${index + 1}`;
      const entries = sheet.querySelectorAll('.copy .entry').length;
      if (entries < 2 || entries > 4) errors.push(`${label}: смысловых шагов ${entries}, ожидалось 2–4`);
      if (!sheet.querySelector('.mast h2')) errors.push(`${label}: отсутствует тезис h2`);
      if (!sheet.querySelector('.verdict')) errors.push(`${label}: отсутствует .verdict`);
      const illustration = sheet.querySelector('.drawing .story-image');
      if (!illustration) errors.push(`${label}: отсутствует растровая причинная иллюстрация`);
      if (illustration && !illustration.getAttribute('alt')?.trim()) {
        errors.push(`${label}: иллюстрация не имеет alt`);
      }
      if (!sheet.querySelector('.folio-note')) errors.push(`${label}: отсутствует .folio-note`);
    });

    sheets.forEach((sheet, index) => {
      if (sheet.scrollWidth > sheet.clientWidth + tolerance || sheet.scrollHeight > sheet.clientHeight + tolerance) {
        errors.push(`лист ${index + 1}: переполнение ${sheet.scrollWidth}x${sheet.scrollHeight} при поле ${sheet.clientWidth}x${sheet.clientHeight}`);
      }
      for (const selector of ['.mast', '.copy', '.drawing', '.folio-note']) {
        const region = sheet.querySelector(selector);
        if (!region) continue;
        if (region.scrollWidth > region.clientWidth + tolerance || region.scrollHeight > region.clientHeight + tolerance) {
          errors.push(`лист ${index + 1} ${selector}: содержимое не помещается`);
        }
      }
    });

    return { sheets: sheets.length, chapters: chapters.length, errors };
  });

  contract.errors.push(...runtimeErrors.map((error) => `ошибка страницы: ${error}`));
  if (contract.errors.length) {
    throw new Error(`Контракт атласа нарушен:\n${contract.errors.join('\n')}`);
  }

  await page.pdf({
    path: outputPath,
    width: '210mm',
    height: '297mm',
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
    displayHeaderFooter: false,
    tagged: true,
    outline: true,
  });

  console.log(`PASS: ${contract.sheets} листов · ${contract.chapters} причинных глав · переполнения нет`);
  console.log(outputPath);
} finally {
  await browser.close();
}
