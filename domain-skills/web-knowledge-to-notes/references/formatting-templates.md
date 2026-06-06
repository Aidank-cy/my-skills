# Formatting Templates

Reusable output templates for `web-knowledge-to-notes`.

The topic folder root contains only the final Markdown note. Store
all downloaded images, the Jina raw markdown, and the image manifest
in `assets/`.

## Image Placeholder

When an image cannot be downloaded or times out, insert this at the
exact position the image appeared in the source article:

```markdown
> 📷 **[PLACEHOLDER: detailed description of this image/chart]**
> Source: original image URL
> Page location: which section heading this image appeared under
```

The description must be specific enough for the user to locate the
image on the original page and manually screenshot it. Bad example:
"a chart". Good example: "bar chart comparing FCF margins of AAPL,
MSFT, and GOOGL from 2019-2024, with Y-axis showing percentage and
X-axis showing fiscal year."

## Final Note Template

Assemble the final Markdown note in this strict order:

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

<table style="width: 100%;">
  <thead>
    <tr>
      <th>概念</th>
      <th>含义</th>
      <th>记忆要点</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Term 1</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <td>Term 2</td>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>

---

## Source Section Heading 1

[Original article text — verbatim, original language, original
paragraph breaks preserved]

[Optional `###` subheadings inside this H2 when the content has clear
parallel categories, steps, examples, contrast pairs, or named items.
Do not add extra H2 headings.]

[Images at original positions:
- Downloaded:
  <p align="center">
    <img src="assets/filename.png" alt="descriptive alt" />
  </p>
  *图注: Chinese description*
- Failed: placeholder block]

[Formulas: $$LaTeX$$ block display]

> [!insight]+ 📌 Agent 点评
>
> **Bold label for the point:** Substantive commentary specific to
> this section. No filler. No restating the original.

---

## Source Section Heading 2

[Same pattern as above]

---

...

---

## Key Terms Glossary

<table style="width: 100%;">
  <thead>
    <tr>
      <th>Term</th>
      <th>中文</th>
      <th>定义</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>

## Connections

- 前置知识：[[NOTE-NAME]]
- 关联概念：[[NOTE-NAME]] — specific reason
- 应用场景：[[NOTE-NAME]] — specific reason

---

*Source: [Article Title](URL) | Extracted: YYYY/MM/DD*
```

## Agent Commentary Format

Each commentary block uses Obsidian's callout syntax with the
`insight` type. The `+` suffix means expanded by default (the user
can collapse it when content becomes familiar during later reviews):

```markdown
> [!insight]+ 📌 Agent 点评
>
> **Background the source omits:** concrete supplementary information.
>
> **⚠️ Common trap:** specific practical caveat with example.
>
> **Cross-reference:** link to related note with explanation of the
> relationship: [[NOTE-NAME]] — how it connects.
```

Each bold label signals the type of commentary so the user can scan
quickly. Only include types that apply to the current section.
