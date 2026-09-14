# Development and contribution

[Documentation](../README.md)

Read root `AGENTS.md` and `SKILL.md` before changing this specification-led project.
`PROJECT.md` records the product objective. Record substantive work in
`docs/roadmap/active-work.md` before editing its implementation authority.

## Change the owning specification

| Change | Authority |
| --- | --- |
| Product, REST, MCP, A2A, tasks or persistence | `components/tracker/component.md` |
| MAC matching, state, dependencies, synchronization or failure semantics | `components/tracker/mac-integration.md` |
| Required regression behavior and acceptance | `components/tracker/quality.md` |
| Visual layout and interactions | `components/tracker/visual.md` |
| Exact runtime and npm dependency closure | `components/tracker/runtime.md` |
| Target/toolchain policy | Selected files under `flavors/` |
| Explanations and operator workflows | `docs/` and root README |

Generated source is disposable. Fix intent in its owning authority and regenerate; do not
hand-edit the application export, source-cache entries or `verification/current.json`.
The framework owns lock resolution, candidate admission and receipts.

## Local lifecycle

```sh
./scripts/litai-service.sh project validate
./scripts/litai-service.sh lock components/tracker
./scripts/litai-service.sh plan components/tracker --model claude-fable-5-1
./scripts/litai-service.sh build components/tracker --model claude-fable-5-1 --update-receipt
./scripts/litai-service.sh verify
```

Review the plan and authorize generated host execution before running it. The wrapper
selects Claude Code and the shown model by default, checks the observed Node/Git versions,
and exposes the supported installed `litai` interface. Do not assume the framework's own
Makefile or contributor commands exist in this derived project.

`build --update-receipt` is the delivery path: it admits, builds, tests and exports the
application and refreshes the receipt. A failed build is not accepted. `rebuild` is not a
substitute for checking that the public export has been refreshed. After documentation-only
changes, the supported normal `test --update-receipt` path can refresh current evidence
while reusing the matching accepted source. Inspect `litai help` for installed flags.

Keep tracked authority stable while generation is running. Put temporary diagnostics and
drafts under ignored `_build/`. Changing tracked inputs during a build can invalidate
its evidence even if the generated program itself appears to work.

## Independent checks

Create a local Python environment and install the browser harness dependency:

```sh
python3 -m venv _build/browser-qa
_build/browser-qa/bin/python -m pip install playwright
```

The retained harness uses installed Google Chrome on macOS and Node at
`/opt/homebrew/opt/node@22/bin/node`. Pass the actual accepted source entrypoint:

```sh
_build/browser-qa/bin/python verification/check_all.py /absolute/path/to/accepted/source/main.js --output _build/independent-checks
```

The nine phases cover service protocols, browser login, live MAC status, boards, peers,
heartbeat expiry, Git failure states and equal/irregular-time graphs. They use isolated
storage and synthetic upstreams. Browser screenshots and assertions complement native
acceptance; they do not manufacture a framework receipt.

Run the maintained MAC regression harnesses against the same accepted source. Use a
fresh output directory for each invocation:

```sh
python3 verification/check_mac_timeout.py /absolute/path/to/accepted/source/main.js --output _build/mac-timeout
python3 verification/check_mac_lifecycle.py /absolute/path/to/accepted/source --output _build/mac-lifecycle
_build/browser-qa/bin/python verification/check_mac_writes.py /absolute/path/to/accepted/source --browser --output _build/mac-writes
```

The MAC repair additionally requires complete snapshot reconciliation, dependency/lifecycle
regressions, synthetic write and browser checks, and an actual-service default 60-second
stalled-body test. The installed packaged test runner has a fixed 60-second process
budget, so its native suite tests a short deadline and the full default-budget scenario
runs separately. Neither may report a watchdog-driven cleanup as success.

## Source cache and reproducibility

The project declares operator-bound `standard-local` and project-relative
`project-committed` source caches. The latter lives under `generated/committed-source-cache/`.
Use the supported publication command only after accepting the intended candidate:

```sh
./scripts/litai-service.sh cache publish
```

Do not copy or alter cache internals by hand. Exact generation keys prevent selecting a
mismatched revision; cache hits still undergo current acceptance. Before claiming portable
delivery, commit and push the published cache, use a fresh GitHub checkout, and verify
both actual cache reuse and current isolated acceptance there.

## Review and landing

Keep the work queue, user documentation and `CHANGELOG.md` consistent with the verified
outcome. Run relevant local checks and inspect the actual configured remote checks. A
GitHub secret scan is not an application CI run. Follow the repository's peer-work survey
and landing skill, review the final PR diff, then verify the merge and remote main commit.

The BSD 2-Clause license remains in root `LICENSE`. Do not publish raw private snapshots,
credentials or diagnostic settings in a contribution. Report limitations honestly and
leave incomplete acceptance work open in the queue.
