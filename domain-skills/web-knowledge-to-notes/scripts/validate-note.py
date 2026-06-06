#!/usr/bin/env python3
"""
validate-note.py — Hard validation gate for web-knowledge-to-notes.

Run after the agent assembles the final note. Any FAIL result means
the note does not meet skill requirements and must be fixed.

Usage:
    python3 validate-note.py <TOPIC_FOLDER>

Expects:
    TOPIC_FOLDER/
    ├── *.md                 (the final note — exactly one .md file)
    └── assets/
        ├── jina-raw.md      (or manual-input.md)
        ├── image-manifest.json
        └── info-points.json (agent-generated IP inventory)

Exit codes:
    0 = all checks passed
    1 = one or more checks failed (details printed)
"""

import json
import os
import re
import sys
import yaml
from pathlib import Path


# ─── Helpers ───

def extract_headings(text, level=2):
    """Extract markdown headings of a given level."""
    pattern = rf'^{"#" * level}\s+(.+)$'
    return [m.group(1).strip() for m in re.finditer(pattern, text, re.MULTILINE)]


def split_sections(text, level=2):
    """Split markdown into sections by heading level.
    Returns list of (heading, body_text) tuples."""
    pattern = rf'^({"#" * level}\s+.+)$'
    parts = re.split(pattern, text, flags=re.MULTILINE)

    sections = []
    i = 1  # parts[0] is content before first heading
    while i < len(parts):
        heading = parts[i].lstrip("#").strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((heading, body))
        i += 2
    return sections


def word_count(text):
    """Count words — handles English and CJK mixed text."""
    # Count English words
    english = len(re.findall(r'[a-zA-Z]+(?:\'[a-zA-Z]+)?', text))
    # Count CJK characters (each counts as ~1 word)
    cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    return english + cjk


def strip_callouts(text):
    """Remove > [!insight] callout blocks from section body,
    so word count only measures article content, not commentary."""
    lines = text.split('\n')
    result = []
    in_callout = False
    for line in lines:
        if re.match(r'^>\s*\[!insight\]', line):
            in_callout = True
            continue
        if in_callout:
            if line.startswith('>'):
                continue
            else:
                in_callout = False
        result.append(line)
    return '\n'.join(result)


def strip_jina_metadata(text):
    """Remove Jina metadata lines from the top of jina-raw.md."""
    lines = text.split('\n')
    body_start = 0
    for i, line in enumerate(lines):
        # Jina metadata lines are typically "Key: Value" at the top
        if re.match(r'^(Title|URL|Markdown Content|Published Time|Description):', line):
            body_start = i + 1
            continue
        if line.strip() == '' and body_start > 0:
            body_start = i + 1
            continue
        if body_start > 0:
            break
    return '\n'.join(lines[body_start:])


def parse_frontmatter(text):
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


# ─── Check functions ───
# Each returns (pass: bool, message: str)

def check_section_integrity(source_text, note_text):
    """Verify H2 headings match between source and note."""
    # Agent-generated sections to exclude from comparison
    agent_sections = {
        'key terms glossary', 'glossary', 'connections',
        'key concepts', '⚡ key concepts'
    }

    source_h2 = extract_headings(source_text, 2)
    note_h2 = [h for h in extract_headings(note_text, 2)
                if h.lower().strip() not in agent_sections]

    if len(source_h2) == 0:
        return True, "Source has no H2 headings (flat article), skipping heading check"

    if len(note_h2) != len(source_h2):
        return False, (
            f"Heading count mismatch: source has {len(source_h2)}, "
            f"note has {len(note_h2)}\n"
            f"  Source: {source_h2}\n"
            f"  Note:   {note_h2}"
        )

    # Check order
    for i, (src, note) in enumerate(zip(source_h2, note_h2)):
        if src.lower() != note.lower():
            return False, (
                f"Heading order mismatch at position {i+1}: "
                f"source='{src}', note='{note}'"
            )

    return True, f"All {len(source_h2)} headings match in order"


