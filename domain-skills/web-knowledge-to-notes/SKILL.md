---
name: web-knowledge-to-notes
description: >
  This skill should be used when the user wants to turn a single URL
  into a detailed Obsidian Markdown learning note with embedded images.
  Use for "整理笔记", "知识提取", "网页笔记", "extract notes", "turn this
  into notes", "make notes from this article", web resource
  knowledge-base building, and extraction from articles, tutorials,
  documentation, or course pages. Also trigger when the user pastes
  article text directly for note conversion. Handles one URL per
  invocation; the user's prompt orchestrates batch calls.
---

# Web Knowledge to Notes

Transform a single web page into an image-rich Obsidian Markdown
learning note. The note preserves all substantive content from the
source article in a refined, more structured form, and adds
agent-generated commentary, glossary, and cross-references.

This skill is a strict five-step pipeline. Execute each step in order
because later steps depend on outputs from earlier steps.

The user's prompt specifies storage paths, file naming conventions,
and domain-specific formatting.

For each processed page, keep the topic folder root clean: only the
final Markdown note belongs there. Create an `assets/` subfolder for
all downloaded images, the raw Jina Markdown, and the image manifest.

---

## Step 1: Fetch Article Content

Use Jina Reader API as the sole fetch method. Jina returns clean
Markdown with headings, paragraphs, tables, and image URLs preserved.

```bash
mkdir -p "$TOPIC_FOLDER/assets"
curl -sL "https://r.jina.ai/$URL" -o "$TOPIC_FOLDER/assets/jina-raw.md"
```

### Jina Metadata

Jina prepends metadata lines at the top of its output (Title:, URL:,
Markdown Content:, etc.). Identify these lines and separate them from
the article body. Use the metadata for frontmatter (title, source URL)
but do not treat metadata lines as article content when analyzing
structure in Step 2.

### Validation

- Article body (below Jina metadata) must contain > 500 characters
- If Jina returns empty or error content, stop and tell the user.
  The user will paste the article text manually as a fallback.

### Manual Fallback

When the user pastes article text directly instead of providing a URL,
save it as `assets/manual-input.md` and proceed to Step 2. Skip image
download in Step 3 — all images become placeholders since there are no
source URLs to download from.

### Special Cases

- **PDF URLs**: download with
  `curl -sL -o "$TOPIC_FOLDER/assets/paper.pdf" "$URL"`, extract text
  with `pdftotext` or Python `pdfplumber`, save as `assets/jina-raw.md`,
  proceed to Step 2.

---

## Step 2: Analyze Structure and Extract Information Points

Read the full article body from `assets/jina-raw.md` (skip Jina
metadata lines). This step produces two outputs: a section plan and
an information-point inventory. Both are used in Step 4 to ensure
no content is lost during refinement.

### 2a. Section Plan

1. List every H2/H3 subheading in the source article.
2. Each subheading becomes one section in the note, preserving the
   original order. Do not merge sections, do not split a single
   source section into multiple sections, do not reorder.
3. If the source has no subheadings but has obvious topic transitions,
   split those into separate sections.
4. Locate every `![alt](url)` image tag and record which section it
   belongs to.
5. Locate every formula or calculation and mark it for LaTeX
   conversion.
6. Count the word count of each source section — this is the baseline
   for the 80% minimum in Step 4.

### 2b. Information-Point Inventory

For each section, extract every discrete information point from the
source text. An information point is any of:

- A definition or explanation of a concept
- A specific number, statistic, or data point
- An example, case study, or illustration
- A formula or calculation method
- A cause-and-effect relationship or logical argument
- A condition, exception, caveat, or edge case
- A comparison or contrast between concepts
- A named entity reference (company, person, regulation, index)

Record them in this format:

```text
INFORMATION POINTS:
Section: "What Is Free Cash Flow?"
  Word count: ~180 words
  IP-1: FCF = cash after operating expenses and capital asset maintenance
  IP-2: FCF excludes non-cash expenses from income statement
  IP-3: FCF includes equipment/asset spending and working capital changes
  IP-4: Interest payments excluded from standard FCF definition
  IP-5: Investment bankers use FCFF and FCFE variants for different
        capital structures
  Image: [alt text] — position after IP-3
  Formula: none

Section: "How to Calculate Free Cash Flow"
  Word count: ~150 words
  IP-1: Primary formula: FCF = Operating Cash Flow − CapEx
  IP-2: OCF already adjusts for non-cash expenses and working capital
  IP-3: Alternative formula: FCF = Net Income + D&A − ΔWC − CapEx
  IP-4: Alternative uses income statement and balance sheet as inputs
  Image: none
  Formula: 2 formulas marked for LaTeX
...
```

### Validation

- Section count ≥ number of subheadings in source article
- Every source subheading appears in the plan
- Every image tag is assigned to a section
- Every section has at least one information point
- Word count recorded for each section

