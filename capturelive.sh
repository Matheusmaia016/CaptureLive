#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -x "$DIR/release/capturelive.exe" ]]; then
  "$DIR/release/capturelive.exe" "$@"
elif [[ -x "$DIR/dist/capturelive.exe" ]]; then
  "$DIR/dist/capturelive.exe" "$@"
else
  python -m capturelive "$@"
fi
