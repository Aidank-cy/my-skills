#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');

function requireDependency(name) {
  try {
    return require(name);
  } catch (error) {
    try {
      return createRequire(path.join(process.cwd(), 'package.json'))(name);
    } catch {
      throw error;
    }
  }
}

function usage() {
  console.error('Usage: node fetch-page.js <URL> <OUTPUT_HTML> [OUTPUT_TEXT]');
}

const [, , url, outputHtml, outputText] = process.argv;
if (!url || !outputHtml) {
  usage();
  process.exit(1);
}

const puppeteer = requireDependency('puppeteer');

async function fetchPage(targetUrl, htmlPath, textPath) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
    await page.setViewport({ width: 1280, height: 900 });

    try {
      await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });
    } catch {
      await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
    }

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await new Promise(resolve => setTimeout(resolve, 2000));
    await page.evaluate(() => window.scrollTo(0, 0));

    await page.evaluate(() => {
      document.querySelectorAll(
        '[class*="cookie"], [class*="consent"], [class*="popup"], ' +
        '[class*="overlay"], [class*="modal"], [class*="gdpr"], ' +
        '[class*="banner"], [id*="cookie"]'
      ).forEach(el => el.remove());
    });

    const html = await page.content();
    const articleText = await page.evaluate(() => {
      const article = document.querySelector('article') || document.querySelector('main') || document.body;
      return article ? article.innerText : '';
    });

    fs.writeFileSync(htmlPath, html);
    if (textPath) fs.writeFileSync(textPath, articleText);

    console.log(JSON.stringify({
      url: targetUrl,
      outputHtml: htmlPath,
      outputText: textPath || null,
      htmlBytes: Buffer.byteLength(html),
      articleTextChars: articleText.length
    }, null, 2));
  } finally {
    await browser.close();
  }
}

fetchPage(url, outputHtml, outputText).catch(error => {
  console.error(error.message);
  process.exit(1);
});