def check_word_count_per_section(source_text, note_text):
    """Verify each note section has ≥80% of source section word count."""
    agent_sections = {
        'key terms glossary', 'glossary', 'connections',
        'key concepts', '⚡ key concepts'
    }

    source_sections = split_sections(source_text, 2)
    note_sections = [(h, b) for h, b in split_sections(note_text, 2)
                      if h.lower().strip() not in agent_sections]

    if not source_sections:
        return True, "No sections to compare"

    failures = []
    for i, (src_h, src_body) in enumerate(source_sections):
        if i >= len(note_sections):
            failures.append(f"  Section '{src_h}' missing from note entirely")
            continue

        note_h, note_body = note_sections[i]
        # Strip callouts from note body before counting
        note_body_clean = strip_callouts(note_body)

        src_wc = word_count(src_body)
        note_wc = word_count(note_body_clean)
        threshold = int(src_wc * 0.8)

        if src_wc > 0 and note_wc < threshold:
            failures.append(
                f"  '{src_h}': {note_wc} words < {threshold} minimum "
                f"(source: {src_wc}, 80%={threshold})"
            )

    if failures:
        return False, "Word count below 80% threshold:\n" + "\n".join(failures)
    return True, "All sections meet 80% word count minimum"


def check_frontmatter(note_text):
    """Verify frontmatter has all required fields."""
    fm = parse_frontmatter(note_text)
    if fm is None:
        return False, "No valid YAML frontmatter found"

    required = ['title', 'source', 'site', 'date_extracted', 'tags']
    missing = [f for f in required if f not in fm or fm[f] is None]

    if missing:
        return False, f"Missing frontmatter fields: {missing}"

    # Validate date format
    date_val = str(fm.get('date_extracted', ''))
    if not re.match(r'^\d{4}/\d{2}/\d{2}$', date_val):
        return False, f"date_extracted format should be YYYY/MM/DD, got: '{date_val}'"

    # Validate tags is a list
    if not isinstance(fm.get('tags'), list) or len(fm['tags']) == 0:
        return False, "tags must be a non-empty list"

    return True, "Frontmatter complete and valid"


def check_required_sections(note_text):
    """Verify TL;DR, Key Concepts, Glossary, Connections exist."""
    checks = []

    # TL;DR
    if re.search(r'\*\*TL;DR\*\*', note_text):
        checks.append(("TL;DR", True, "present"))
    else:
        checks.append(("TL;DR", False, "missing"))

    # Key Concepts table (heading level and emoji prefix may vary).
    # Accept legacy Markdown tables and the full-width HTML table
    # format used by newer notes for better Obsidian alignment.
    kc_match = re.search(r'Key Concepts\s*\n\s*\n(\|[\s\S]*?)(?=\n\n---|\n\n##)', note_text)
    if kc_match:
        rows = [l for l in kc_match.group(1).split('\n')
                if l.strip().startswith('|') and '---' not in l and '概念' not in l]
        if 4 <= len(rows) <= 8:
            checks.append(("Key Concepts", True, f"{len(rows)} entries"))
        else:
            checks.append(("Key Concepts", False,
                          f"{len(rows)} entries (need 4-8)"))
    else:
        html_match = re.search(
            r'Key Concepts\s*\n\s*\n(<table\b[\s\S]*?</table>)',
            note_text,
            re.IGNORECASE,
        )
        if html_match:
            table_html = html_match.group(1)
            rows = re.findall(
                r'<tr\b[\s\S]*?</tr>',
                table_html,
                re.IGNORECASE,
            )
            body_rows = [
                row for row in rows
                if not re.search(r'<th\b', row, re.IGNORECASE)
            ]
            if 4 <= len(body_rows) <= 8:
                checks.append(("Key Concepts", True,
                              f"{len(body_rows)} entries"))
            else:
                checks.append(("Key Concepts", False,
                              f"{len(body_rows)} entries (need 4-8)"))
        else:
            checks.append(("Key Concepts", False, "table not found"))

    # Glossary
    if re.search(r'^##\s+.*(?:Glossary|glossary)', note_text, re.MULTILINE):
        checks.append(("Glossary", True, "present"))
    else:
        checks.append(("Glossary", False, "section missing"))

    # Connections
    if re.search(r'^##\s+Connections', note_text, re.MULTILINE):
        checks.append(("Connections", True, "present"))
    else:
        checks.append(("Connections", False, "section missing"))

    failures = [f"  {name}: {msg}" for name, ok, msg in checks if not ok]
    if failures:
        return False, "Missing required sections:\n" + "\n".join(failures)
    return True, "All required sections present"


