#!/usr/bin/env node
// Консервативная техническая проверка локальных HTML-артефактов.
// Не проверяет красоту, clipping, пересечения или намерение композиции.
// Usage: check_html.mjs <file.html | HTML_artifacts dir> [...]

import { execSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const WIDTHS = [390, 768, 1440];
const HORIZONTAL_SCROLL_TOLERANCE = 4;
const NETWORK_PROTOCOLS = new Set(['http:', 'https:', 'ws:', 'wss:']);

function loadPlaywright() {
  try {
    return require('playwright');
  } catch {
    try {
      const globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
      return require(path.join(globalRoot, 'playwright', 'index.js'));
    } catch {
      console.error('playwright не найден: нужен локальный или глобальный пакет (npm i -g playwright).');
      process.exit(2);
    }
  }
}

function protocolOf(url) {
  try {
    return new URL(url).protocol;
  } catch {
    return '';
  }
}

function collectTargets(args) {
  const files = [];
  for (const arg of args) {
    const target = path.resolve(arg);
    const stat = fs.statSync(target);
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(target).sort()) {
        if (entry.endsWith('.html') && !entry.startsWith('_')) {
          files.push(path.join(target, entry));
        }
      }
    } else if (target.endsWith('.html')) {
      files.push(target);
    }
  }
  return [...new Set(files)];
}

function unique(items) {
  return [...new Set(items)];
}

const args = process.argv.slice(2);
if (!args.length) {
  console.error('Usage: check_html.mjs <file.html | HTML_artifacts dir> [...]');
  process.exit(2);
}

const targets = collectTargets(args);
if (!targets.length) {
  console.error('HTML-файлы не найдены.');
  process.exit(2);
}

const { chromium } = loadPlaywright();
const browser = await chromium.launch();
let dirty = false;

try {
  for (const file of targets) {
    const findings = [];

    for (const width of WIDTHS) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      const runtimeErrors = [];
      const failedLocalRequests = [];
      const networkAttempts = [];

      page.on('pageerror', (error) => {
        runtimeErrors.push(`pageerror: ${error.message.slice(0, 140)}`);
      });
      page.on('console', (message) => {
        const isOwnedRequestError = message.text().startsWith('Failed to load resource:');
        if (message.type() === 'error' && !isOwnedRequestError) {
          runtimeErrors.push(`console: ${message.text().slice(0, 140)}`);
        }
      });
      page.on('requestfailed', (request) => {
        if (protocolOf(request.url()) === 'file:') {
          failedLocalRequests.push(request.url());
        }
      });
      page.on('request', (request) => {
        if (NETWORK_PROTOCOLS.has(protocolOf(request.url()))) {
          networkAttempts.push(request.url());
        }
      });
      page.on('websocket', (socket) => networkAttempts.push(socket.url()));

      try {
        await page.goto(pathToFileURL(file).href, { waitUntil: 'domcontentloaded' });
        await page.waitForTimeout(1200);

        const horizontalScroll = await page.evaluate((tolerance) => {
          const root = document.scrollingElement || document.documentElement;
          const startX = window.scrollX;
          const startY = window.scrollY;
          const previousBehavior = document.documentElement.style.scrollBehavior;
          document.documentElement.style.scrollBehavior = 'auto';
          window.scrollTo(root.scrollWidth, startY);
          const travel = window.scrollX;
          window.scrollTo(startX, startY);
          document.documentElement.style.scrollBehavior = previousBehavior;
          return travel > tolerance
            ? { travel, scrollWidth: root.scrollWidth, viewport: window.innerWidth }
            : null;
        }, HORIZONTAL_SCROLL_TOLERANCE);

        if (horizontalScroll) {
          findings.push(
            `[${width}px] page scrolls horizontally by ${horizontalScroll.travel}px ` +
            `(scrollWidth ${horizontalScroll.scrollWidth}, viewport ${horizontalScroll.viewport})`,
          );
        }
      } catch (error) {
        runtimeErrors.push(`navigation: ${error.message.slice(0, 140)}`);
      }

      for (const url of unique(failedLocalRequests)) {
        findings.push(`[${width}px] local request failed: ${url}`);
      }
      for (const url of unique(networkAttempts)) {
        findings.push(`[${width}px] forbidden network request: ${url}`);
      }
      for (const error of unique(runtimeErrors)) {
        findings.push(`[${width}px] ${error}`);
      }

      await page.close();
    }

    if (findings.length) {
      dirty = true;
      console.log(`\n✗ ${path.basename(file)} — ${findings.length}`);
      for (const finding of findings) console.log(`  ${finding}`);
    } else {
      console.log(`✓ ${path.basename(file)}`);
    }
  }
} finally {
  await browser.close();
}

process.exit(dirty ? 1 : 0);
