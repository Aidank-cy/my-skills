---
name: web-knowledge-to-notes
description: >
  This skill should be used when the user wants to turn URLs into detailed
  Obsidian Markdown learning notes with embedded images. Use for "整理笔记",
  "知识提取", "网页笔记", "extract notes", "turn this into notes", "make notes
  from this article", URL batches, web resource knowledge-base building, and
  extraction from articles, tutorials, documentation, PDFs, or course pages.
---

# Web Knowledge to Notes

Transform web pages into comprehensive, detailed, image-rich Obsidian Markdown
learning notes.

This skill is a strict seven-step pipeline. Execute each step in order because
later steps depend on explicit outputs from earlier steps. Keep fetching,
extraction, structure analysis, writing, image handling, assembly, and quality
checks as separate phases.

The user's prompt specifies storage paths, file naming conventions, and
domain-specific formatting such as bilingual headers, glossary format, captions,
and cross-reference style.

For each processed page, keep the topic folder root clean: only the final main
Markdown note belongs in the root. Create an `assets/` subfolder for all
intermediate, source, and media artifacts, including `raw.html`,
`article-text.txt`, `extracted.md`, `manifest.json`, downloaded images,
screenshots, PDFs, and placeholders expressed as files.

---

## Step 1: Fetch Source Page Content

Use a two-tier fetch strategy. Puppeteer is the primary method because it
launches a real Chromium browser and can reach pages that block simple
`curl`/fetch requests. Built-in web fetch is the fallback.

### Tier 1: Puppeteer

Fetch each page with `scripts/fetch-page.js`:

```bash
mkdir -p "$TOPIC_FOLDER/assets"
node scripts/fetch-page.js "$URL" "$TOPIC_FOLDER/assets/raw.html" "$TOPIC_FOLDER/assets/article-text.txt"
```

Save page HTML to `assets/raw.html`. Save browser-extracted article text to
`assets/article-text.txt`. Use the returned article text length for validation.

### Tier 2: Built-In Web Fetch

If Puppeteer throws an error or returns empty content for a specific URL, use
the built-in web browse/fetch capability to read the page. Save the result for
Step 2 processing.

### Validation

- Fetched content must contain > 500 characters of article text
- If Tier 1 fails, try Tier 2
- If both fail, mark the URL as failed, skip to the next URL, and log it in the
  user-specified index or status file

### Special Cases

- **PDF URLs** (e.g., NBER papers): download with
  `curl -sL -o "$TOPIC_FOLDER/assets/paper.pdf" "$URL"`, then extract text with
  `pdftotext "$TOPIC_FOLDER/assets/paper.pdf" -` or Python `pdfplumber`. Skip
  Step 2 and go directly to Step 3.
- **Course index pages** (e.g., Damodaran NYU): extract all lecture titles and
  links from the page, download associated PDF slides, extract content from each,
  and combine into one consolidated note.

---

## Step 2: Extract Article Content

Extract the main body content from `assets/raw.html`. Use
`scripts/extract-article.py`, which tries Python `readability-lxml` +
`html2text` first and regex extraction as fallback:

```bash
python3 scripts/extract-article.py "$TOPIC_FOLDER/assets/raw.html" "$TOPIC_FOLDER/assets/extracted.md"
```

### Output

Save extraction result as `assets/extracted.md`, containing:

- Article title
- All body paragraphs, preserving original paragraph breaks
- All subheadings, preserving hierarchy
- All tables
- All image src URLs and alt text, preserved as `![alt](src)`

### Validation

- `assets/extracted.md` word count > 500. Normal Investopedia articles
  typically yield > 2000 words.
- If < 500: check whether it is a JS-rendered page, retry Step 1 with
  Puppeteer if available, otherwise mark as low-quality extraction and continue.

### Preservation Requirement

Do not compress, summarize, or rewrite content in this step. Preserve the source
article's original content structure as completely as possible; organize the
content later in Step 3.

---

## Step 3: Analyze Article Structure and Determine Section List

Before writing any note content, analyze the source article's structure.

### Operation

