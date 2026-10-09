#!/bin/sh
# Install the IP-rails pre-commit and corpus-free pushed-ref backstop.
set -eu
cd "$(dirname "$0")/.."
current=$(git config --local --get core.hooksPath || true)
if [ -n "$current" ] && [ "$current" != "tools/hooks" ]; then
  echo "Existing core.hooksPath differs; refusing to replace it: $current" >&2
  exit 1
fi
chmod +x tools/hooks/pre-commit tools/hooks/pre-push
git config --local core.hooksPath tools/hooks
echo "Installed tools/hooks: staged IP check and corpus-free pushed-ref validation"