### Save IP Inventory

Save the information-point inventory to `assets/info-points.json` for
use by the validation script in Step 5. Format:

```json
{
  "sections": [
    {
      "heading": "Section Heading",
      "word_count": 180,
      "info_points": [
        {
          "text": "short description of the info point",
          "keywords": ["key", "terms", "that", "must", "appear"]
        }
      ]
    }
  ]
}
```

Each `keywords` list must contain 2-5 distinctive terms from the
information point that can be matched against the final note text.
Choose terms specific enough to avoid false matches — prefer technical
terms and named entities over common words.

---

## Step 3: Download and Filter Images

Two-phase process: the script downloads candidates, then the agent
filters by content relevance.

### Phase 1: Script Download

```bash
bash scripts/download-images.sh "$TOPIC_FOLDER/assets/jina-raw.md" "$TOPIC_FOLDER/assets"
```

The script extracts all `![alt](url)` references, filters out obvious
junk by URL pattern (ad networks, tracking pixels, favicons, social
icons), downloads with a 20-second per-image timeout, and writes
`assets/image-manifest.json`.

### Phase 2: Agent Content-Relevance Filter

After the script finishes, read `assets/image-manifest.json` and
evaluate every successfully downloaded image. For each image, apply
this decision process:

1. Read the image's **alt text** from the manifest.
2. Read the **section content** surrounding where this image appeared
   in the source article.
3. Ask: **Does this image contain information that supports
   understanding the section's topic?**

Classify using these rules:

| Decision      | Signal                                                                                                        | Action                                                                |
| ------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Keep**      | Alt text describes data, a concept, or a process AND the section discusses that topic                         | Rename to descriptive kebab-case, include in note                     |
| **Keep**      | Alt text is vague BUT the image appeared between explanatory paragraphs (likely a diagram/chart)              | Keep, write descriptive alt text based on section context             |
| **Drop**      | Alt text contains: "ad", "sponsor", "promo", "newsletter", "signup", "related article", "thumbnail", "banner" | Delete file from assets/                                              |
| **Drop**      | Image appeared outside the article body (sidebar, footer, header, "related articles" section)                 | Delete file from assets/                                              |
| **Drop**      | Image is a generic stock photo unrelated to the section's specific financial/technical content                | Delete file from assets/                                              |
| **Uncertain** | Cannot determine relevance from alt text alone                                                                | Keep it — false positive is better than losing an informational image |

After filtering, update `assets/image-manifest.json`: add a
`"agent_decision"` field ("keep" or "drop") and `"reason"` to each
image entry.

### Placeholder Generation

For images that were kept but failed to download, generate a
placeholder at the exact source position:

```markdown
> 📷 **[PLACEHOLDER: detailed description of this image/chart]**
> Source: original image URL
> Page location: which section heading this image appeared under
```

The placeholder description must be specific enough for the user to
locate and screenshot the image from the original page. Bad:
"a chart". Good: "bar chart comparing FCF margins of AAPL, MSFT, and
GOOGL from 2019-2024, Y-axis percentage, X-axis fiscal year."

---

## Step 4: Assemble Note Content

Build the final note following the three-zone layout.

### Zone 1: Navigation Layer (agent-generated)

```markdown
---
title: Article Title
source: https://original-url.com
site: Site Name
date_extracted: YYYY/MM/DD
tags:
  - tag1
  - tag2
---

# ARTICLE-TITLE

> **TL;DR**: 2-3 sentences in Chinese summarizing the core takeaway.

### ⚡ Key Concepts

| 概念   | 含义       | 记忆要点    |
| ------ | ---------- | ----------- |
| Term 1 | definition | memory hook |
| Term 2 | definition | memory hook |

---
```

Frontmatter rules:
- `title`: English, no quotes
- `date_extracted`: `YYYY/MM/DD` format
- `tags`: lowercase, kebab-case
- H1 heading and filename: UPPER-CASE-KEBAB matching the title

Key Concepts table: 4-8 entries, each row self-contained and scannable
in 2 seconds during review.

### Zone 2: Article Body + Agent Commentary

Process each section from the section plan **in original order**.

#### Content refinement rules

The note body is a refined version of the source article — not a
verbatim copy, but not a free rewrite either. Refinement operates
within strict boundaries to ensure no knowledge is lost.

**What refinement IS allowed to do:**

- Translate the source text into Chinese. The entire note body is
  written in Chinese regardless of the source language.
- Polish and smooth the Chinese text — it should read like a
  well-written Chinese financial article, not a mechanical translation.
  Use natural connectives (因此, 然而, 具体来说, 值得注意的是, 换言之)
  and ensure each paragraph has a coherent narrative flow.
- Retain English for financial/technical terms. On first occurrence,
  add Chinese in parentheses: `P/E Ratio（市盈率）`. Subsequent
  occurrences can use English only.
