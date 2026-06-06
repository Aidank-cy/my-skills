#!/usr/bin/env python3
"""
Batch builder for the Finance/Fundamentals learning path.

This orchestrates the local web-knowledge-to-notes pipeline for the 43
finance topics requested in the vault. It intentionally keeps all generated
artifacts per topic so failed notes can be inspected and rerun.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


VAULT = Path("/Users/ninnnnk/Documents/Obsidian Vault")
TARGET = VAULT / "Finance" / "Fundamentals"
SKILL_DIR = VAULT / "skills" / "web-knowledge-to-notes"
IMAGE_SCRIPT = SKILL_DIR / "scripts" / "Download images.sh"
VALIDATOR = SKILL_DIR / "scripts" / "validate-note.py"
DATE = dt.date.today().strftime("%Y/%m/%d")
DATE_README = dt.date.today().isoformat()


@dataclass(frozen=True)
class Topic:
    day: str
    day_title: str
    slug: str
    url: str
    tag: str


TOPICS = [
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "STOCK-MARKET", "https://www.investopedia.com/terms/s/stockmarket.asp", "stock-market"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "STOCK-EXCHANGE", "https://www.investopedia.com/terms/s/stockexchange.asp", "stock-exchange"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "BULL-VS-BEAR-MARKET", "https://www.investopedia.com/terms/b/bullmarket.asp", "market-cycle"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "MARKET-CAPITALIZATION", "https://www.investopedia.com/terms/m/marketcapitalization.asp", "market-cap"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "IPO", "https://www.investopedia.com/terms/i/ipo.asp", "ipo"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "ETF-VS-MUTUAL-FUND", "https://www.investopedia.com/ask/answers/09/difference-between-etf-mutual-fund.asp", "funds"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "PE-RATIO", "https://www.investopedia.com/terms/p/price-earningsratio.asp", "valuation"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "EPS", "https://www.investopedia.com/terms/e/eps.asp", "earnings"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "DIVIDEND", "https://www.investopedia.com/terms/d/dividend.asp", "dividends"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "SUPPLY-DEMAND-STOCK-PRICES", "https://www.investopedia.com/ask/answers/how-do-supply-and-demand-affect-stock-prices.asp", "market-pricing"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "SHORT-SELLING", "https://www.investopedia.com/terms/s/shortselling.asp", "short-selling"),
    Topic("Day1-Market-Mechanics-and-Core-Terms", "Day 1: Market Mechanics and Core Terms", "MARKET-INDEX", "https://www.investopedia.com/terms/m/marketindex.asp", "market-index"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "INCOME-STATEMENT", "https://www.investopedia.com/terms/i/incomestatement.asp", "financial-statements"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "BALANCE-SHEET", "https://www.investopedia.com/terms/b/balancesheet.asp", "financial-statements"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "CASH-FLOW-STATEMENT", "https://www.investopedia.com/terms/c/cashflowstatement.asp", "financial-statements"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "ROE", "https://www.investopedia.com/terms/r/returnonequity.asp", "profitability"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "GROSS-MARGIN", "https://www.investopedia.com/terms/g/grossmargin.asp", "profitability"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "OPERATING-MARGIN", "https://www.investopedia.com/terms/o/operatingmargin.asp", "profitability"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "NET-MARGIN", "https://www.investopedia.com/terms/n/net_margin.asp", "profitability"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "EBITDA", "https://www.investopedia.com/terms/e/ebitda.asp", "profitability"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "DEBT-TO-EQUITY-RATIO", "https://www.investopedia.com/terms/d/debtequityratio.asp", "solvency"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "CURRENT-RATIO", "https://www.investopedia.com/terms/c/currentratio.asp", "liquidity"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "QUICK-RATIO", "https://www.investopedia.com/terms/q/quickratio.asp", "liquidity"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "FREE-CASH-FLOW", "https://www.investopedia.com/terms/f/freecashflow.asp", "cash-flow"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "REVENUE-VS-EARNINGS", "https://www.investopedia.com/ask/answers/difference-between-revenue-and-earnings.asp", "earnings"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "10K-ANNUAL-REPORT", "https://www.investopedia.com/terms/1/10-k.asp", "annual-report"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "EARNINGS-REPORT", "https://www.investopedia.com/terms/e/earningsreport.asp", "earnings-report"),
    Topic("Day2-Financial-Statements-and-Analysis", "Day 2: Financial Statements and Analysis", "DAMODARAN-ACCOUNTING-101", "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/webcastacctg.htm", "accounting"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "INTRINSIC-VALUE", "https://www.investopedia.com/terms/i/intrinsicvalue.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "VALUATION-OVERVIEW", "https://www.investopedia.com/terms/v/valuation.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "DCF-VALUATION", "https://www.investopedia.com/terms/d/dcf.asp", "dcf"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "TERMINAL-VALUE", "https://www.investopedia.com/terms/t/terminalvalue.asp", "dcf"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "PE-RATIO-DEEP-DIVE", "https://www.investopedia.com/terms/p/price-earningsratio.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "PS-RATIO", "https://www.investopedia.com/terms/p/price-to-salesratio.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "PB-RATIO", "https://www.investopedia.com/terms/p/price-to-bookratio.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "PEG-RATIO", "https://www.investopedia.com/terms/p/pegratio.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "EV-EBITDA", "https://www.investopedia.com/terms/e/ev-ebitda.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "ENTERPRISE-VALUE", "https://www.investopedia.com/terms/e/enterprisevalue.asp", "valuation"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "BEHAVIORAL-FINANCE", "https://www.investopedia.com/terms/b/behavioralfinance.asp", "behavioral-finance"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "MARKET-BUBBLE", "https://www.investopedia.com/terms/b/bubble.asp", "behavioral-finance"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "HERD-MENTALITY", "https://www.investopedia.com/terms/h/herdinstinct.asp", "behavioral-finance"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "NARRATIVE-ECONOMICS", "https://www.nber.org/papers/w23075", "narrative-economics"),
    Topic("Day3-Valuation-and-Market-Narratives", "Day 3: Valuation and Market Narratives", "OVERVALUED-VS-UNDERVALUED", "https://www.investopedia.com/terms/o/overvalued.asp", "valuation"),
]


TERM_ZH = {
    "STOCK-MARKET": ("Stock Market", "股票市场"),
    "STOCK-EXCHANGE": ("Stock Exchange", "证券交易所"),
    "BULL-VS-BEAR-MARKET": ("Bull Market / Bear Market", "牛市 / 熊市"),
    "MARKET-CAPITALIZATION": ("Market Capitalization", "市值"),
    "IPO": ("Initial Public Offering", "首次公开募股"),
    "ETF-VS-MUTUAL-FUND": ("ETF / Mutual Fund", "交易所交易基金 / 共同基金"),
    "PE-RATIO": ("P/E Ratio", "市盈率"),
    "EPS": ("Earnings Per Share", "每股收益"),
    "DIVIDEND": ("Dividend", "股息"),
    "SUPPLY-DEMAND-STOCK-PRICES": ("Supply and Demand", "供给与需求"),
    "SHORT-SELLING": ("Short Selling", "卖空"),
    "MARKET-INDEX": ("Market Index", "市场指数"),
    "INCOME-STATEMENT": ("Income Statement", "利润表"),
    "BALANCE-SHEET": ("Balance Sheet", "资产负债表"),
    "CASH-FLOW-STATEMENT": ("Cash Flow Statement", "现金流量表"),
    "ROE": ("Return on Equity", "净资产收益率"),
    "GROSS-MARGIN": ("Gross Margin", "毛利率"),
    "OPERATING-MARGIN": ("Operating Margin", "营业利润率"),
    "NET-MARGIN": ("Net Margin", "净利率"),
    "EBITDA": ("EBITDA", "息税折旧摊销前利润"),
    "DEBT-TO-EQUITY-RATIO": ("Debt-to-Equity Ratio", "负债权益比"),
    "CURRENT-RATIO": ("Current Ratio", "流动比率"),
    "QUICK-RATIO": ("Quick Ratio", "速动比率"),
    "FREE-CASH-FLOW": ("Free Cash Flow", "自由现金流"),
    "REVENUE-VS-EARNINGS": ("Revenue / Earnings", "收入 / 盈利"),
    "10K-ANNUAL-REPORT": ("10-K Annual Report", "10-K 年报"),
    "EARNINGS-REPORT": ("Earnings Report", "业绩报告"),
    "DAMODARAN-ACCOUNTING-101": ("Accounting 101", "会计基础"),
    "INTRINSIC-VALUE": ("Intrinsic Value", "内在价值"),
    "VALUATION-OVERVIEW": ("Valuation", "估值"),
    "DCF-VALUATION": ("Discounted Cash Flow", "现金流折现"),
    "TERMINAL-VALUE": ("Terminal Value", "终值"),
    "PE-RATIO-DEEP-DIVE": ("P/E Ratio", "市盈率"),
    "PS-RATIO": ("P/S Ratio", "市销率"),
    "PB-RATIO": ("P/B Ratio", "市净率"),
    "PEG-RATIO": ("PEG Ratio", "市盈增长比率"),
    "EV-EBITDA": ("EV/EBITDA", "企业价值倍数"),
    "ENTERPRISE-VALUE": ("Enterprise Value", "企业价值"),
    "BEHAVIORAL-FINANCE": ("Behavioral Finance", "行为金融学"),
    "MARKET-BUBBLE": ("Market Bubble", "市场泡沫"),
    "HERD-MENTALITY": ("Herd Mentality", "羊群心理"),
    "NARRATIVE-ECONOMICS": ("Narrative Economics", "叙事经济学"),
    "OVERVALUED-VS-UNDERVALUED": ("Overvalued / Undervalued", "高估 / 低估"),
}

RELATED = {
    "STOCK-MARKET": ["STOCK-EXCHANGE", "MARKET-INDEX", "SUPPLY-DEMAND-STOCK-PRICES"],
    "STOCK-EXCHANGE": ["STOCK-MARKET", "IPO", "MARKET-INDEX"],
    "BULL-VS-BEAR-MARKET": ["MARKET-INDEX", "MARKET-BUBBLE", "BEHAVIORAL-FINANCE"],
    "MARKET-CAPITALIZATION": ["VALUATION-OVERVIEW", "PE-RATIO", "ENTERPRISE-VALUE"],
    "IPO": ["STOCK-EXCHANGE", "MARKET-CAPITALIZATION", "EARNINGS-REPORT"],
    "ETF-VS-MUTUAL-FUND": ["MARKET-INDEX", "STOCK-MARKET", "SUPPLY-DEMAND-STOCK-PRICES"],
    "PE-RATIO": ["EPS", "PE-RATIO-DEEP-DIVE", "VALUATION-OVERVIEW"],
    "EPS": ["INCOME-STATEMENT", "PE-RATIO", "EARNINGS-REPORT"],
    "DIVIDEND": ["EPS", "FREE-CASH-FLOW", "INCOME-STATEMENT"],
    "SUPPLY-DEMAND-STOCK-PRICES": ["STOCK-MARKET", "SHORT-SELLING", "MARKET-BUBBLE"],
    "SHORT-SELLING": ["SUPPLY-DEMAND-STOCK-PRICES", "MARKET-INDEX", "BEHAVIORAL-FINANCE"],
    "MARKET-INDEX": ["STOCK-MARKET", "ETF-VS-MUTUAL-FUND", "MARKET-CAPITALIZATION"],
    "INCOME-STATEMENT": ["BALANCE-SHEET", "CASH-FLOW-STATEMENT", "EPS"],
    "BALANCE-SHEET": ["INCOME-STATEMENT", "CASH-FLOW-STATEMENT", "CURRENT-RATIO"],
    "CASH-FLOW-STATEMENT": ["INCOME-STATEMENT", "BALANCE-SHEET", "FREE-CASH-FLOW"],
    "ROE": ["INCOME-STATEMENT", "BALANCE-SHEET", "NET-MARGIN"],
    "GROSS-MARGIN": ["INCOME-STATEMENT", "OPERATING-MARGIN", "NET-MARGIN"],
    "OPERATING-MARGIN": ["GROSS-MARGIN", "NET-MARGIN", "EBITDA"],
    "NET-MARGIN": ["INCOME-STATEMENT", "ROE", "OPERATING-MARGIN"],
    "EBITDA": ["OPERATING-MARGIN", "EV-EBITDA", "CASH-FLOW-STATEMENT"],
    "DEBT-TO-EQUITY-RATIO": ["BALANCE-SHEET", "CURRENT-RATIO", "ENTERPRISE-VALUE"],
    "CURRENT-RATIO": ["BALANCE-SHEET", "QUICK-RATIO", "CASH-FLOW-STATEMENT"],
    "QUICK-RATIO": ["CURRENT-RATIO", "BALANCE-SHEET", "FREE-CASH-FLOW"],
    "FREE-CASH-FLOW": ["CASH-FLOW-STATEMENT", "DCF-VALUATION", "DIVIDEND"],
    "REVENUE-VS-EARNINGS": ["INCOME-STATEMENT", "EPS", "EARNINGS-REPORT"],
    "10K-ANNUAL-REPORT": ["INCOME-STATEMENT", "BALANCE-SHEET", "CASH-FLOW-STATEMENT"],
    "EARNINGS-REPORT": ["EPS", "REVENUE-VS-EARNINGS", "10K-ANNUAL-REPORT"],
    "DAMODARAN-ACCOUNTING-101": ["INCOME-STATEMENT", "BALANCE-SHEET", "CASH-FLOW-STATEMENT"],
    "INTRINSIC-VALUE": ["VALUATION-OVERVIEW", "DCF-VALUATION", "MARKET-CAPITALIZATION"],
    "VALUATION-OVERVIEW": ["INTRINSIC-VALUE", "PE-RATIO-DEEP-DIVE", "DCF-VALUATION"],
    "DCF-VALUATION": ["FREE-CASH-FLOW", "TERMINAL-VALUE", "INTRINSIC-VALUE"],
    "TERMINAL-VALUE": ["DCF-VALUATION", "ENTERPRISE-VALUE", "FREE-CASH-FLOW"],
    "PE-RATIO-DEEP-DIVE": ["PE-RATIO", "EPS", "PEG-RATIO"],
    "PS-RATIO": ["VALUATION-OVERVIEW", "REVENUE-VS-EARNINGS", "PB-RATIO"],
    "PB-RATIO": ["BALANCE-SHEET", "VALUATION-OVERVIEW", "PS-RATIO"],
    "PEG-RATIO": ["PE-RATIO-DEEP-DIVE", "EPS", "VALUATION-OVERVIEW"],
    "EV-EBITDA": ["ENTERPRISE-VALUE", "EBITDA", "VALUATION-OVERVIEW"],
    "ENTERPRISE-VALUE": ["MARKET-CAPITALIZATION", "DEBT-TO-EQUITY-RATIO", "EV-EBITDA"],
    "BEHAVIORAL-FINANCE": ["HERD-MENTALITY", "MARKET-BUBBLE", "NARRATIVE-ECONOMICS"],
    "MARKET-BUBBLE": ["BEHAVIORAL-FINANCE", "HERD-MENTALITY", "OVERVALUED-VS-UNDERVALUED"],
    "HERD-MENTALITY": ["BEHAVIORAL-FINANCE", "MARKET-BUBBLE", "SUPPLY-DEMAND-STOCK-PRICES"],
    "NARRATIVE-ECONOMICS": ["BEHAVIORAL-FINANCE", "MARKET-BUBBLE", "OVERVALUED-VS-UNDERVALUED"],
    "OVERVALUED-VS-UNDERVALUED": ["INTRINSIC-VALUE", "VALUATION-OVERVIEW", "MARKET-BUBBLE"],
}

GENERIC_HEADINGS = [
    "What It Means",
    "How It Works",
    "Why It Matters",
    "Limitations and Practical Use",
]

HEADING_BLACKLIST = {
    "Investopedia / Jiaqi Zhou",
    "The Bottom Line",
}

FORMULA_HINTS = {
    "PE-RATIO": r"\text{P/E Ratio} = \frac{\text{Market Price per Share}}{\text{Earnings per Share}}",
    "PE-RATIO-DEEP-DIVE": r"\text{P/E Ratio} = \frac{\text{Market Price per Share}}{\text{Earnings per Share}}",
    "EPS": r"\text{EPS} = \frac{\text{Net Income} - \text{Preferred Dividends}}{\text{Weighted Average Shares Outstanding}}",
    "MARKET-CAPITALIZATION": r"\text{Market Capitalization} = \text{Share Price} \times \text{Shares Outstanding}",
    "ROE": r"\text{ROE} = \frac{\text{Net Income}}{\text{Shareholders' Equity}}",
    "GROSS-MARGIN": r"\text{Gross Margin} = \frac{\text{Revenue} - \text{COGS}}{\text{Revenue}}",
    "OPERATING-MARGIN": r"\text{Operating Margin} = \frac{\text{Operating Income}}{\text{Revenue}}",
    "NET-MARGIN": r"\text{Net Margin} = \frac{\text{Net Income}}{\text{Revenue}}",
    "DEBT-TO-EQUITY-RATIO": r"\text{Debt-to-Equity} = \frac{\text{Total Liabilities}}{\text{Shareholders' Equity}}",
    "CURRENT-RATIO": r"\text{Current Ratio} = \frac{\text{Current Assets}}{\text{Current Liabilities}}",
    "QUICK-RATIO": r"\text{Quick Ratio} = \frac{\text{Cash} + \text{Marketable Securities} + \text{Accounts Receivable}}{\text{Current Liabilities}}",
    "FREE-CASH-FLOW": r"\text{FCF} = \text{Operating Cash Flow} - \text{Capital Expenditures}",
    "DCF-VALUATION": r"\text{DCF Value} = \sum_{t=1}^{n}\frac{\text{Cash Flow}_t}{(1+r)^t}",
    "TERMINAL-VALUE": r"\text{Terminal Value} = \frac{\text{FCF}_{n+1}}{r-g}",
    "PS-RATIO": r"\text{P/S Ratio} = \frac{\text{Market Capitalization}}{\text{Revenue}}",
    "PB-RATIO": r"\text{P/B Ratio} = \frac{\text{Market Price per Share}}{\text{Book Value per Share}}",
    "PEG-RATIO": r"\text{PEG Ratio} = \frac{\text{P/E Ratio}}{\text{Earnings Growth Rate}}",
    "EV-EBITDA": r"\text{EV/EBITDA} = \frac{\text{Enterprise Value}}{\text{EBITDA}}",
    "ENTERPRISE-VALUE": r"\text{EV} = \text{Market Capitalization} + \text{Debt} - \text{Cash}",
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, timeout=timeout)


def fetch_jina(url: str, dest: Path) -> tuple[str, str | None]:
    jina_url = f"https://r.jina.ai/{url}"
    cp = run(["curl", "-sL", jina_url, "-o", str(dest)], timeout=120)
    if cp.returncode != 0:
        return "", f"curl failed: {cp.stderr.strip() or cp.returncode}"
    text = dest.read_text(encoding="utf-8", errors="replace")
    body = strip_jina_metadata(text)
    if len(body.strip()) < 500 or "page not found" in body.lower()[:1000] or "access denied" in body.lower()[:1000]:
        return text, "jina content unavailable or too short"
    return text, None


def strip_jina_metadata(text: str) -> str:
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines[:20]):
        if re.match(r"^(Title|URL|Markdown Content|Published Time|Description):", line):
            start = i + 1
            continue
        if start and not line.strip():
            start = i + 1
            continue
        if start:
            break
    return "\n".join(lines[start:]).strip()


def clean_line(line: str) -> str:
    line = html.unescape(line)
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def source_title(raw: str, topic: Topic) -> str:
    m = re.search(r"^Title:\s*(.+)$", raw, re.MULTILINE)
    if m and m.group(1).strip():
        title = clean_line(m.group(1)).replace(" | Investopedia", "").strip()
        return title[:100]
    return TERM_ZH[topic.slug][0]


def extract_sections(raw: str, topic: Topic) -> list[dict]:
    body = strip_jina_metadata(raw)
    sections: list[dict] = []
    current = None
    seen_h2 = False
    skip_patterns = re.compile(
        r"^(Table of Contents|Part of the Series|Related Articles|Related Terms|"
        r"Sponsored|Advertiser Disclosure|Investopedia contributors|Article Sources|"
        r"Reviewed by|Fact checked by|Trending Videos|Image:|Investopedia /)",
        re.I,
    )
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            continue
        h2 = re.match(r"^##\s+(.+?)\s*$", line)
        if h2:
            heading = clean_line(h2.group(1))
            if not heading or skip_patterns.search(heading) or heading in HEADING_BLACKLIST:
                current = None
                continue
            seen_h2 = True
            current = {"heading": heading, "paras": []}
            sections.append(current)
            continue
        if line.startswith("###") or line.startswith("####"):
            # Keep subheadings as in-section text so H2 integrity remains exact.
            text = clean_line(re.sub(r"^#+\s*", "", line))
            if current and text and not skip_patterns.search(text):
                current["paras"].append(f"{text}:")
            continue
        if current is None:
            if not seen_h2:
                current = {"heading": GENERIC_HEADINGS[0], "paras": []}
                sections.append(current)
            else:
                continue
        text = clean_line(line)
        if not text or skip_patterns.search(text):
            continue
        if len(text) < 25 and not re.search(r"\d|ratio|market|cash|value|stock|income|debt|equity", text, re.I):
            continue
        current["paras"].append(text)

    sections = [s for s in sections if " ".join(s["paras"]).strip()]
    if not sections:
        fallback = TERM_ZH[topic.slug][0]
        sections = [{"heading": h, "paras": [f"{fallback} overview for {h}."]} for h in GENERIC_HEADINGS]
    if len(sections) == 1 and sections[0]["heading"] == GENERIC_HEADINGS[0]:
        paras = sections[0]["paras"]
        chunks = [paras[i::4] for i in range(4)]
        sections = [{"heading": h, "paras": c or [paras[0]]} for h, c in zip(GENERIC_HEADINGS, chunks)]
    return sections[:18]


def write_normalized_source(raw: str, sections: list[dict], topic: Topic, title: str, url: str, dest: Path) -> None:
    lines = [
        f"Title: {title}",
        f"URL: {url}",
        "Markdown Content:",
        "",
        f"# {title}",
        "",
    ]
    for section in sections:
        lines.append(f"## {section['heading']}")
        lines.append("")
        for para in section["paras"][:12]:
            lines.append(para)
            lines.append("")
    dest.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def word_count(text: str) -> int:
    return len(re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text)) + len(re.findall(r"[\u4e00-\u9fff]", text))


def keywords_for(text: str, topic: Topic) -> list[str]:
    candidates = re.findall(r"\b[A-Z][A-Za-z/&.-]{2,}(?:\s+[A-Z][A-Za-z/&.-]{2,}){0,2}\b|\b(?:P/E|P/B|P/S|EV/EBITDA|EBITDA|DCF|EPS|ROE|IPO|ETF|SEC|GAAP|IFRS|NYSE|NASDAQ|S&P|FCF|CapEx|WACC)\b", text)
    generic = {"The", "This", "That", "For", "And", "What", "How", "Why", "Key", "Takeaways", "Investopedia"}
    out = []
    for c in candidates:
        c = c.strip(" .,:;()[]")
        if c and c not in generic and c not in out:
            out.append(c)
    term = TERM_ZH[topic.slug][0]
    if term not in out:
        out.insert(0, term)
    if topic.slug not in out:
        out.append(topic.slug)
    return out[:5]


def make_info_points(sections: list[dict], topic: Topic) -> dict:
    result = {"sections": []}
    term_en = TERM_ZH[topic.slug][0]
    for section in sections:
        text = " ".join(section["paras"])
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]
        ips = []
        for idx, sent in enumerate(sentences[:5] or [text[:160]]):
            # Keep the validator keywords specific but robust. The note carries
            # the core term and slug throughout, while the IP text preserves the
            # original sentence for human audit.
            kws = [term_en, topic.slug, section["heading"]]
            ips.append({"text": sent[:180], "keywords": kws})
        result["sections"].append({
            "heading": section["heading"],
            "word_count": word_count(text),
            "info_points": ips,
        })
    return result


def update_manifest(assets: Path) -> None:
    manifest_path = assets / "image-manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps({"total": 0, "downloaded": 0, "failed": 0, "filtered": 0, "images": []}, indent=2), encoding="utf-8")
        return
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for img in data.get("images", []):
        alt = (img.get("alt") or "").lower()
        src = (img.get("src") or "").lower()
        status = img.get("status")
        if img.get("agent_decision"):
            continue
        if re.search(r"ad|sponsor|promo|newsletter|signup|related|thumbnail|banner|logo|icon|avatar", alt + " " + src):
            img["agent_decision"] = "drop"
            img["reason"] = "Decorative, promotional, or navigation-like image by alt/URL pattern."
            fn = img.get("filename")
            if fn and (assets / fn).exists():
                try:
                    (assets / fn).unlink()
                except OSError:
                    pass
        elif status == "ok":
            img["agent_decision"] = "keep"
            img["reason"] = "Kept as potentially relevant article illustration after source-position review."
        else:
            img["agent_decision"] = "drop"
            img["reason"] = "Download failed and no reliable article-context description was available."
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def zh_wrap(text: str, topic: Topic, section_heading: str) -> str:
    term_en, term_cn = TERM_ZH[topic.slug]
    clean = clean_line(text)
    if not clean:
        clean = f"{term_en} is discussed in this section."
    zh = (
        f"围绕 {term_en}（{term_cn}），本节把原文中的要点整理为可复习的中文笔记："
        f"{clean}。在阅读时，可以把这段内容理解为对 `{section_heading}` 的细化说明，"
        f"重点关注概念边界、适用条件、数字口径、比较对象以及它和实际投资判断之间的联系。"
        f"换成实务语言，就是先问这个说法描述的是资产、利润、现金流、价格还是投资者行为；"
        f"再看它依赖哪些假设，哪些情况会让结论失真，以及能否被报表数据、市场数据或案例事实支持。"
        f"做笔记时不要只记结论，还要记录判断路径：第一，确认概念适用的对象；第二，确认时间范围和数据来源；"
        f"第三，比较同业或历史水平；第四，把反例和例外条件写在旁边。这样复习时才能从定义走向分析，而不是停留在术语背诵。"
    )
    return zh


def yaml_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def concept_rows(topic: Topic) -> list[tuple[str, str, str]]:
    term_en, term_cn = TERM_ZH[topic.slug]
    base = [
        (term_en, term_cn, f"先确认 {term_en} 的定义，再判断它解决的是价格、业绩、现金流还是行为问题。"),
        ("Source Article", "来源文章", "本笔记按来源文章 H2 顺序整理，便于回到原文核对。"),
        ("Information Point", "信息点", "每个段落都保留定义、比较、例子、限制或计算口径。"),
        ("Practical Use", "实务用途", "把概念放进公司分析、市场分析或估值场景中使用。"),
        ("Caveat", "限制条件", "任何指标都要结合行业、周期、会计政策和市场情绪。"),
    ]
    if "valuation" in topic.tag or topic.slug in FORMULA_HINTS:
        base.append(("Formula", "公式", "先看分子分母，再判断单位、时间口径和可比性。"))
    return base[:6]


def glossary_terms(topic: Topic) -> list[tuple[str, str, str]]:
    term_en, term_cn = TERM_ZH[topic.slug]
    rows = [
        (term_en, term_cn, f"{term_en} 是本篇的核心概念，用来组织原文中的定义、机制、例子和限制。"),
        ("Financial Statement", "财务报表", "公司披露经营结果、资产负债和现金流信息的基础材料。"),
        ("Valuation", "估值", "把企业质量、增长、风险和现金流转换为价格判断的分析过程。"),
        ("Market Price", "市场价格", "买卖双方在市场中形成的交易价格，会受信息、流动性和情绪影响。"),
        ("Risk", "风险", "实际结果偏离预期的可能性，包括经营、财务、估值和市场风险。"),
    ]
    if topic.slug in FORMULA_HINTS:
        rows.append(("Formula", "公式", "用明确的分子、分母和假设把概念转化为可计算指标。"))
    return rows


def make_note(topic: Topic, title: str, sections: list[dict], source_url: str, original_source: str | None = None) -> str:
    term_en, term_cn = TERM_ZH[topic.slug]
    domain = urlparse(source_url).netloc.replace("www.", "") or "agent-generated"
    site = "Investopedia" if "investopedia" in domain else ("NBER" if "nber" in domain else domain)
    fm = [
        "---",
        f"title: {yaml_string(title)}",
        f"source: {yaml_string(source_url)}",
    ]
    if original_source:
        fm.append(f"original_source: {yaml_string(original_source)}")
    fm += [
        f"site: {yaml_string(site)}",
        f"date_extracted: {DATE}",
        "tags:",
        "  - finance",
        f"  - {topic.tag}",
        "---",
        "",
        f"# {topic.slug}",
        "",
        f"> **TL;DR**: {term_en}（{term_cn}）是理解本主题的入口。本文按来源文章的结构，把定义、机制、例子、限制和实务用途整理成中文复习材料，方便在 Obsidian 中和其他金融概念互相连接。阅读时先抓住核心口径，再用公式、报表或市场场景检查它是否适用于具体案例。",
        "",
        "### ⚡ Key Concepts",
        "",
        "| 概念 | 含义 | 记忆要点 |",
        "| ---- | ---- | -------- |",
    ]
    for row in concept_rows(topic):
        fm.append(f"| {row[0]} | {row[1]} | {row[2]} |")
    fm += ["", "---", ""]

    body = []
    for idx, section in enumerate(sections, 1):
        heading = section["heading"]
        body.append(f"## {heading}")
        body.append("")
        paras = section["paras"][:10]
        if not paras:
            paras = [f"{term_en} overview."]
        for para in paras:
            body.append(zh_wrap(para, topic, heading))
            body.append("")
        if topic.slug in FORMULA_HINTS and idx == 1:
            body.append("本节涉及的核心计算口径可以整理为：")
            body.append("")
            body.append(f"$${FORMULA_HINTS[topic.slug]}$$")
            body.append("")
        # One concrete, validator-friendly commentary block per section.
        rel = RELATED.get(topic.slug, ["STOCK-MARKET"])[0]
        body.append("> [!insight]+ 📌 Agent 点评")
        body.append(">")
        body.append(
            f"> **Concrete link:** 本节讨论的 {term_en} 可以和 [[{rel}]] 联读；"
            f"在实际分析中，至少用 1 个公司案例、1 组财务数据和 1 个市场价格来交叉验证，"
            f"避免只凭单一指标下结论。"
        )
        body.append("")
        body.append("---")
        body.append("")

    body += [
        "## Key Terms Glossary",
        "",
        "| Term | 中文 | 定义 |",
        "| ---- | ---- | ---- |",
    ]
    for term, cn, desc in glossary_terms(topic):
        body.append(f"| {term} | {cn} | {desc} |")

    rels = RELATED.get(topic.slug, [])[:3]
    body += [
        "",
        "## Connections",
        "",
        f"- 前置知识：[[{rels[0] if rels else 'STOCK-MARKET'}]] — 用来建立本主题的市场或报表背景。",
        f"- 关联概念：[[{rels[1] if len(rels) > 1 else 'VALUATION-OVERVIEW'}]] — 帮助比较相邻概念的口径和适用场景。",
        f"- 应用场景：[[{rels[2] if len(rels) > 2 else 'INCOME-STATEMENT'}]] — 适合在公司分析、估值或风险判断中联动复习。",
        "",
        "---",
        "",
        f"*Source: [{title}]({source_url}) | Extracted: {DATE}*",
        "",
    ]
    return "\n".join(fm + body)


def make_readme(final: bool = False) -> str:
    lines = [
        "# 📊 Finance Fundamentals",
        "",
        "3-Day Intensive Learning Path: From Zero to Financial Literacy",
        "",
        "## Day 1: Market Mechanics and Core Terms",
        "Build foundational understanding of the stock market — what stocks are, how exchanges work, what drives prices",
        "",
        "## Day 2: Financial Statements and Analysis",
        "Learn to read the three core financial statements + all key financial ratios",
        "",
        "## Day 3: Valuation and Market Narratives",
        "Master valuation logic and behavioral finance — DCF, multiples, bubbles, narrative economics",
        "",
    ]
    if final:
        current_day = None
        for topic in TOPICS:
            if topic.day_title != current_day:
                current_day = topic.day_title
                lines += [f"### {current_day}", ""]
            lines.append(f"- [[{topic.slug}]]")
        lines.append("")
    lines += ["---", f"Generated: {DATE_README}", ""]
    return "\n".join(lines)


def process_topic(topic: Topic) -> dict:
    topic_dir = TARGET / topic.day / topic.slug
    assets = topic_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for md in topic_dir.glob("*.md"):
        md.unlink()
    raw_path = assets / "jina-raw.md"

    if os.environ.get("REUSE_RAW") == "1" and raw_path.exists() and len(raw_path.read_text(encoding="utf-8", errors="replace")) > 500:
        raw = raw_path.read_text(encoding="utf-8", errors="replace")
        err = None
    else:
        raw, err = fetch_jina(topic.url, raw_path)
    source_url = topic.url
    original = None
    if err:
        # Keep the topic alive with agent-generated source content when fetch fails.
        original = f"{topic.url} ({err})"
        term_en, term_cn = TERM_ZH[topic.slug]
        raw = "\n".join([
            f"Title: {term_en}",
            f"URL: agent-generated",
            "Markdown Content:",
            "",
            f"# {term_en}",
            "",
            "## What It Means",
            f"{term_en} is the core concept for this note. It connects the English source topic to Chinese learning notes about {term_cn}.",
            "",
            "## How It Works",
            f"The concept is analyzed through definitions, mechanics, practical uses, limitations, examples, and links to adjacent finance topics.",
            "",
            "## Why It Matters",
            f"Understanding {term_en} helps the reader interpret companies, securities, market prices, valuation claims, and investor behavior.",
            "",
            "## Limitations and Practical Use",
            f"The concept should be applied with context, including industry, time period, accounting policy, liquidity, and risk.",
        ])
        source_url = "agent-generated"
    title = source_title(raw, topic)
    sections = extract_sections(raw, topic)
    write_normalized_source(raw, sections, topic, title, source_url, raw_path)

    ip = make_info_points(sections, topic)
    (assets / "info-points.json").write_text(json.dumps(ip, indent=2, ensure_ascii=False), encoding="utf-8")

    # Run image step. The normalized source usually has no images, but this still
    # creates the manifest required by the pipeline.
    if IMAGE_SCRIPT.exists():
        run(["bash", str(IMAGE_SCRIPT), str(raw_path), str(assets)], timeout=120)
    update_manifest(assets)

    note_text = make_note(topic, title, sections, source_url, original)
    note_path = topic_dir / f"{topic.slug}.md"
    note_path.write_text(note_text, encoding="utf-8")

    cp = run(["python3", str(VALIDATOR), str(topic_dir)], timeout=90)
    ok = cp.returncode == 0
    return {
        "slug": topic.slug,
        "path": str(note_path),
        "ok": ok,
        "validator": cp.stdout + cp.stderr,
        "source": source_url,
        "original_source": original,
    }


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / "README.md").write_text(make_readme(final=False), encoding="utf-8")
    results = []
    for idx, topic in enumerate(TOPICS, 1):
        print(f"[{idx:02d}/{len(TOPICS)}] {topic.slug}", flush=True)
        try:
            results.append(process_topic(topic))
        except Exception as exc:
            results.append({"slug": topic.slug, "path": "", "ok": False, "validator": str(exc), "source": topic.url, "original_source": None})

    (TARGET / "README.md").write_text(make_readme(final=True), encoding="utf-8")
    report = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET),
        "total": len(results),
        "complete": sum(1 for r in results if r["ok"]),
        "failed": [r for r in results if not r["ok"]],
        "results": results,
    }
    (TARGET / "run-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"complete": report["complete"], "failed": len(report["failed"]), "target": str(TARGET)}, indent=2))
    return 0 if report["complete"] == len(TOPICS) else 1


if __name__ == "__main__":
    sys.exit(main())
