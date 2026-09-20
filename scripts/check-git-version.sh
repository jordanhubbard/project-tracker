#!/usr/bin/env bash
# Validate the Project Tracker minimum Git version without rejecting newer releases.
set -euo pipefail

git_version="${1:-}"
if [[ ! "$git_version" =~ ^git[[:space:]]version[[:space:]]([0-9]+)\.([0-9]+)\.([0-9]+)([[:space:]].*)?$ ]]; then
  echo "Unable to parse Git version: ${git_version:-<empty>}. Project Tracker requires Git 2.30.0 or newer." >&2
  exit 1
fi

git_major="${BASH_REMATCH[1]}"
git_minor="${BASH_REMATCH[2]}"
git_patch="${BASH_REMATCH[3]}"

if (( git_major < 2 || (git_major == 2 && git_minor < 30) )); then
  echo "Unsupported Git version ${git_major}.${git_minor}.${git_patch}. Project Tracker requires Git 2.30.0 or newer." >&2
  exit 1
fi