def check_formulas(note_text):
    """Detect likely unconverted plain-text formulas."""
    # Patterns that look like formulas but aren't in $$...$$ blocks
    plain_formula_patterns = [
        r'(?<!\$)\b\w+\s*=\s*\w+\s*[\+\-\×÷/]\s*\w+(?!\$)',  # X = A + B
    ]
    # But exclude lines inside $$ blocks
    in_math = False
    suspicious = []
    for line in note_text.split('\n'):
        if line.strip().startswith('$$'):
            in_math = not in_math
            continue
        if in_math:
            continue
        # Skip lines in callouts, frontmatter, code blocks
        if line.startswith('>') or line.startswith('```') or line.startswith('---'):
            continue
        for pattern in plain_formula_patterns:
            matches = re.findall(pattern, line)
            for m in matches:
                # Filter out common false positives
                if any(fp in m.lower() for fp in ['http', 'url', 'path', 'file', 'alt']):
                    continue
                suspicious.append(f"  Line: {line.strip()[:80]}")

    if suspicious and len(suspicious) <= 10:
        return False, ("Possible unconverted formulas (should use $$...$$):\n"
                       + "\n".join(suspicious[:5]))
    return True, "No obvious unconverted formulas detected"


def check_cross_references(note_text):
    """Verify [[...]] links use UPPER-CASE-KEBAB format."""
    refs = re.findall(r'\[\[([^\]]+)\]\]', note_text)
    bad = [r for r in refs if r != r.upper() or ' ' in r]

    if bad:
        return False, (
            f"Cross-references not in UPPER-CASE-KEBAB format:\n"
            + "\n".join(f"  [[{r}]] → should be [[{r.upper().replace(' ', '-')}]]"
                        for r in bad[:5])
        )
    if refs:
        return True, f"{len(refs)} cross-references, all UPPER-CASE-KEBAB"
    return True, "No cross-references found (acceptable if no related notes)"


def check_images(note_text, manifest_path):
    """Verify image references match manifest decisions."""
    if not os.path.exists(manifest_path):
        return True, "No image manifest found (no images in source)"

    with open(manifest_path) as f:
        manifest = json.load(f)

    failures = []

    for img in manifest.get('images', []):
        decision = img.get('agent_decision')
        filename = img.get('filename')
        alt = img.get('alt', '')
        src = img.get('src', '')

        if decision == 'keep' and img['status'] == 'ok' and filename:
            # Should be referenced in note
            if filename not in note_text:
                failures.append(
                    f"  KEEP image '{filename}' not referenced in note")

        elif decision == 'drop' and filename:
            # Should NOT be referenced in note
            if filename in note_text:
                failures.append(
                    f"  DROPPED image '{filename}' still referenced in note")

        elif decision is None and img['status'] in ('ok', 'failed'):
            failures.append(
                f"  Image '{alt or src}' has no agent_decision — "
                f"agent skipped Phase 2 filtering")

    if failures:
        return False, "Image check failures:\n" + "\n".join(failures)
    return True, "Image references consistent with manifest"


def check_commentary_quality(note_text):
    """Check commentary blocks for common quality issues."""
    # Extract all insight callout blocks
    blocks = re.findall(
        r'>\s*\[!insight\].*?\n((?:>.*\n)*)',
        note_text, re.MULTILINE
    )

    if not blocks:
        return True, "No commentary blocks found (acceptable for some articles)"

    failures = []

    # Banned filler phrases
    filler_patterns = [
        r'(?:this|the) (?:section|concept|topic) is (?:very )?important',
        r'worth (?:reviewing|studying|reading) (?:carefully|again)',
        r'this is (?:a )?(key|critical|essential|fundamental) (?:concept|idea|point)',
        r'值得.*(?:反复|认真|仔细).*(?:学习|阅读|复习|理解)',
        r'这(?:一)?(?:节|部分|概念)(?:非常|很|十分)?(?:重要|关键)',
        r'建议.*(?:反复|多次).*(?:阅读|学习|复习)',
    ]

    for i, block in enumerate(blocks, 1):
        block_text = re.sub(r'^>\s*', '', block, flags=re.MULTILINE)

        # Check for filler
        for pattern in filler_patterns:
            if re.search(pattern, block_text, re.IGNORECASE):
                failures.append(
                    f"  Block {i}: contains filler phrase matching '{pattern}'")
                break

        # Check for concreteness: must have at least one of:
        # - a number/percentage
        # - a [[cross-reference]]
        # - a company/index name (crude check via capitalized words after common patterns)
        has_number = bool(re.search(r'\d+\.?\d*\s*[%％]|\$[\d,]+|\d+\.\d+|\d{2,}', block_text))
        has_ref = bool(re.search(r'\[\[', block_text))
        has_formula = bool(re.search(r'\$\$', block_text))
        # Check for specific entity names and financial terms
        has_entity = bool(re.search(
            r'\b(?:S&P|NYSE|NASDAQ|MSCI|Bloomberg|Moody|Fitch|'
            r'Apple|Microsoft|Amazon|Google|Tesla|Berkshire|'
            r'Warren Buffett|Damodaran|Graham|Enron|'
            r'Fed(?:eral Reserve)?|SEC|GAAP|IFRS|'
            r'P/E|P/B|EV/EBITDA|ROE|ROA|WACC|DCF|EPS|'
            r'OCF|CapEx|FCFF|FCFE|D&A|EBITDA|'
            r'Cash Flow Statement|Income Statement|Balance Sheet|'
            r'MD&A|10-K|10-Q|IPO|M&A|LBO)\b',
            block_text, re.IGNORECASE
        ))

        if not (has_number or has_ref or has_formula or has_entity):
            # Extract first 60 chars for context
            preview = block_text.strip()[:60].replace('\n', ' ')
            failures.append(
                f"  Block {i}: no concrete element found "
                f"(number/reference/formula/entity). Preview: '{preview}...'"
            )

    if failures:
        return False, "Commentary quality issues:\n" + "\n".join(failures)
    return True, f"All {len(blocks)} commentary blocks pass quality checks"


