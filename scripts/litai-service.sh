#!/usr/bin/env bash
# Run the supported Node/npm service lifecycle with the installed Node toolchain.
set -euo pipefail
tracker_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$tracker_root"
# Full-stack generation needs more than the CLI's 15-minute default.
export LITERATE_AI_CODING_CLI_TIMEOUT_SECONDS="${LITERATE_AI_CODING_CLI_TIMEOUT_SECONDS:-3600}"
# This adapter provides direct Read/Write/Edit tools under LitAI's no-shell generation policy.
export CODING_CLI="${CODING_CLI:-claude}"
if [[ -x /opt/homebrew/opt/node@22/bin/node ]]; then
  export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
fi
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) throw Error("Node 22+ is required")'
tracker_git_version="$(git --version)"
case "$tracker_git_version" in
  'git version 2.50.1'|'git version 2.50.1 '*) ;;
  *) echo 'Git version differs from the observed 2.50.1 build authority; refresh runtime.md before rebuilding.' >&2; exit 1 ;;
esac
if [[ $# -eq 0 ]]; then
  set -- rebuild components/tracker --allow-host-execution --keep-runtime
fi
exec litai "$@"
