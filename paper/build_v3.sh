#!/bin/zsh
# Version 3 (ACL draft): regenerate every number, table and figure, then compile main_v3.pdf.
set -e
cd "$(dirname "$0")/.."
zsh paper/build_v2.sh > /dev/null
.venv/bin/python -m analysis.targets | tail -1
.venv/bin/python -m analysis.v3
cd paper
if ! tectonic --keep-intermediates main_v3.tex > main_v3.build.log 2>&1; then
  grep -E -i "error|undefined" main_v3.build.log | head -8
  echo "LATEX FAILED: main_v3.pdf was not rebuilt" >&2
  exit 1
fi
grep -E -i "warning: (reference|citation)|undefined" main_v3.build.log | sort -u | head || true
echo "main_v3: $(pdfinfo main_v3.pdf | awk '/Pages/ {print $2}') pages; PENDING markers: $(grep -c 'PENDING{' main_v3.tex)"