- Remove filler phrases and padding from the source
- Merge duplicate paragraphs that repeat the same point
- Reorder paragraphs within a section for better logical flow
- Break long run-on sentences into clearer shorter sentences

**What refinement is NOT allowed to do:**

- Delete any information point from the Step 2 inventory — every IP
  must appear in the refined text
- Change the technical meaning of any statement
- Add new claims or information to the body text (agent additions
  go only in `> [!insight]+` commentary blocks)
- Merge separate source sections together or reorder sections
- Use stilted translation patterns like "这是一个...的概念" or
  "它被定义为..." — write naturally, not literally
- Over-simplify: translating a precise 3-clause English sentence
  into a vague 1-clause Chinese sentence loses information

#### Per-section word count rule

Each refined section must be ≥ 80% of the word count of the
corresponding source section (as recorded in Step 2).

```text
Source section "What Is Free Cash Flow?" — 180 words
Refined section minimum: 180 × 0.8 = 144 words
```

If a refined section falls below 80%, it means content was cut that
should not have been. Restore the missing material before proceeding.

The 80% floor applies per section, not to the note as a whole —
this prevents the agent from over-trimming short sections while
padding long ones.

#### Information-point verification

After writing each section, cross-check against the information-point
inventory from Step 2:

```text
Section: "What Is Free Cash Flow?"
  IP-1: FCF = cash after operating expenses and capital asset maintenance ✓
  IP-2: FCF excludes non-cash expenses from income statement ✓
  IP-3: FCF includes equipment/asset spending and working capital changes ✓
  IP-4: Interest payments excluded from standard FCF definition ✓
  IP-5: Investment bankers use FCFF and FCFE variants ✓
  → All 5/5 information points present ✓
  → Word count: 155 words (180 × 0.8 = 144 minimum) ✓
```

If any information point is missing, add it back before moving to the
next section. Do not proceed with missing IPs.

#### Section-to-section mapping enforcement

The final note must have exactly the same H2 headings as the source
article, in the same order. Before writing, verify:

```text
Source headings: [H1, H2a, H2b, H2c, ...]
Note headings:   [H2a, H2b, H2c, ...] + Glossary + Connections
```

If the counts do not match, stop and fix before continuing.

#### Image placement

Images appear at their original positions within the refined section
text (between the same information points as in the source):

- Downloaded successfully: `![descriptive alt](assets/filename.png)`
  followed by `*图注: Chinese description*`
- Download failed: placeholder block

#### Formula handling

Convert every formula in the source to LaTeX `$$...$$` block display.
Use `\text{}` for named variables:

```
Source: "FCF = Net Income + D&A - Changes in WC - CapEx"
Output: $$FCF = \text{Net Income} + \text{D\&A} - \Delta WC - \text{CapEx}$$
```

Agent commentary may include formulas too (worked examples). Same
LaTeX format inside callout blocks.

#### Agent commentary rules

Place one `> [!insight]+` block at the end of each section, after all
refined text and images for that section.

```markdown
## Original Section Heading

[Refined article text — all IPs preserved, ≥80% word count]

[Images at original positions]

> [!insight]+ 📌 Agent 点评
>
> **Bold label:** Substantive commentary.

---
```

**Anchoring requirement**: each commentary point must reference
specific content from its own section — a term the section introduced,
a number it cited, a claim it made. If the agent cannot point to a
specific sentence or concept in the section it is commenting on, the
commentary belongs elsewhere or should not exist.

**Concreteness requirement**: every commentary point must contain at
least one concrete element from this list:
- A specific number, percentage, or range
- A named company, index, or instrument
- A formula or calculation
- A `[[NOTE-NAME]]` cross-reference
- A specific real-world scenario with enough detail to be actionable

Commentary that passes the "allowed types" check but fails the
concreteness check is still filler. Example of failure: "This ratio
varies by industry" (no numbers, no industries named). Example of
pass: "S&P 500 median is ~1.0-1.5; banks run 10+ due to their
leverage-dependent business model."

Allowed commentary types (use only what applies):

| Type                        | What it looks like                                 |
| --------------------------- | -------------------------------------------------- |
| Background the source omits | Facts the reader needs but the article skipped     |
| Practical trap or caveat    | Specific way this concept misleads in practice     |
| Concrete reference values   | Industry benchmarks, typical ranges, real data     |
| Cross-note link             | Connection to a specific note with explanation     |
| Calculation example         | Worked numbers making an abstract formula concrete |

Forbidden:

- "This section is important / worth reviewing carefully"
- Restating what the section already said in different words
- Vague associations without specifics ("relates to macro")
- Re-defining terms the section already defined
- Commentary about a different section's content

If a section has no substantive, concrete commentary to add, omit the
`> [!insight]+` block entirely. No block is better than a weak block.

