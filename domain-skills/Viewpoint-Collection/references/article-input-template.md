# Article Input Template

Use this template after collecting five articles. Keep entries in the exact
display order requested by the user.

Remove chart/image caption lines from `body` by default. Keep captions only when
the user explicitly asks to retain them.

For ambiguous caption-like lines, inspect the article webpage or saved HTML
around the line before deciding. Remove the line when it is adjacent to image or
figure markup; keep it when it is normal prose or a section heading.

```json
[
  {
    "title": "Article 1 title without book-title marks",
    "url": "https://example.com/article-1",
    "body": "Paragraph one.\nParagraph two.\nParagraph three."
  },
  {
    "title": "Article 2 title without book-title marks",
    "url": "https://example.com/article-2",
    "body": "Paragraph one.\nParagraph two."
  },
  {
    "title": "Article 3 title without book-title marks",
    "url": "https://example.com/article-3",
    "body": "Paragraph one.\nParagraph two."
  },
  {
    "title": "Article 4 title without book-title marks",
    "url": "https://example.com/article-4",
    "body": "Paragraph one.\nParagraph two."
  },
  {
    "title": "Article 5 title without book-title marks",
    "url": "https://example.com/article-5",
    "body": "Paragraph one.\nParagraph two."
  }
]
```

## Manual Fallback Prompt

Use this prompt when a WeChat URL cannot be fetched or parsed:

```text
I could not automatically extract article {n} from this URL:
{url}

Please provide:
1. Article title
2. Article body text, with paragraphs separated by line breaks
```

After receiving manual text, normalize blank lines so the final `body` field
uses single `\n` separators only.