def check_info_points(note_text, ip_path):
    """Verify information points from inventory appear in the note."""
    if not os.path.exists(ip_path):
        return False, (
            "info-points.json not found — agent must save the IP inventory "
            "from Step 2 to assets/info-points.json"
        )

    with open(ip_path) as f:
        ip_data = json.load(f)

    total_ips = 0
    missing_ips = []

    for section in ip_data.get('sections', []):
        section_name = section.get('heading', 'unknown')
        for ip in section.get('info_points', []):
            total_ips += 1
            # Check if key terms from the IP appear in the note
            keywords = ip.get('keywords', [])
            ip_text = ip.get('text', '')

            if not keywords:
                continue

            # At least half of keywords should appear in the note
            found = sum(1 for kw in keywords
                       if kw.lower() in note_text.lower())
            if found < len(keywords) * 0.5:
                missing_ips.append(
                    f"  [{section_name}] IP: '{ip_text[:60]}...' "
                    f"— only {found}/{len(keywords)} keywords found"
                )

    if missing_ips:
        return False, (
            f"Possibly missing information points ({len(missing_ips)}/{total_ips}):\n"
            + "\n".join(missing_ips[:10])
            + ("\n  ... and more" if len(missing_ips) > 10 else "")
        )
    return True, f"All {total_ips} information points have keyword coverage"


def check_file_organization(topic_folder):
    """Verify only one .md in root, everything else in assets/."""
    root_files = [f for f in os.listdir(topic_folder)
                  if os.path.isfile(os.path.join(topic_folder, f))]
    root_md = [f for f in root_files if f.endswith('.md')]
    root_other = [f for f in root_files if not f.endswith('.md')]

    failures = []
    if len(root_md) != 1:
        failures.append(
            f"  Expected exactly 1 .md file in root, found {len(root_md)}: {root_md}")
    if root_other:
        failures.append(
            f"  Non-.md files in root (should be in assets/): {root_other}")

    assets_dir = os.path.join(topic_folder, 'assets')
    if not os.path.isdir(assets_dir):
        failures.append("  assets/ directory missing")

    if failures:
        return False, "File organization issues:\n" + "\n".join(failures)
    return True, "File organization correct"


