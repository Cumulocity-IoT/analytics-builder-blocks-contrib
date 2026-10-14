#!/usr/bin/env bash
#
# Builds one extension zip per block.
#
# A block's zip contains the block's .mon file plus the dependency files listed
# for it in the dependencies file (format: "<block file>: <dep file>...").
# Helper files that do not define a block (no $blockCategory annotation) are only
# shipped as dependencies, never as standalone zips.
#
# Usage: build-individual-blocks.sh <analytics_builder> <output-dir> <version> <dependencies-file> <block-dir>...

set -euo pipefail

BUILDER="$1"
OUTPUT_DIR="$2"
VERSION="$3"
DEPS_FILE="$4"
shift 4

declare -A deps=()
while IFS= read -r line; do
  line="${line%%#*}"
  [[ "$line" == *:* ]] || continue
  block="${line%%:*}"
  block="$(echo $block)"
  deps["$block"]="${line#*:}"
  for dep in ${deps[$block]}; do
    if [ ! -f "$dep" ]; then
      echo "Error: dependency '$dep' of '$block' not found" >&2
      exit 1
    fi
  done
done < "$DEPS_FILE"

BLOCK_COUNT=0
for dir in "$@"; do
  [ -d "$dir" ] || continue
  for block_file in "$dir"/*.mon; do
    [ -f "$block_file" ] || continue
    if ! grep -q '\$blockCategory' "$block_file"; then
      echo "  Skipped (not a block): $block_file"
      continue
    fi
    block_name=$(basename "$block_file" .mon)
    files=("$block_file" ${deps[$block_file]:-})

    temp_dir=$(mktemp -d)
    cp "${files[@]}" "$temp_dir/"

    "$BUILDER" build extension \
      --input "$temp_dir/" \
      --output "$OUTPUT_DIR/${block_name}-${VERSION}.zip"

    rm -rf "$temp_dir"

    BLOCK_COUNT=$((BLOCK_COUNT + 1))
    echo "  Built: ${block_name} (${files[*]})"
  done
done

echo ""
echo "Built $BLOCK_COUNT individual blocks"
