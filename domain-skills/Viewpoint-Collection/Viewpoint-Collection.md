---
name: coal-viewpoint-update
description: >
  This skill should be used when updating the "观点搜集整理" sheet in the
  CITIC Securities coal industry database workbook. Trigger when the user says
  "update viewpoints", "replace viewpoint links", "fill in new articles",
  "coal weekly report viewpoint updates", provides 5 WeChat article links for
  the Excel database, or says "更新观点", "替换链接", "填入新文章". Also handle
  blocked WeChat extraction by requesting manual article text. Do NOT trigger
  for unrelated Excel editing, general coal research, or casual discussion.
---

# Coal Viewpoint Update

Update the five viewpoint entries in the `观点搜集整理` sheet of the CITIC
Securities coal industry database workbook. Treat this as a narrowly scoped
spreadsheet maintenance task: preserve workbook structure and formatting while
replacing the designated title, URL, body cells, and body-range row heights.

## Activation Guard

Use this skill only when the user needs the database viewpoint page refreshed
with five article links or five prepared article entries. Do not use it for
general spreadsheet cleanup, financial modeling, or article summarization
outside the workbook update workflow.

## Inputs

Collect these inputs before editing the workbook:

- One `.xlsx` coal industry database workbook.
- Five article URLs in the intended display order.
- Article title and body text for any URL that cannot be fetched automatically.
- Caption policy: remove chart/image captions unless the user explicitly says
  to keep them.

If the user provides fewer or more than five entries, ask for the exact five
items before modifying the workbook. The workbook layout is fixed around five
viewpoint slots, so partial updates are easy to misalign.

## Cell Map

Write each article into column D of the matching row group. Columns D:M are
already merged for body areas; write to the top-left cell in column D.

| Article | Title row | URL row | Body merged range |
| --- | ---: | ---: | --- |
| 1 | 121 | 122 | D123:M139 |
| 2 | 140 | 141 | D142:M160 |
| 3 | 161 | 162 | D163:M178 |
| 4 | 179 | 180 | D181:M199 |
| 5 | 200 | 201 | D202:M215 |

## Workflow

1. Fetch each article page when possible.
2. Extract the article title and body from WeChat HTML.
3. Apply the caption policy. Remove chart/image caption text by default; keep it
   only when the user explicitly requests caption retention.
4. Review ambiguous caption-like lines against the fetched webpage context
   before writing the final article JSON.
5. If extraction is blocked, ask the user for that article's title and body
   instead of leaving an empty slot.
6. Create an article JSON file using the reference template.
7. Run the bundled workbook update script.
8. Verify URL display values and hyperlink targets both match the provided
   links.
9. Verify body merged-range row heights were recalculated to fit wrapped text.
10. Verify the output workbook exists and uses the original filename with a
   `tmp` suffix unless the user requested another output path.

## Extraction Rules

For WeChat Official Account articles, prefer the `<h1 id="activity-name">`
title and extract body text from `<div id="js_content">`.

Preserve paragraph order with single newlines between paragraphs. Exclude
scripts, styles, images, videos, iframes, author metadata, source notices,
publish dates, and end-of-article boilerplate.

Remove chart/image captions by default, including short centered chart titles,
figure/table labels, data-source notes, and lines such as `价格对比`, `走势图`,
or `统计图`. Also remove natural-language photo captions such as `图为...` and
short standalone lines describing where a photo was taken. If the user
explicitly says to keep captions, retain those caption lines and run the script
with `--keep-captions`.

Do not rely on regex alone for ambiguous caption-like text. When a line may be
either a caption or an article heading/body sentence, inspect the fetched
webpage or saved HTML around that exact text. Treat it as a caption when the
line is inside or immediately after a centered image/figure block, adjacent to
an `<img>`/image link/video placeholder, styled like a small standalone
description, or separated from surrounding prose by image containers. Preserve
it when it appears in normal paragraph flow or functions as a section heading.
If the page cannot be fetched for this review, remove only high-confidence
caption lines and keep ambiguous content.

Common photo-caption signals observed in WeChat articles:

- A centered image block appears immediately before the text.
- The caption itself is in a separate centered section or paragraph.
- Caption text is shorter than body paragraphs and often uses smaller type,
  commonly around 14-15px, sometimes bold.
- The next content block switches back to justified body prose or a section
  heading.
- The line describes what is shown in the image, often with phrases like
  `图为...`, `...拍摄的...`, a place name plus an object, or a source/photo note.

When the fetched page contains `请在微信客户端打开` or lacks `js_content`, treat it
as blocked by anti-scraping controls. Ask for manual title and body text for
that URL and continue after the user supplies it.

## Workbook Rules

Restrict edits to the 15 target cells in the cell map plus the row heights
inside the five body merged ranges. This keeps formulas, source labels, merged
ranges, column widths, sheet order, and other sheets intact while avoiding stale
blank space from previous articles.
For URL cells, update both the displayed cell value and the Excel hyperlink
target; replacing only the displayed value can leave a stale clickable link.
For body cells, keep wrap text enabled and recalculate the total height of each
merged body range from the normalized body text and the D:M pixel width. Excel
does not reliably auto-fit wrapped text in merged cells, so use the bundled
script instead of relying on manual auto-fit. Prefer font-aware measurement
when the runtime has Pillow available; otherwise fall back to a conservative
height estimate. Assign normal line-height rows to the visible wrapped text
lines into the bottom row of each merged range, compressing the preceding body
rows. This mirrors the manual Excel fix of dragging the final row height of the
merged area until all body text is visible and the bottom of the text sits near
the bottom of the corresponding area. Keep every row height at or below Excel's
maximum row height, and place overflow into rows immediately above the final row
from the bottom upward; invalid oversized row heights can trigger an Excel
repair log and still leave text clipped. Keep the non-overflow rows at normal
row height rather than collapsing them, because Excel may clip merged wrapped
text when the upper rows of the merged region are nearly zero-height even if the
total region height is mathematically sufficient.

Patch the workbook package directly instead of saving the whole workbook through
a general spreadsheet writer. Complex source workbooks may contain drawing
objects and external-link caches that broad rewrites can damage, causing Excel
to show a recovery log on open. Limit package changes to the target worksheet XML
and that worksheet's relationship file. Patch the worksheet XML text in place so
namespace declarations, revision metadata, drawing anchors, sheet properties,
merged ranges, and unrelated cells remain byte-for-byte compatible with the
source workbook.

Use the bundled script for the workbook write step:

```bash
python scripts/update_viewpoints.py /path/to/database.xlsx /path/to/articles.json
```

When the user explicitly requests caption retention, run:

```bash
python scripts/update_viewpoints.py /path/to/database.xlsx /path/to/articles.json --keep-captions
```

Run the script with a Python environment that has `openpyxl` installed. If the
default `python` lacks spreadsheet packages, use the agent or workspace runtime
that provides them.

The default output path is the original workbook name with `tmp` inserted before
the extension, for example `中信建投煤炭行业数据库20260529tmp.xlsx`.

## References

| When | Read or run |
| --- | --- |
| Need the article JSON shape or manual fallback format | `references/article-input-template.md` |
| Need to update the workbook from prepared article data | `scripts/update_viewpoints.py` |
