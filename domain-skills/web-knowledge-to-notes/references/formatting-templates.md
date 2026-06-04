# Formatting Templates

Reusable output templates for `web-knowledge-to-notes`.

The topic folder root should contain only the final main Markdown note. Store
all source, extraction, manifest, image, screenshot, PDF, and other generated
support files in `assets/`.

## Image Placeholder

When an image cannot be obtained, insert this placeholder at the exact position
where the image should appear in the note:

```markdown
> 📷 **[PLACEHOLDER: detailed description of this image/chart]**
> Source: original image URL
> Page location: description of where to find it in the source article (under which heading)
```

The placeholder description should be detailed enough for the user to quickly
locate the image on the source page and manually screenshot it.

## Final Note Template

Assemble the final Markdown note in this strict order:

```markdown
---
title: "Descriptive Title"
source: "https://original-url.com"
site: "Site Name"
date_extracted: "YYYY-MM-DD"
tags:
  - tag1
  - tag2
---

# Title

> **TL;DR**: 2-3 sentences summarizing the single most important takeaway of this note.

---

## Section 1 Heading

[2-4 natural paragraphs, written per Step 4 rules]

[Image or placeholder, if source article has an image here. Downloaded visuals
use `![descriptive alt text](assets/image-name.png)` paths.]
*图注: description*

## Section 2 Heading

[2-4 natural paragraphs]

...

## Section N Heading

[2-4 natural paragraphs]

---

## Practical Application

[If source article has relevant content or this concept has clear real-world applications]

## Common Pitfalls

[If source article has relevant content or agent knowledge includes common misconceptions in this area]

## Key Terms Glossary

| Term   | Translation | Definition |
| ------ | ----------- | ---------- |
| Term 1 | ...         | ...        |
| Term 2 | ...         | ...        |

[This table must cover every financial term that appears in the note. No omissions.]

## Connections

- Related: [[NOTE-NAME]]
- Prerequisite: [[NOTE-NAME]]
- Builds on: [[NOTE-NAME]]

[Use the filename format specified in the user's prompt]

---

*Source: [Original Title](URL) | Extracted: YYYY-MM-DD*
```
