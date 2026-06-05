#!/usr/bin/env python3
"""Update viewpoint entries in the coal industry database workbook."""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape


SHEET_NAME = "观点搜集整理"
SECTIONS = [
    {"title_row": 121, "url_row": 122, "body_row": 123, "body_end_row": 139},
    {"title_row": 140, "url_row": 141, "body_row": 142, "body_end_row": 160},
    {"title_row": 161, "url_row": 162, "body_row": 163, "body_end_row": 178},
    {"title_row": 179, "url_row": 180, "body_row": 181, "body_end_row": 199},
    {"title_row": 200, "url_row": 201, "body_row": 202, "body_end_row": 215},
]
BODY_START_COLUMN = 4
BODY_END_COLUMN = 13
BODY_FONT_PIXELS = 13
BODY_VERTICAL_PADDING = 8.0
LINE_HEIGHT_SAFETY_FACTOR = 1.5
EXCEL_MAX_ROW_HEIGHT = 409.5
DEFAULT_EXCEL_COLUMN_PIXELS = 64
CAPTION_KEYWORDS = (
    "价格对比",
    "走势图",
    "趋势图",
    "统计图",
    "分布图",
    "变化图",
    "结构图",
    "示意图",
    "对比图",
    "柱状图",
    "折线图",
)

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


@dataclass(frozen=True)
class Article:
    title: str
    url: str
    body: str


