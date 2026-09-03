#!/bin/bash
# Sequential income then deaths for one UF so hover joins do not race.
set -euo pipefail
UF="${1:?UF required}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
./scripts/build_theme_uf.sh "$UF" income
./scripts/build_theme_uf.sh "$UF" deaths