def check_chinese_content(note_text):
    """Verify the note body is primarily in Chinese."""
    # Extract body sections only (skip frontmatter, headings, code blocks,
    # tables, image refs, callout markers)
    body_lines = []
    in_frontmatter = False
    in_code = False
    in_html_table = False
    for line in note_text.split('\n'):
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.search(r'<table\b', line, re.IGNORECASE):
            in_html_table = True
            continue
        if in_html_table:
            if re.search(r'</table>', line, re.IGNORECASE):
                in_html_table = False
            continue
        if re.search(r'<img\b', line, re.IGNORECASE):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        # Skip headings, table rows, image refs, callout markers, links
        if (line.startswith('#') or line.startswith('|') or
            line.startswith('![') or line.startswith('> 📷') or
            line.startswith('> [!') or line.startswith('*Source:') or
            line.startswith('$$')):
            continue
        # Skip callout content lines (start with >)
        if line.startswith('>'):
            continue
        body_lines.append(line)

    body_text = '\n'.join(body_lines)
    if not body_text.strip():
        return True, "No body text to check"

    # Count CJK characters vs Latin characters
    cjk_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', body_text))
    latin_chars = len(re.findall(r'[a-zA-Z]', body_text))
    total = cjk_chars + latin_chars

    if total == 0:
        return True, "No text content to evaluate"

    cjk_ratio = cjk_chars / total

    # Body should be primarily Chinese. Ratio won't be very high
    # because financial terms stay in English, but below 30% means
    # the text is mostly English — likely untranslated.
    if cjk_ratio < 0.3:
        return False, (
            f"Body text appears to not be in Chinese. "
            f"CJK ratio: {cjk_ratio:.1%} ({cjk_chars} CJK / {latin_chars} Latin). "
            f"Expected ≥30%. Did the agent forget to translate?"
        )

    return True, f"Chinese content ratio: {cjk_ratio:.1%} ({cjk_chars} CJK / {latin_chars} Latin)"


# ─── Main ───

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate-note.py <TOPIC_FOLDER>")
        sys.exit(1)

    topic_folder = sys.argv[1]
    if not os.path.isdir(topic_folder):
        print(f"ERROR: {topic_folder} is not a directory")
        sys.exit(1)

    # Find the final note
    root_mds = [f for f in os.listdir(topic_folder)
                if f.endswith('.md') and os.path.isfile(os.path.join(topic_folder, f))]
    if len(root_mds) != 1:
        print(f"ERROR: Expected 1 .md file in {topic_folder}, found {len(root_mds)}: {root_mds}")
        sys.exit(1)

    note_path = os.path.join(topic_folder, root_mds[0])
    note_text = Path(note_path).read_text(encoding='utf-8', errors='replace')

    # Find source markdown
    assets_dir = os.path.join(topic_folder, 'assets')
    source_path = os.path.join(assets_dir, 'jina-raw.md')
    if not os.path.exists(source_path):
        source_path = os.path.join(assets_dir, 'manual-input.md')
    if os.path.exists(source_path):
        source_text = strip_jina_metadata(
            Path(source_path).read_text(encoding='utf-8', errors='replace'))
    else:
        source_text = ""

    manifest_path = os.path.join(assets_dir, 'image-manifest.json')
    ip_path = os.path.join(assets_dir, 'info-points.json')

    # ─── Run all checks ───
    checks = [
        ("Section Integrity",
         lambda: check_section_integrity(source_text, note_text)
         if source_text else (True, "No source to compare (manual input)")),

        ("Word Count ≥80%",
         lambda: check_word_count_per_section(source_text, note_text)
         if source_text else (True, "No source to compare")),

        ("Frontmatter",
         lambda: check_frontmatter(note_text)),

        ("Required Sections",
         lambda: check_required_sections(note_text)),

        ("Formula Conversion",
         lambda: check_formulas(note_text)),

        ("Cross-Reference Format",
         lambda: check_cross_references(note_text)),

        ("Image Consistency",
         lambda: check_images(note_text, manifest_path)),

        ("Commentary Quality",
         lambda: check_commentary_quality(note_text)),

        ("Information Points",
         lambda: check_info_points(note_text, ip_path)),

        ("File Organization",
         lambda: check_file_organization(topic_folder)),

        ("Chinese Content",
         lambda: check_chinese_content(note_text)),
    ]

    print("=" * 60)
    print(f"  VALIDATION: {root_mds[0]}")
    print("=" * 60)
    print()

    passed = 0
    failed = 0
    warnings = 0

    for name, check_fn in checks:
        try:
            ok, msg = check_fn()
        except Exception as e:
            ok, msg = False, f"Check crashed: {e}"

        if ok:
            passed += 1
            print(f"  ✅ PASS  {name}")
            print(f"          {msg}")
        else:
            failed += 1
            print(f"  ❌ FAIL  {name}")
            for line in msg.split('\n'):
                print(f"          {line}")
        print()

    print("=" * 60)
    print(f"  RESULT: {passed} passed, {failed} failed")
    if failed > 0:
        print(f"  ⛔ NOTE DOES NOT MEET REQUIREMENTS — FIX BEFORE DELIVERY")
    else:
        print(f"  ✅ ALL CHECKS PASSED")
    print("=" * 60)

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
