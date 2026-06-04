const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
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

const puppeteer = requireDependency('puppeteer');

const VISUAL_DUPLICATE_DISTANCE = 6;

function sha256(buffer) {
    return crypto.createHash('sha256').update(Buffer.from(buffer)).digest('hex');
}

function mimeFromExtension(ext) {
    const normalized = String(ext || '').toLowerCase().replace(/^\./, '');
    if (normalized === 'jpg' || normalized === 'jpeg') return 'image/jpeg';
    if (normalized === 'gif') return 'image/gif';
    if (normalized === 'webp') return 'image/webp';
    return 'image/png';
}

function normalizeSrc(src) {
    if (!src) return '';
    try {
        const parsed = new URL(src);
        parsed.hash = '';
        return parsed.toString();
    } catch {
        return src;
    }
}

function hammingDistance(a, b) {
    if (!a || !b || a.length !== b.length) return Infinity;
    let distance = 0;
    for (let i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) distance++;
    }
    return distance;
}

function slugify(value, fallback) {
    const safe = (value || fallback)
        .replace(/[^a-zA-Z0-9\u4e00-\u9fff-]/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '')
        .toLowerCase()
        .slice(0, 50);
    return safe || fallback;
}

function uniqueFilename(outputDir, filename) {
    const ext = path.extname(filename);
    const base = filename.slice(0, filename.length - ext.length);
    let candidate = filename;
    let counter = 2;
    while (fs.existsSync(path.join(outputDir, candidate))) {
        candidate = `${base}-${counter}${ext}`;
        counter++;
    }
    return candidate;
}

function findDuplicate(candidate, captured) {
    const candidateSrc = normalizeSrc(candidate.src);
    for (const existing of captured) {
        if (candidateSrc && normalizeSrc(existing.src) === candidateSrc) {
            return { existing, reason: 'same normalized source URL', distance: 0 };
        }
        if (candidate.sourceHash && existing.sourceHash === candidate.sourceHash) {
            return { existing, reason: 'same file hash', distance: 0 };
        }
        const distance = hammingDistance(candidate.visualHash, existing.visualHash);
        if (distance <= VISUAL_DUPLICATE_DISTANCE) {
            return { existing, reason: 'similar perceptual hash', distance };
        }
    }
    return null;
}

function removeCapturedFile(outputDir, entry) {
    if (!entry?.filename) return;
    try {
        fs.unlinkSync(path.join(outputDir, entry.filename));
    } catch { }
}

function withTimeout(promise, ms) {
    return Promise.race([
        promise,
        new Promise((_, reject) => setTimeout(() => reject(new Error(`timeout after ${ms}ms`)), ms))
    ]);
}

async function computeVisualHash(hashPage, buffer, mimeType = 'image/png') {
    const dataUrl = `data:${mimeType};base64,${Buffer.from(buffer).toString('base64')}`;
    try {
        return await hashPage.evaluate(async (src) => {
            const img = new Image();
            img.decoding = 'async';
            img.src = src;
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
            });

            const canvas = document.createElement('canvas');
            canvas.width = 8;
            canvas.height = 8;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, 8, 8);
            const pixels = ctx.getImageData(0, 0, 8, 8).data;
            const grays = [];
            for (let i = 0; i < pixels.length; i += 4) {
                grays.push((pixels[i] * 0.299) + (pixels[i + 1] * 0.587) + (pixels[i + 2] * 0.114));
            }
            const avg = grays.reduce((sum, value) => sum + value, 0) / grays.length;
            return grays.map(value => value >= avg ? '1' : '0').join('');
        }, dataUrl);
    } catch {
        return null;
    }
}

