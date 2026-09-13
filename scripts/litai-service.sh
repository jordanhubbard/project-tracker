#!/usr/bin/env bash
# Run LitAI with the application's isolated, pinned service interpreter.
set -euo pipefail
tracker_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tracker_runtime="$tracker_root/_build/service-runtime"
cd "$tracker_root"
if [[ ! -x "$tracker_runtime/bin/python" ]]; then
  uv venv "$tracker_runtime" --python '>=3.11'
fi
uv pip sync --python "$tracker_runtime/bin/python" flavors/python-service/requirements.txt
export PATH="$tracker_runtime/bin:$PATH"
if [[ $# -eq 0 ]]; then
  set -- rebuild components/tracker --allow-host-execution --keep-runtime
fi
exec litai "$@"