Read the full content of `assets/extracted.md` and identify every logical
paragraph or topic in the source article.

The note must have at least as many sections as the source article has logical
topics. Preserve the one-to-one mapping; do not merge source topics together.

Specific approach:

1. List all subheadings (H2/H3) in the source article
2. Treat each subheading as one section
3. If the source has no subheadings but has obvious topic transitions
   (subject matter changes), split those into separate sections too
4. If a source section has very little content (< 3 sentences), keep it as a
   separate section. Step 4 will use agent knowledge to supplement and extend it.

### Output

Generate a section plan list in this format:

```text
SECTION PLAN:
1. [Source heading/topic] — source has ~X sentences / X paragraphs on this topic
2. [Source heading/topic] — ...
3. ...
N. Practical Application — (if source has practical application content)
N+1. Key Terms Glossary — (mandatory)
N+2. Connections — (mandatory)
```

### Validation

- Section count ≥ number of subheadings in source article (can be more, never fewer)
- Every source article subheading appears in the plan

---

## Step 4: Write Note Content Section by Section

Following the section plan from Step 3, write content one section at a time.

### Writing Rules for Each Section

**Paragraph structure: 2-4 natural paragraphs**

- Paragraph 1: Concept introduction. Explain what this is, why it matters, and
  where it sits in the overall knowledge framework.
- Paragraph 2: Core details. Reproduce every detail from the source article's
  corresponding section: every point, data point, example, and nuance. Do not
  summarize this material.
- Paragraph 3: Extension or deep-dive. If the source content is substantial,
  expand on points the source mentioned but did not elaborate on. If the source
  content is thin, use agent knowledge to supplement directly related content:
  relationships with other sections in this note, connections to other notes in
  the knowledge base, common real-world application scenarios, and mistakes
  beginners frequently make.
- Paragraph 4 (if warranted): Additional edge cases, controversial viewpoints,
  or advanced tips.

**Content source priority**

```text
1. Source article's original details (highest priority: reproduce every detail)
2. Agent knowledge to deep-dive and expand on source content
3. Agent knowledge to supplement related concepts as extension
```

**Content boundaries**

- Do not skip any detail point from the source article
- Do not compress 3 source paragraphs into 1 sentence
- Do not write only vague overviews without specific content in a section
- Do not fabricate nonexistent data or case studies. Agent knowledge supplements
  are fine, but must be accurate and directly related.

### Language Rules

**Two-language separation: English for thinking, Chinese for writing.**

- All internal reasoning, planning, and intermediate work (Step 1-3, Step 7
  self-check) must be done in English. Section plans, validation logs, and debug
  output are all in English.
- All note content written in Step 4 defaults to Chinese. This includes every
  paragraph in every section, TL;DR, Practical Application, Common Pitfalls, and
  Glossary definitions.
- Financial terms retain their English originals. On first occurrence, add
  Chinese translation in parentheses, e.g., `P/E Ratio（市盈率）`. Subsequent
  occurrences can use English only.
- Chinese text must read naturally and fluently, like a well-written Chinese
  financial article rather than a mechanical translation. Sentences should flow
  with logical connectives such as `因此`, `然而`, `具体来说`, `值得注意的是`,
  and `换言之`. Each paragraph should have a coherent narrative arc.
- Use the same register as the source article. If the source is explanatory and
  conversational, the Chinese should be too; if the source is formal, match that.
- Avoid stilted translation patterns like `这是一个...的概念` or `它被定义为...`.
- Follow the user's prompt for bilingual heading format, caption language, and
  related project conventions.

### Formatting Elements

Use these elements only when they fit the source content:

| Element | Use When | Skip When |
|---|---|---|
| `> **Key Definition:**` blockquote | The section introduces a definition worth memorizing | The section is discursive with no clear-cut definition |
| Formula code block | The source article contains a math formula or calculation | The source has no formula in this section |
| Markdown table | Comparing multiple items or listing structured data | Content is purely narrative |
| Mermaid diagram | Source describes a process/flow in pure text with no accompanying image | An image is available, or content does not involve a process |
| Image / Placeholder | Source article has an image/chart at this location | Source has no visual element at this location |

