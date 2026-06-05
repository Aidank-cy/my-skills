#!/usr/bin/env bash
#
# download-images.sh — Extract image URLs from Jina Markdown output,
# filter junk, download with per-image timeout.
#
# Usage: bash download-images.sh <JINA_MD_FILE> <OUTPUT_DIR>
#
# Outputs:
#   - Downloaded images in OUTPUT_DIR
#   - image-manifest.json listing all images and their download status
#   (Agent performs a second content-relevance filter after this script)

set -euo pipefail

JINA_MD="${1:?Usage: download-images.sh <JINA_MD_FILE> <OUTPUT_DIR>}"
OUTPUT_DIR="${2:?Usage: download-images.sh <JINA_MD_FILE> <OUTPUT_DIR>}"
TIMEOUT=20
MAX_PARALLEL=5
TAB="$(printf '\t')"

mkdir -p "$OUTPUT_DIR"

# ── Extract and filter in one pass using Python for reliability ──
# Handles: URL extraction, junk filtering, safe TSV output

python3 - "$JINA_MD" "$OUTPUT_DIR" << 'PYEOF'
import re, sys, os

jina_md = sys.argv[1]
output_dir = sys.argv[2]

with open(jina_md, encoding="utf-8", errors="replace") as f:
    content = f.read()

# Extract all ![alt](url) patterns
images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
print(f"Found {len(images)} image references")

# URL-pattern filters
AD_TRACKING = re.compile(
    r'(doubleclick\.|googlesyndication\.|amazon-adsystem\.|adnxs\.|'
    r'adsrvr\.|moatads\.|chartbeat\.|quantserve\.|scorecardresearch\.|'
    r'outbrain\.|taboola\.|tracking|pixel|beacon)',
    re.IGNORECASE
)
DECORATIVE = re.compile(
    r'(favicon|logo\.|icon\.|avatar|gravatar|share[-_]?button|'
    r'social[-_]?icon|badge\.|button\.|arrow\.|spacer\.)',
    re.IGNORECASE
)
PROMO = re.compile(
    r'(newsletter|signup|subscribe|promo[-_]?banner|cta[-_]?banner|'
    r'related[-_]?article|thumbnail)',
    re.IGNORECASE
)
INFO_SVG = re.compile(
    r'(chart|diagram|flow|graph|figure|table|process|structure|'
    r'formula|equation)',
    re.IGNORECASE
)

queue = []
filtered = []

for alt, url in images:
    reason = None

    # Data URIs
    if url.startswith('data:'):
        reason = "data URI"
    # Ad networks / tracking
    elif AD_TRACKING.search(url):
        reason = "ad network or tracking"
    # Decorative UI elements (check both URL and alt)
    elif DECORATIVE.search(url) or DECORATIVE.search(alt):
        reason = "decorative UI element"
    # Promo / navigation (check both URL and alt)
    elif PROMO.search(url) or PROMO.search(alt):
        reason = "promotional or navigation"
    # SVG: only keep if alt suggests informational content
    elif url.lower().endswith('.svg') or '.svg?' in url.lower():
        if not INFO_SVG.search(alt):
            reason = "non-informational SVG"

    if reason:
        filtered.append((alt, url, reason))
    else:
        queue.append((alt, url))

# Write download queue
with open(os.path.join(output_dir, "_download_queue.tsv"), "w") as f:
    for alt, url in queue:
        f.write(f"{alt}\t{url}\n")

# Write filtered log
with open(os.path.join(output_dir, "_filtered_log.tsv"), "w") as f:
    for alt, url, reason in filtered:
        f.write(f"{alt}\t{url}\t{reason}\n")

print(f"After URL filter: {len(queue)} to download ({len(filtered)} filtered out)")

# Write counts for the shell script
with open(os.path.join(output_dir, "_counts.txt"), "w") as f:
    f.write(f"{len(images)}\n{len(queue)}\n{len(filtered)}\n")
PYEOF

# Read counts
TOTAL=$(sed -n '1p' "$OUTPUT_DIR/_counts.txt")
QUEUE_SIZE=$(sed -n '2p' "$OUTPUT_DIR/_counts.txt")
FILTERED=$(sed -n '3p' "$OUTPUT_DIR/_counts.txt")

if [ "$QUEUE_SIZE" -eq 0 ]; then
  python3 -c "
import json, sys, os
filtered = []
fpath = os.path.join('$OUTPUT_DIR', '_filtered_log.tsv')
if os.path.exists(fpath):
    with open(fpath) as f:
        for line in f:
            parts = line.strip().split('\t', 2)
            if len(parts) == 3:
                filtered.append({'status':'filtered','filename':None,'alt':parts[0],'src':parts[1],'agent_decision':'drop','reason':parts[2]})
json.dump({'total':$TOTAL,'downloaded':0,'failed':0,'filtered':$FILTERED,'images':filtered},
          open(os.path.join('$OUTPUT_DIR','image-manifest.json'),'w'), indent=2, ensure_ascii=False)
"
  rm -f "$OUTPUT_DIR/_download_queue.tsv" "$OUTPUT_DIR/_filtered_log.tsv" "$OUTPUT_DIR/_counts.txt"
  echo "No images to download after filtering."
  exit 0
fi

# ── Download with timeout ──