### Zone 3: Index Layer (agent-generated)

```markdown
## Key Terms Glossary

| Term | 中文 | 定义 |
| ---- | ---- | ---- |
| ...  | ...  | ...  |

## Connections

- 前置知识：[[NOTE-NAME]]
- 关联概念：[[NOTE-NAME]] — specific reason
- 应用场景：[[NOTE-NAME]] — specific reason

---

*Source: [Article Title](URL) | Extracted: YYYY/MM/DD*
```

Glossary: cover every financial/technical term in the note.
Cross-references: use `[[UPPER-CASE-KEBAB]]` format.

### Language Rules

- All note body content: Chinese. This includes refined article text,
  TL;DR, Key Concepts, commentary, Glossary definitions, Connections,
  and image captions.
- Financial/technical terms: keep English originals inline. First
  occurrence add Chinese in parentheses: `P/E Ratio（市盈率）`.
  Subsequent occurrences can use English only.
- Frontmatter fields, H1 heading, H2 section headings, and filename:
  English (matching source article headings).
- Chinese text quality: read like a well-written Chinese financial
  article. Avoid mechanical translation artifacts. Match the register
  of the source — conversational if the source is conversational,
  formal if the source is formal.

---

## Step 5: Validate and Save

After assembling the note, run the validation script. This is
mandatory — do not deliver the note until all checks pass.

```bash
python3 scripts/validate-note.py "$TOPIC_FOLDER"
```

The script checks 10 categories: section integrity, per-section word
count ≥80%, frontmatter completeness, required sections, formula
conversion, cross-reference format, image consistency, commentary
quality, information-point coverage, and file organization.

If any check fails, the script prints the specific failure with
details. Fix each failure and re-run until all 10 pass. Common
failures and fixes:

| Failure             | Typical cause                        | Fix                                    |
| ------------------- | ------------------------------------ | -------------------------------------- |
| Section Integrity   | Heading merged or dropped            | Restore missing H2                     |
| Word Count <80%     | Over-trimmed during refinement       | Restore removed content                |
| Missing info points | IP deleted during refinement         | Add IP back to section                 |
| Commentary quality  | Filler phrase or no concrete element | Rewrite with specifics or remove block |
| Unconverted formula | Plain-text formula not LaTeX'd       | Wrap in `$$...$$`                      |
| Cross-ref format    | `[[lowercase name]]`                 | Change to `[[UPPER-CASE-KEBAB]]`       |

Once all checks pass, save the final note to the topic folder root.

### Section Integrity

- [ ] Count H2 headings in final note (excluding Glossary and
      Connections) — must equal source article heading count
- [ ] Headings appear in the same order as the source
- [ ] No source section was merged, split, or omitted

### Information Completeness

- [ ] Every information point from Step 2 inventory is present in
      the corresponding section of the final note
- [ ] Each section's word count ≥ 80% of the source section's word
      count
- [ ] No information point was moved to a different section
- [ ] Formulas converted to LaTeX, no plain-text formulas remain

### Refinement Boundaries

- [ ] No new factual claims added to the body text (agent additions
      are only in commentary blocks)
- [ ] Technical meaning of all statements preserved
- [ ] Body text is in Chinese with English financial/technical terms
      retained inline
- [ ] Chinese reads naturally — no mechanical translation artifacts
- [ ] Only filler/padding/duplication was removed, not substance

### Commentary Quality

- [ ] Each `> [!insight]+` block references specific content from its
      own section (not another section)
- [ ] Each commentary point contains at least one concrete element
      (number, company, formula, note link, or specific scenario)
- [ ] No filler: no importance statements, no restating, no vague
      associations
- [ ] Sections with no substantive commentary have no `> [!insight]+`
      block

### Images

- [ ] Every kept image has a downloaded file or placeholder at its
      original position in the text
- [ ] Decorative/ad images are excluded — not in the final note
- [ ] Downloaded images have descriptive kebab-case filenames
- [ ] Placeholders have specific descriptions, source URLs, and
      section locations
- [ ] `image-manifest.json` has agent_decision and reason for each
      image

### Format

- [ ] Frontmatter complete: title, source, site, date_extracted, tags
- [ ] TL;DR in Chinese, 2-3 sentences
- [ ] Key Concepts table has 4-8 entries
- [ ] Glossary covers every financial/technical term
- [ ] Cross-references use `[[UPPER-CASE-KEBAB]]` format
- [ ] Only the final `.md` note in topic folder root; everything else
      in `assets/`

---

## Resources

| When                                           | Use                                  |
| ---------------------------------------------- | ------------------------------------ |
| Need to download and pre-filter article images | `scripts/download-images.sh`         |
| Need to validate final note before delivery    | `scripts/validate-note.py`           |
| Need final note layout or placeholder format   | `references/formatting-templates.md` |