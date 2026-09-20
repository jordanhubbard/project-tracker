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
node -e 'if (process.versions.node !== "22.23.2") throw Error("Node differs from observed 22.23.2 build authority; refresh runtime.md before rebuilding")'
"$tracker_root/scripts/check-git-version.sh" "$(git --version)"
if [[ $# -eq 0 ]]; then
  set -- rebuild components/tracker --allow-host-execution --keep-runtime
  if [[ "$CODING_CLI" == claude ]]; then
    set -- "$@" --model claude-fable-5-1
  fi
fi
exec litai "$@"
