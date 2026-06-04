#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


def extract_with_readability(raw_html: str) -> str | None:
    try:
        from readability import Document
        import html2text
    except ImportError:
        return None

    doc = Document(raw_html)
    content_html = doc.summary()
    title = doc.title()

    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_tables = False

    content_md = converter.handle(content_html).strip()
    return f"# {title}\n\n{content_md}".strip()


def extract_with_regex(raw_html: str) -> str:
    content = re.sub(
        r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>",
        "",
        raw_html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    match = re.search(r"<(article|main)[^>]*>(.*?)</\1>", content, re.DOTALL | re.IGNORECASE)
    content = match.group(2) if match else content
    content = re.sub(r"<h([1-6])[^>]*>(.*?)</h\1>", r"\n## \2\n", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<[^>]+>", "", content)
    content = html.unescape(content)
    return re.sub(r"\n{3,}", "\n\n", content).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract article Markdown from raw HTML.")
    parser.add_argument("input_html")
    parser.add_argument("output_md")
    args = parser.parse_args()

    raw_html = Path(args.input_html).read_text(encoding="utf-8", errors="replace")
    content_md = extract_with_readability(raw_html) or extract_with_regex(raw_html)
    Path(args.output_md).write_text(content_md, encoding="utf-8")

    word_count = len(re.findall(r"\w+", content_md))
    print(f"wrote {args.output_md} words={word_count}")


if __name__ == "__main__":
    main()