download_one() {
  local alt="$1"
  local url="$2"
  local output_dir="$3"
  local timeout="$4"

  # Safe filename from alt text or URL
  local safename
  if [ -n "$alt" ]; then
    safename=$(echo "$alt" | tr '[:upper:]' '[:lower:]' \
      | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g' | head -c 50)
  fi
  if [ -z "${safename:-}" ]; then
    safename=$(echo "$url" | sed -E 's|.*/||; s|\?.*||; s|[^a-zA-Z0-9.-]|-|g' | head -c 50)
  fi
  [ -z "$safename" ] && safename="image"

  # Extension from URL
  local ext
  ext=$(echo "$url" | sed -E 's|\?.*||' | grep -oiE '\.(png|jpg|jpeg|gif|webp)$' | head -1 | tr '[:upper:]' '[:lower:]')
  [ -z "$ext" ] && ext=".png"

  local filename="${safename}${ext}"

  # Collision avoidance
  local counter=2
  while [ -f "$output_dir/$filename" ]; do
    filename="${safename}-${counter}${ext}"
    counter=$((counter + 1))
  done

  # Download
  local http_code
  http_code=$(curl -sL -o "$output_dir/$filename" -w "%{http_code}" \
    --max-time "$timeout" --connect-timeout 10 \
    -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    -H "Referer: ${url%/*}/" \
    "$url" 2>/dev/null) || http_code="000"

  # Validate: HTTP 2xx/3xx AND > 1KB
  local filesize=0
  if [ -f "$output_dir/$filename" ]; then
    filesize=$(wc -c < "$output_dir/$filename" | tr -d ' ')
  fi

  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 400 ] && [ "$filesize" -gt 1024 ]; then
    echo "OK${TAB}${filename}${TAB}${filesize}"
  else
    rm -f "$output_dir/$filename"
    echo "FAIL${TAB}${TAB}${http_code}"
  fi
}

export -f download_one
export TAB

# ── Parallel download using background jobs ──
RESULTS_FILE="$OUTPUT_DIR/_results.tsv"
> "$RESULTS_FILE"

declare -a ALTS=()
declare -a URLS=()
while IFS="${TAB}" read -r alt url; do
  ALTS+=("$alt")
  URLS+=("$url")
done < "$OUTPUT_DIR/_download_queue.tsv"

TOTAL_QUEUE=${#ALTS[@]}
IDX=0
DOWNLOADED=0
FAILED=0

while [ "$IDX" -lt "$TOTAL_QUEUE" ]; do
  PIDS=()
  BATCH_END=$((IDX + MAX_PARALLEL))
  [ "$BATCH_END" -gt "$TOTAL_QUEUE" ] && BATCH_END=$TOTAL_QUEUE

  for (( i=IDX; i<BATCH_END; i++ )); do
    tmpfile="$OUTPUT_DIR/_dl_${i}.tmp"
    ( download_one "${ALTS[$i]}" "${URLS[$i]}" "$OUTPUT_DIR" "$TIMEOUT" > "$tmpfile" ) &
    PIDS+=($!)
  done

  for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
  done

  for (( i=IDX; i<BATCH_END; i++ )); do
    tmpfile="$OUTPUT_DIR/_dl_${i}.tmp"
    result=""
    [ -f "$tmpfile" ] && result=$(cat "$tmpfile") && rm -f "$tmpfile"
    [ -z "$result" ] && result="FAIL${TAB}${TAB}000"

    status="${result%%${TAB}*}"
    rest="${result#*${TAB}}"
    filename="${rest%%${TAB}*}"

    printf "%s\t%s\t%s\t%s\n" "$status" "$filename" "${ALTS[$i]}" "${URLS[$i]}" >> "$RESULTS_FILE"

    if [ "$status" = "OK" ]; then
      DOWNLOADED=$((DOWNLOADED + 1))
      echo "  ✅ ${filename}"
    else
      FAILED=$((FAILED + 1))
      echo "  ❌ Failed: ${ALTS[$i]} (${URLS[$i]})"
    fi
  done

  IDX=$BATCH_END
done

# ── Write manifest using Python for safe JSON encoding ──
python3 - "$OUTPUT_DIR" "$RESULTS_FILE" "$OUTPUT_DIR/_filtered_log.tsv" \
  "$TOTAL" "$DOWNLOADED" "$FAILED" "$FILTERED" << 'PYEOF'
import json, sys, os

output_dir, results_file, filtered_file = sys.argv[1], sys.argv[2], sys.argv[3]
total, downloaded, failed, filtered_count = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])

images = []

if os.path.exists(results_file):
    with open(results_file) as f:
        for line in f:
            parts = line.strip().split('\t', 3)
            if len(parts) >= 4:
                status, filename, alt, src = parts[0], parts[1], parts[2], parts[3]
                images.append({
                    "status": "ok" if status == "OK" else "failed",
                    "filename": filename if status == "OK" else None,
                    "alt": alt,
                    "src": src,
                    "agent_decision": None,
                    "reason": None
                })

if os.path.exists(filtered_file):
    with open(filtered_file) as f:
        for line in f:
            parts = line.strip().split('\t', 2)
            if len(parts) == 3:
                images.append({
                    "status": "filtered",
                    "filename": None,
                    "alt": parts[0],
                    "src": parts[1],
                    "agent_decision": "drop",
                    "reason": parts[2]
                })

manifest = {
    "total": total,
    "downloaded": downloaded,
    "failed": failed,
    "filtered": filtered_count,
    "images": images
}

with open(os.path.join(output_dir, "image-manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
PYEOF

# Cleanup
rm -f "$OUTPUT_DIR/_download_queue.tsv" "$OUTPUT_DIR/_filtered_log.tsv" \
      "$OUTPUT_DIR/_counts.txt" "$RESULTS_FILE"

echo ""
echo "Done: $DOWNLOADED downloaded, $FAILED failed, $FILTERED filtered"
echo "Manifest: $OUTPUT_DIR/image-manifest.json"
echo "→ Agent: review manifest and apply content-relevance filter (Step 3 Phase 2)"