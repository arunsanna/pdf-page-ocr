#!/usr/bin/env bash
# Check prerequisites for a future, user-operated Linux/NVIDIA model runner.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/install-gpu-runner.sh --check

This helper does not install packages, download model weights, configure a
model server, or start a service. It only verifies whether the current host is
a plausible Linux/NVIDIA environment for a separately managed GPU OCR runner.
EOF
}

if [[ $# -ne 1 || "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  [[ $# -eq 1 ]] && exit 0
  exit 2
fi

if [[ "$1" != "--check" ]]; then
  echo "Expected --check." >&2
  usage >&2
  exit 2
fi

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "GPU runner checks require Linux. No installation was performed." >&2
  exit 1
fi

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi was not found. Install and validate an NVIDIA driver first." >&2
  exit 1
fi

echo "Linux host: PASS"
echo "NVIDIA driver and GPU visibility: PASS"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
printf '\nNo packages, model weights, or services were installed or started.\n'
echo "Use a separately reviewed, pinned serving profile to operate a GPU endpoint."
