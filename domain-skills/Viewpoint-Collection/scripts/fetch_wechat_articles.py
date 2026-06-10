#!/usr/bin/env python3
"""Fetch WeChat article pages with browser-like headers and write article JSON."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


SCRIPT_DIR = Path(__file__).resolve().parent
UPDATE_SCRIPT = SCRIPT_DIR / "update_viewpoints.py"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://mp.weixin.qq.com/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


def load_update_module() -> Any:
    spec = importlib.util.spec_from_file_location("update_viewpoints", UPDATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {UPDATE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    if args.urls_file:
        with args.urls_file.open("r", encoding="utf-8") as handle:
            urls.extend(line.strip() for line in handle if line.strip())
    urls.extend(args.urls)
    if len(urls) != 5:
        raise ValueError("exactly five WeChat article URLs are required")
    return urls


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def warm_session(session: requests.Session, timeout: float) -> None:
    session.get("https://mp.weixin.qq.com/", timeout=timeout)


def fetch_html(session: requests.Session, url: str, timeout: float) -> str:
    response = session.get(url, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    if not response.encoding:
        response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def safe_html_name(index: int, url: str) -> str:
    token = url.rstrip("/").rsplit("/", 1)[-1] or f"article-{index}"
    safe_token = "".join(char if char.isalnum() or char in "-_" else "_" for char in token)
    return f"{index:02d}-{safe_token}.html"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch five WeChat article URLs with browser-like headers and write article JSON."
    )
    parser.add_argument("urls", nargs="*", help="Five WeChat article URLs in workbook display order")
    parser.add_argument("--urls-file", type=Path, help="Text file containing one URL per line")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output article JSON path")
    parser.add_argument("--html-dir", type=Path, help="Optional directory for fetched HTML captures")
    parser.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout in seconds")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between article requests in seconds")
    parser.add_argument(
        "--keep-captions",
        action="store_true",
        help="Keep chart/image caption lines in extracted article bodies.",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Skip the initial mp.weixin.qq.com homepage request.",
    )
    args = parser.parse_args()

    urls = read_urls(args)
    update_viewpoints = load_update_module()
    session = build_session()

    if not args.no_warmup:
        try:
            warm_session(session, args.timeout)
        except requests.RequestException as exc:
            print(f"warning: WeChat warmup request failed: {exc}", file=sys.stderr)

    if args.html_dir:
        args.html_dir.mkdir(parents=True, exist_ok=True)

    articles: list[dict[str, str]] = []
    failures: list[str] = []

    for index, url in enumerate(urls, start=1):
        try:
            html = fetch_html(session, url, args.timeout)
            if args.html_dir:
                html_path = args.html_dir / safe_html_name(index, url)
                html_path.write_text(html, encoding="utf-8")

            title, body = update_viewpoints.extract_wechat_article(
                html, keep_captions=args.keep_captions
            )
            if not title or not body:
                failures.append(f"article {index}: blocked or missing title/body: {url}")
                continue

            articles.append({"title": title, "url": url, "body": body})
            print(f"article {index}: extracted {title}", file=sys.stderr)
        except requests.RequestException as exc:
            failures.append(f"article {index}: request failed: {url} ({exc})")

        if index < len(urls) and args.delay > 0:
            time.sleep(args.delay)

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(articles, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(os.fspath(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