---

## Step 5: Image Handling

Puppeteer is the primary image capture method. Use `scripts/capture-visuals.js`
for article images, chart screenshots, figure screenshots, and large table
screenshots:

```bash
node scripts/capture-visuals.js "$URL" "$TOPIC_FOLDER/assets/"
```

### Operation Sequence

1. Collect all image URLs from `assets/extracted.md` (`![alt](src)` format)
2. Filter out obviously useless images: tracking pixels, icons < 100px, ad
   images, logos, social media icons, and base64 data URIs with `data:image/svg`
3. Run `scripts/capture-visuals.js` for the source URL and `assets/` folder
4. Deduplicate visuals before using them:
   - Treat identical normalized source URLs or identical file hashes as duplicate
     images.
   - Use perceptual hash comparison for near-duplicates. The bundled script
     shrinks each captured image to an 8x8 grayscale fingerprint and skips a new
     visual when its Hamming distance from an already-kept visual is <= 6.
   - Prefer screenshots over downloaded images when both represent the same
     visual, because screenshots preserve the page's rendered context more
     reliably. When a screenshot is near-duplicate with a downloaded image, keep
     the screenshot and drop the downloaded image.
5. After downloads complete, match images to note positions:
   - Compare downloaded filenames (derived from alt text) with context in the
     source article
   - Reference each image as `![descriptive alt text](assets/image-filename.png)`
   - Add caption: `*图注: description*`
6. For any image that failed to download, insert a placeholder

### Placeholder Format

Use the image placeholder template in `references/formatting-templates.md`.
The placeholder description must be detailed enough for the user to quickly
locate the image on the source page and manually screenshot it.

### Image Naming

- Use descriptive kebab-case names: `income-statement-structure.png`
- Avoid meaningless names like `img-1.png`, `figure-2.png`
- Store images in `assets/` beside the source and extraction artifacts

---

## Step 6: Assemble Final Note

Combine all section content from Step 4 and images from Step 5 into the final
Markdown file.

Use the strict final note template in `references/formatting-templates.md`.
Keep frontmatter, title, TL;DR, source-mapped sections, images/placeholders,
optional application and pitfall sections, glossary, connections, and source
footer in that order. Save only the final main Markdown note in the topic folder
root; all other generated files stay under `assets/`.

---

## Step 7: Quality Self-Check

Before saving the file, check against every item below. If any item fails, fix it
before saving.

### Content Check

- [ ] Section count ≥ number of logical topics in source article
- [ ] Every subheading/topic from the source article has a corresponding section in the note
- [ ] Each section has 2-4 natural paragraphs
- [ ] Every specific detail from the source (data, examples, definitions, caveats) appears in the note
- [ ] Thin sections have been supplemented with agent knowledge (related/extended content)
- [ ] Language rules followed per user prompt (default language, term handling)

### Format Check

- [ ] Frontmatter complete (title, source, site, date_extracted, tags)
- [ ] TL;DR exists and is accurate
- [ ] Definitions use blockquote format
- [ ] Formulas use code blocks, only when source article has formulas
- [ ] Glossary covers every financial term that appears in the note
- [ ] Cross-references use the correct filename format

### Image Check

- [ ] Every meaningful image in the source article has a corresponding image or placeholder in the note
- [ ] Successfully downloaded images have descriptive filenames, stored in `assets/`
- [ ] Main note references downloaded visuals with `assets/<filename>` paths
- [ ] Duplicate or near-duplicate visuals were skipped or noted in `assets/manifest.json`
- [ ] Placeholders contain detailed description, source URL, and page location

---

## Resources

| When | Use |
|------|-----|
| Need to fetch JS-rendered or anti-scraping-protected pages with Puppeteer | `scripts/fetch-page.js` |
| Need to extract article Markdown from fetched HTML | `scripts/extract-article.py` |
| Need image, chart, figure, or table capture | `scripts/capture-visuals.js` |
| Need final note structure or image placeholder format | `references/formatting-templates.md` |
