#!/usr/bin/env bash
# Run the supported Node/npm service lifecycle with the installed Node toolchain.
set -euo pipefail
tracker_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$tracker_root"
if [[ -x /opt/homebrew/opt/node@22/bin/node ]]; then
  export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
fi
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) throw Error("Node 22+ is required")'
if [[ $# -eq 0 ]]; then
  set -- rebuild components/tracker --allow-host-execution --keep-runtime
fi
exec litai "$@"
