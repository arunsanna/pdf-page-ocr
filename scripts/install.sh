#!/usr/bin/env bash
# Install only the locked, CPU-safe Python project environment.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [--install-uv]

Synchronizes the locked project environment. This script does not download OCR
model weights, install GPU runtimes, start a service, or send document data.

Options:
  --install-uv  Install uv with the active Python interpreter if it is missing.
  -h, --help    Show this help text.
EOF
}

install_uv=false
while (($#)); do
  case "$1" in
    --install-uv) install_uv=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v uv >/dev/null 2>&1; then
  if [[ "$install_uv" != true ]]; then
    cat >&2 <<'EOF'
uv is required but was not found.

Install it using your preferred trusted method, then rerun this script. To let
this script install uv with the active Python interpreter, rerun:
  ./scripts/install.sh --install-uv
EOF
    exit 1
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to install uv." >&2
    exit 1
  fi

  echo "Installing uv with python3 because --install-uv was explicitly requested..."
  python3 -m pip install --user uv
  export PATH="$HOME/.local/bin:$PATH"
fi

if [[ ! -f uv.lock ]]; then
  echo "uv.lock is missing; refusing an unlocked install." >&2
  exit 1
fi

echo "Synchronizing the locked CPU-safe project environment..."
uv sync --locked --all-groups
echo "Installed. No model weights or GPU services were installed."