def normalize_body(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n")]
    return re.sub(r"\n{2,}", "\n", "\n".join(line for line in lines if line))


def is_caption_line(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text)
    if not normalized or len(normalized) > 110:
        return False
    if re.match(r"^(图|表|图表)[\d一二三四五六七八九十]+[：:.\s、-]", normalized):
        return True
    if normalized.startswith("图为"):
        return True
    if re.search(r"(附近|现场|当地|上空|港|站|机场|码头|海峡|街头|厂区|矿区).{0,24}(拍摄|摄|航拍)的", normalized):
        return True
    if re.search(r"(拍摄|摄|航拍)的.{0,36}(照片|图片|画面|场景|船只|火车站|港口|码头|矿区|厂区)", normalized):
        return True
    if re.match(r"^(数据来源|资料来源|来源|注|备注)[：:]", normalized):
        return True
    return any(keyword in normalized for keyword in CAPTION_KEYWORDS)


def remove_caption_lines(text: str) -> str:
    return "\n".join(line for line in normalize_body(text).split("\n") if not is_caption_line(line))


def element_is_centered(element: Any) -> bool:
    for parent in [element, *element.parents]:
        style = parent.attrs.get("style", "") if hasattr(parent, "attrs") else ""
        if "text-align: center" in style or "text-align:center" in style:
            return True
    return False


def element_has_small_caption_style(element: Any) -> bool:
    for node in [element, *element.descendants]:
        attrs = getattr(node, "attrs", {})
        style = attrs.get("style", "") if attrs else ""
        compact_style = re.sub(r"\s+", "", style)
        if "font-size:15px" in compact_style or "font-size:14px" in compact_style:
            return True
    return False


def previous_visible_sibling_has_media(element: Any) -> bool:
    checked = 0
    sibling = element.previous_sibling
    while sibling is not None and checked < 3:
        if getattr(sibling, "name", None):
            text = sibling.get_text(strip=True)
            has_media = bool(sibling.find(["img", "video", "iframe"])) or "nodeleaf" in str(sibling.attrs)
            if has_media:
                return True
            if text:
                checked += 1
        sibling = sibling.previous_sibling
    return False


def should_skip_extracted_text(element: Any, text: str, keep_captions: bool) -> bool:
    if keep_captions:
        return False
    if is_caption_line(text):
        return True
    if len(text) <= 110 and element_is_centered(element):
        if previous_visible_sibling_has_media(element):
            return True
        if element_has_small_caption_style(element) and any(keyword in text for keyword in CAPTION_KEYWORDS):
            return True
    return False


def extract_wechat_article(html_content: str, keep_captions: bool = False) -> tuple[str, str]:
    """Extract title and body text from WeChat Official Account HTML."""
    try:
        from bs4 import BeautifulSoup
    except ModuleNotFoundError as exc:
        raise RuntimeError("HTML extraction requires beautifulsoup4") from exc

    soup = BeautifulSoup(html_content, "html.parser")

    title_tag = soup.find("h1", id="activity-name")
    if not title_tag:
        title_tag = soup.find("h1", class_="rich_media_title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    content_div = soup.find("div", id="js_content")
    if not content_div or "请在微信客户端打开" in html_content:
        return title, ""

    for tag in content_div.find_all(["script", "style", "img", "video", "iframe"]):
        tag.decompose()

    paragraphs: list[str] = []
    for element in content_div.find_all(["p", "section"]):
        if element.find(["p", "section"]):
            continue
        text = element.get_text(strip=True)
        if text and not should_skip_extracted_text(element, text, keep_captions):
            paragraphs.append(text)

    body = normalize_body("\n".join(paragraphs))
    if not keep_captions:
        body = remove_caption_lines(body)
    return title, body


def load_articles(path: Path, keep_captions: bool = False) -> list[Article]:
    with path.open("r", encoding="utf-8") as handle:
        raw_articles: Any = json.load(handle)

    if not isinstance(raw_articles, list) or len(raw_articles) != 5:
        raise ValueError("articles JSON must contain exactly 5 article objects")

    articles: list[Article] = []
    for index, item in enumerate(raw_articles, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"article {index} must be an object")

        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        body = normalize_body(str(item.get("body", "")))
        if not keep_captions:
            body = remove_caption_lines(body)

        missing = [name for name, value in {"title": title, "url": url, "body": body}.items() if not value]
        if missing:
            raise ValueError(f"article {index} is missing: {', '.join(missing)}")

        articles.append(Article(title=title, url=url, body=body))

    return articles


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}tmp{input_path.suffix}")


def column_width_pixels(width: float | None) -> int:
    if width is None:
        return DEFAULT_EXCEL_COLUMN_PIXELS
    return int(((256 * width + int(128 / 7)) / 256) * 7)


def load_body_font() -> Any | None:
    try:
        from PIL import ImageFont
    except ModuleNotFoundError:
        return None

    candidates = [
        Path("/System/Library/Fonts/Supplemental/NotoSansKaithi-Regular.ttf"),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
        Path("/System/Library/Fonts/Supplemental/Kailasa.ttc"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(os.fspath(path), BODY_FONT_PIXELS)
            except OSError:
                continue
    return ImageFont.load_default()


def text_width_pixels(text: str, font: Any) -> int:
    if not text:
        return 0
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0]


def estimated_character_width(char: str) -> float:
    if unicodedata.east_asian_width(char) in {"F", "W"}:
        return 1.0
    if unicodedata.east_asian_width(char) == "A":
        return 0.8
    return 0.55


def count_wrapped_lines_without_font(paragraph: str, width_pixels: int) -> int:
    width_units = max(width_pixels / 7, 20.0)
    line_count = 1
    current_width = 0.0
    for char in paragraph:
        char_width = estimated_character_width(char)
        if current_width and current_width + char_width > width_units:
            line_count += 1
            current_width = char_width
        else:
            current_width += char_width
    return line_count


def count_wrapped_lines(text: str, width_pixels: int, font: Any | None) -> int:
    line_count = 0
    for paragraph in normalize_body(text).split("\n"):
        if not paragraph:
            line_count += 1
            continue
        if font is None:
            line_count += count_wrapped_lines_without_font(paragraph, width_pixels)
            continue

        current = ""
        paragraph_lines = 1
        for char in paragraph:
            candidate = current + char
            if current and text_width_pixels(candidate, font) > width_pixels:
                paragraph_lines += 1
                current = char
            else:
                current = candidate
        line_count += paragraph_lines
    return max(1, line_count)


def qn(name: str) -> str:
    return f"{{{MAIN_NS}}}{name}"


def rqn(name: str) -> str:
    return f"{{{OFFICE_REL_NS}}}{name}"


def workbook_sheet_path(zip_file: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(zip_file.read("xl/workbook.xml"))
    rels = ET.fromstring(zip_file.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets = workbook.find(qn("sheets"))
    if sheets is None:
        raise ValueError("workbook has no sheets collection")

    for sheet in sheets:
        if sheet.attrib.get("name") == SHEET_NAME:
            rel_id = sheet.attrib[rqn("id")]
            return "xl/" + rel_map[rel_id].lstrip("/")
    raise ValueError(f"sheet not found: {SHEET_NAME}")


def worksheet_rels_path(sheet_path: str) -> str:
    sheet_name = sheet_path.rsplit("/", 1)[1]
    return f"xl/worksheets/_rels/{sheet_name}.rels"


def extract_attribute(tag: str, name: str) -> str | None:
    match = re.search(rf'\b{name}="([^"]*)"', tag)
    return match.group(1) if match else None


def set_attribute(tag: str, name: str, value: str) -> str:
    if re.search(rf'\b{name}="[^"]*"', tag):
        return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', tag, count=1)
    return tag[:-1] + f' {name}="{value}">'


def inline_string_cell(ref: str, style: str | None, text: str) -> str:
    attrs = f'r="{ref}"'
    if style is not None:
        attrs += f' s="{style}"'
    space = ' xml:space="preserve"' if text.startswith(" ") or text.endswith(" ") or "\n" in text else ""
    return f'<c {attrs} t="inlineStr"><is><t{space}>{escape(text)}</t></is></c>'


def replace_cell(xml: str, ref: str, text: str) -> str:
    pattern = re.compile(rf'<c\b(?=[^>]*\br="{re.escape(ref)}")[^>]*/>|<c\b(?=[^>]*\br="{re.escape(ref)}")[^>]*>.*?</c>', re.S)
    match = pattern.search(xml)
    if not match:
        raise ValueError(f"cell not found: {ref}")
    style = extract_attribute(match.group(0), "s")
    return xml[: match.start()] + inline_string_cell(ref, style, text) + xml[match.end() :]


def default_row_height(xml: str) -> float:
    match = re.search(r"<sheetFormatPr\b[^>]*>", xml)
    if not match:
        return 15.0
    return float(extract_attribute(match.group(0), "defaultRowHeight") or "15")


def merged_body_width_pixels(xml: str) -> int:
    widths: dict[int, float] = {}
    cols_match = re.search(r"<cols>.*?</cols>", xml, re.S)
    if cols_match:
        for col_match in re.finditer(r"<col\b[^>]*/>", cols_match.group(0)):
            tag = col_match.group(0)
            min_col = int(extract_attribute(tag, "min") or "0")
            max_col = int(extract_attribute(tag, "max") or "0")
            width = float(extract_attribute(tag, "width") or "8.43")
            for index in range(min_col, max_col + 1):
                widths[index] = width
    return sum(column_width_pixels(widths.get(column)) for column in range(BODY_START_COLUMN, BODY_END_COLUMN + 1))


def bottom_up_heights(
    body: str,
    row_count: int,
    width_pixels: int,
    font: Any | None,
    base_row_height: float,
) -> list[float]:
    line_count = count_wrapped_lines(body, width_pixels, font)
    target_height = (line_count * base_row_height * LINE_HEIGHT_SAFETY_FACTOR) + BODY_VERTICAL_PADDING
    heights = [base_row_height] * row_count
    remaining_height = max(0.0, target_height - sum(heights))

    for index in range(row_count - 1, -1, -1):
        add_height = min(remaining_height, EXCEL_MAX_ROW_HEIGHT - heights[index])
        heights[index] += add_height
        remaining_height -= add_height
        if remaining_height <= 0:
            break

    if remaining_height > 0:
        raise ValueError("body text cannot fit within Excel's row height limits")
    return heights


def replace_row_height(xml: str, row_number: int, height: float) -> str:
    pattern = re.compile(rf'<row\b(?=[^>]*\br="{row_number}")[^>]*>')
    match = pattern.search(xml)
    if not match:
        raise ValueError(f"row not found: {row_number}")
    tag = set_attribute(match.group(0), "ht", f"{height:.3f}".rstrip("0").rstrip("."))
    tag = set_attribute(tag, "customHeight", "1")
    return xml[: match.start()] + tag + xml[match.end() :]


def replace_relationship_target(rels_xml: str, rel_id: str, target: str) -> str:
    pattern = re.compile(rf'<Relationship\b(?=[^>]*\bId="{re.escape(rel_id)}")[^>]*/>')
    match = pattern.search(rels_xml)
    if not match:
        raise ValueError(f"relationship not found: {rel_id}")
    tag = set_attribute(match.group(0), "Target", escape(target, {'"': "&quot;"}))
    return rels_xml[: match.start()] + tag + rels_xml[match.end() :]


def hyperlink_relationship_ids(sheet_xml: str) -> dict[str, str]:
    result: dict[str, str] = {}
    hyperlinks_match = re.search(r"<hyperlinks>.*?</hyperlinks>", sheet_xml, re.S)
    if not hyperlinks_match:
        raise ValueError("worksheet has no hyperlinks collection")
    for match in re.finditer(r"<hyperlink\b[^>]*/>", hyperlinks_match.group(0)):
        tag = match.group(0)
        ref = extract_attribute(tag, "ref")
        rel_id = extract_attribute(tag, "r:id")
        if ref and rel_id:
            result[ref] = rel_id
    return result


def patch_worksheet(sheet_xml: bytes, rels_xml: bytes, articles: list[Article]) -> tuple[bytes, bytes]:
    xml = sheet_xml.decode("utf-8")
    rels = rels_xml.decode("utf-8")
    width_pixels = merged_body_width_pixels(xml)
    base_row_height = default_row_height(xml)
    font = load_body_font()
    hyperlink_ids = hyperlink_relationship_ids(xml)

    for article, section in zip(articles, SECTIONS):
        xml = replace_cell(xml, f"D{section['title_row']}", f"《{article.title}》")
        xml = replace_cell(xml, f"D{section['url_row']}", article.url)
        xml = replace_cell(xml, f"D{section['body_row']}", article.body)

        url_ref = f"D{section['url_row']}"
        rels = replace_relationship_target(rels, hyperlink_ids[url_ref], article.url)

        row_count = section["body_end_row"] - section["body_row"] + 1
        heights = bottom_up_heights(article.body, row_count, width_pixels, font, base_row_height)
        for row_number, height in zip(range(section["body_row"], section["body_end_row"] + 1), heights):
            xml = replace_row_height(xml, row_number, height)

    return xml.encode("utf-8"), rels.encode("utf-8")


def update_workbook(input_path: Path, articles: list[Article], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_path, "r") as source:
        sheet_path = workbook_sheet_path(source)
        rels_path = worksheet_rels_path(sheet_path)
        patched_sheet, patched_rels = patch_worksheet(
            source.read(sheet_path),
            source.read(rels_path),
            articles,
        )

        with zipfile.ZipFile(output_path, "w") as target:
            for info in source.infolist():
                data = source.read(info.filename)
                if info.filename == sheet_path:
                    data = patched_sheet
                elif info.filename == rels_path:
                    data = patched_rels
                target.writestr(info, data)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update five viewpoint entries in the coal industry database workbook."
    )
    parser.add_argument("input_workbook", type=Path, help="Path to the source .xlsx workbook")
    parser.add_argument("articles_json", type=Path, help="Path to a JSON file with exactly five articles")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output workbook path. Defaults to the input filename with a tmp suffix.",
    )
    parser.add_argument(
        "--keep-captions",
        action="store_true",
        help="Keep chart/image caption lines in article bodies. Defaults to removing them.",
    )
    args = parser.parse_args()

    articles = load_articles(args.articles_json, keep_captions=args.keep_captions)
    output_path = args.output or default_output_path(args.input_workbook)
    update_workbook(args.input_workbook, articles, output_path)
    print(os.fspath(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
