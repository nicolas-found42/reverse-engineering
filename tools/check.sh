#!/bin/sh
# Run the tool tests: tools/check.sh [test_module ...]. Needs Python >= 3.10 (the tools use 3.10+ syntax).
cd "$(dirname "$0")/.." || exit 1
for candidate in "${PYTHON:-}" python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
  [ -n "$candidate" ] && command -v "$candidate" >/dev/null 2>&1 || continue
  if "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
    exec "$candidate" tools/run_tests.py "$@"
  fi
done
echo "check.sh: no Python >= 3.10 found (set PYTHON=...)" >&2
exit 2