async function captureVisuals(url, outputDir) {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');

    try {
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    } catch (e) {
        console.error(`Navigation timeout, retrying with domcontentloaded`);
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
    }

    // Scroll fully to trigger lazy-loaded images
    await page.evaluate(async () => {
        const distance = 300;
        const delay = 200;
        while (document.scrollingElement.scrollTop + window.innerHeight
            < document.scrollingElement.scrollHeight) {
            document.scrollingElement.scrollBy(0, distance);
            await new Promise(r => setTimeout(r, delay));
        }
        window.scrollTo(0, 0);
    });
    await new Promise(r => setTimeout(r, 3000));

    // Remove cookie banners, popups, overlays
    await page.evaluate(() => {
        document.querySelectorAll(
            '[class*="cookie"], [class*="consent"], [class*="popup"], ' +
            '[class*="overlay"], [class*="modal"], [class*="gdpr"], ' +
            '[class*="banner"], [id*="cookie"]'
        ).forEach(el => el.remove());
    });

    fs.mkdirSync(outputDir, { recursive: true });
    const captured = [];
    const skippedDuplicates = [];
    const hashPage = await browser.newPage();

    // ── Strategy 1: Download meaningful <img> with full src resolution ──
    const contentSelectors = [
        'article', 'main', '.article-body', '.content',
        '#content', '.post-content', '.entry-content',
        '[role="main"]', '.article__body', '.article-content'
    ];

    const images = await page.evaluate((selectors) => {
        let container = null;
        for (const sel of selectors) {
            container = document.querySelector(sel);
            if (container) break;
        }
        if (!container) container = document.body;

        const results = [];
        container.querySelectorAll('img').forEach((img, i) => {
            let src = img.src || '';

            // data-src (lazy loading)
            if (!src || src === window.location.href || src === '') {
                src = img.getAttribute('data-src') || '';
            }

            // srcset on <img>
            if (!src) {
                const srcset = img.getAttribute('srcset') || '';
                if (srcset) {
                    const candidates = srcset.split(',').map(s => s.trim().split(/\s+/));
                    src = candidates[candidates.length - 1]?.[0] || '';
                }
            }

            // parent <picture><source>
            if (!src || src === window.location.href || src === '') {
                const picture = img.closest('picture');
                if (picture) {
                    for (const source of picture.querySelectorAll('source')) {
                        const srcset = source.getAttribute('srcset') || '';
                        if (srcset) {
                            const candidates = srcset.split(',').map(s => s.trim().split(/\s+/));
                            src = candidates[candidates.length - 1]?.[0] || '';
                            if (src) break;
                        }
                    }
                }
            }

            if (!src || src.startsWith('data:') || src.includes('tracking')
                || src.includes('pixel') || src === window.location.href) return;

            const w = img.naturalWidth || img.offsetWidth || 0;
            const h = img.naturalHeight || img.offsetHeight || 0;
            if (w < 100 && h < 100) return;

            const parentClass = (img.parentElement?.className || '').toLowerCase();
            const alt = (img.alt || '').toLowerCase();
            if ((parentClass.includes('author') || parentClass.includes('reviewer')
                || parentClass.includes('avatar') || alt.includes('portrait')
                || alt.includes('headshot')) && w < 300 && h < 300) return;

            results.push({ src, alt: img.alt || `figure-${i}`, width: w, height: h, index: i });
        });
        return results;
    }, contentSelectors);

    console.log(`Found ${images.length} meaningful images`);

    for (const img of images) {
        try {
            const imgPage = await browser.newPage();
            const response = await imgPage.goto(img.src, { timeout: 15000 });
            if (response && response.ok()) {
                const buffer = await response.buffer();
                if (buffer.length > 1024) {
                    const ext = (img.src.match(/\.(png|jpg|jpeg|gif|webp)/i) || ['', 'png'])[1];
                    const sourceHash = sha256(buffer);
                    const visualHash = await computeVisualHash(hashPage, buffer, mimeFromExtension(ext));
                    const duplicate = findDuplicate({
                        type: 'image',
                        src: img.src,
                        sourceHash,
                        visualHash
                    }, captured);
                    if (duplicate) {
                        skippedDuplicates.push({
                            type: 'image',
                            alt: img.alt,
                            src: img.src,
                            duplicateOf: duplicate.existing.filename,
                            reason: duplicate.reason,
                            distance: duplicate.distance
                        });
                        console.log(`↩️  Skipped duplicate image: ${img.alt || img.src} -> ${duplicate.existing.filename} (${duplicate.reason})`);
                        await imgPage.close();
                        continue;
                    }

                    const safeName = slugify(img.alt, `figure-${img.index}`);
                    const filename = uniqueFilename(outputDir, `${safeName}.${ext}`);
                    fs.writeFileSync(path.join(outputDir, filename), buffer);
                    captured.push({
                        type: 'image',
                        filename,
                        alt: img.alt,
                        src: img.src,
                        sourceHash,
                        visualHash
                    });
                    console.log(`✅ Downloaded: ${filename} (${buffer.length} bytes)`);
                }
            }
            await imgPage.close();
        } catch (e) {
            console.error(`❌ Failed: ${img.src} — ${e.message}`);
        }
    }

    // ── Strategy 2: Screenshot visual elements ──
    const screenshotSelectors = [
        'svg:not([width="0"])', 'canvas', '.chart', '.diagram',
        '.infographic', '.chart-container', 'table'
    ];

    for (const selector of screenshotSelectors) {
        try {
            const elements = await page.$$(selector);
            for (let i = 0; i < Math.min(elements.length, 8); i++) {
                const box = await elements[i].boundingBox();
                if (box && box.width > 200 && box.height > 100) {
                    const safeSel = selector.replace(/[^a-z]/gi, '').slice(0, 20);
                    const buffer = await withTimeout(elements[i].screenshot({ type: 'png' }), 5000);
                    const sourceHash = sha256(buffer);
                    const visualHash = await computeVisualHash(hashPage, buffer, 'image/png');
                    const duplicate = findDuplicate({
                        type: 'screenshot',
                        src: `${selector}#${i}`,
                        sourceHash,
                        visualHash
                    }, captured);
                    if (duplicate) {
                        if (duplicate.existing.type === 'image') {
                            const filename = uniqueFilename(outputDir, `screenshot-${safeSel}-${i}.png`);
                            fs.writeFileSync(path.join(outputDir, filename), buffer);
                            removeCapturedFile(outputDir, duplicate.existing);
                            const duplicateIndex = captured.indexOf(duplicate.existing);
                            if (duplicateIndex >= 0) captured.splice(duplicateIndex, 1);

                            captured.push({
                                type: 'screenshot',
                                filename,
                                selector,
                                sourceHash,
                                visualHash,
                                replacedDownloadedImage: duplicate.existing.filename
                            });
                            skippedDuplicates.push({
                                type: 'image',
                                filename: duplicate.existing.filename,
                                duplicateOf: filename,
                                reason: `${duplicate.reason}; screenshot preferred over downloaded image`,
                                distance: duplicate.distance
                            });
                            console.log(`🔁 Replaced downloaded image with screenshot: ${duplicate.existing.filename} -> ${filename} (${duplicate.reason})`);
                            continue;
                        }

                        skippedDuplicates.push({
                            type: 'screenshot',
                            selector,
                            duplicateOf: duplicate.existing.filename,
                            reason: duplicate.reason,
                            distance: duplicate.distance
                        });
                        console.log(`↩️  Skipped duplicate screenshot: ${selector}#${i} -> ${duplicate.existing.filename} (${duplicate.reason})`);
                        continue;
                    }

                    const filename = uniqueFilename(outputDir, `screenshot-${safeSel}-${i}.png`);
                    fs.writeFileSync(path.join(outputDir, filename), buffer);
                    captured.push({
                        type: 'screenshot',
                        filename,
                        selector,
                        sourceHash,
                        visualHash
                    });
                    console.log(`✅ Screenshot: ${filename} (${Math.round(box.width)}x${Math.round(box.height)})`);
                }
            }
        } catch (e) { }
    }

    await hashPage.close();
    await browser.close();

    // Output manifest
    const manifest = {
        url,
        outputDir,
        duplicateDetection: {
            method: 'sha256 exact hash + 8x8 grayscale perceptual hash',
            perceptualHashHammingThreshold: VISUAL_DUPLICATE_DISTANCE,
            preference: 'When a screenshot duplicates a downloaded image, keep the screenshot and remove the downloaded image.'
        },
        captured,
        skippedDuplicates
    };
    fs.writeFileSync(path.join(outputDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
    console.log(JSON.stringify(manifest, null, 2));
}

const [, , url, outputDir] = process.argv;
if (!url || !outputDir) {
    console.error('Usage: node capture-visuals.js <URL> <OUTPUT_DIR>');
    process.exit(1);
}
captureVisuals(url, outputDir).catch(e => { console.error(e); process.exit(1); });
