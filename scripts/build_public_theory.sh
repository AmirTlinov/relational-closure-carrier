#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ATLAS="$ROOT/theory"
PDF="$ROOT/THEORY.pdf"
PAGES="$ATLAS/pages"
DPI="${DPI:-180}"

for command in node pdfinfo pdffonts pdftoppm pdftotext gs magick; do
  command -v "$command" >/dev/null || {
    printf 'Required command not found: %s\n' "$command" >&2
    exit 1
  }
done

(cd "$ATLAS" && node print-atlas.mjs . "$PDF")

info="$(mktemp)"
fonts="$(mktemp)"
text="$(mktemp)"
sheet_dir="$(mktemp -d)"
trap 'rm -f "$info" "$fonts" "$text"; rm -rf "$sheet_dir"' EXIT

pdfinfo -f 1 -l 9 "$PDF" >"$info"
pages="$(awk '/^Pages:/ { print $2; exit }' "$info")"
[[ "$pages" == "9" ]] || {
  printf 'THEORY.pdf produced %s pages, expected 9\n' "$pages" >&2
  exit 1
}

awk '
  /^Page[[:space:]]+[0-9]+[[:space:]]+size:/ {
    if ($4 < 593.9 || $4 > 596.1 || $6 < 840.9 || $6 > 843.1) exit 1
    found++
  }
  /^Page[[:space:]]+[0-9]+[[:space:]]+rot:/ { if ($4 != 0) exit 1 }
  END { if (found != 9) exit 1 }
' "$info" || {
  printf 'THEORY.pdf is not nine A4 portrait sheets\n' >&2
  exit 1
}

grep -Eq '^Tagged:[[:space:]]+yes$' "$info" || {
  printf 'THEORY.pdf is not tagged\n' >&2
  exit 1
}

gs -q -dNOPAUSE -dBATCH -sDEVICE=nullpage "$PDF"
pdffonts "$PDF" >"$fonts"
awk '
  NR <= 2 { next }
  NF { count++; if ($(NF-4) != "yes" || $(NF-2) != "yes") bad++ }
  END { exit !(count > 0 && bad == 0) }
' "$fonts" || {
  printf 'THEORY.pdf has fonts without embedding or Unicode maps\n' >&2
  exit 1
}

pdftotext -layout "$PDF" "$text"
grep -Fq '∂C = 0' "$text" || {
  printf 'THEORY.pdf lost the boundary operator during printing\n' >&2
  exit 1
}

mkdir -p "$PAGES"
find "$PAGES" -type f -name 'page-*.png' -delete
for page in $(seq 1 "$pages"); do
  printf -v padded '%02d' "$page"
  pdftoppm -png -singlefile -r "$DPI" -f "$page" -l "$page" \
    "$PDF" "$PAGES/page-$padded" >/dev/null 2>&1
done

make_row() {
  local output="$1"
  shift
  local args=()
  local image
  for image in "$@"; do
    args+=( '(' "$image" -resize '400x' -bordercolor '#e8e2d8' -border 8 ')' )
  done
  magick "${args[@]}" +append "$output"
}

make_row "$sheet_dir/row-1.png" "$PAGES"/page-{01..03}.png
make_row "$sheet_dir/row-2.png" "$PAGES"/page-{04..06}.png
make_row "$sheet_dir/row-3.png" "$PAGES"/page-{07..09}.png
magick "$sheet_dir/row-1.png" "$sheet_dir/row-2.png" "$sheet_dir/row-3.png" -append -quality 88 \
  "$PAGES/contact-sheet.jpg"

printf 'PASS public theory: 9 pages A4, tagged, embedded Unicode fonts, %s dpi previews\n' "$DPI"
