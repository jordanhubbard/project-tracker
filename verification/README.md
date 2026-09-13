# Independent product checks

Run with a Python environment containing the official `mcp` client and Playwright,
Node 22+, Git, and Google Chrome installed. The local verification environment is
`_build/browser-qa/bin/python`.

```sh
_build/browser-qa/bin/python verification/check_all.py /absolute/path/to/main.js
```

The command runs service/protocol checks, desktop/mobile board interactions, and
real Git graph checks with equal and unequal commit timestamps. Each phase starts
isolated temporary databases and local fixtures. Results and browser screenshots
are written beneath `_build/independent-checks`; `summary.json` records every phase
and remains incomplete until all phases finish. A failed phase produces a nonzero
exit status. Review screenshots as well as the behavioral results.

These are independent product diagnostics. They do not generate or replace LitAI's
native acceptance, source custody, or `verification/current.json` receipt. Final
verification also requires a successful authorized LitAI lifecycle, public `litai
run` launch, and review of the remaining product flows below. The inherited private worker
matrix documentation describes framework workers, not product acceptance.

Individual checkers accept `--help`, except `check_service.py`, whose command is:

```sh
_build/browser-qa/bin/python verification/check_service.py -- /path/to/node /path/to/main.js
```

Its optional `--diagnostic-continue` flag records independent failures and proceeds
to later phases, then still exits nonzero. Use it to investigate a disposable
candidate, never to turn a failed check into a pass.

## Additional product review

After the automated suite passes, review these flows against the same artifact:

- Compare the desktop board with the supplied Trello reference: dark card/list
  surfaces, colored covers and label strips, horizontal columns, sidebar, toolbar,
  readable card metadata and visible focus. Inspect mobile screenshots for usable
  scrolling, dialogs and controls.
- Register a repository through the UI, inspect its authority and metadata, use
  repository/task search, and open task details from the overview and activity.
- Drag a task to another state and confirm a second browser receives the move.
  Rename, reorder, add and delete workflow states with task migration handling.
- Exercise filters, repository inspector, commit-to-task links and graph empty,
  missing-path and truncated-history states.
- Register an isolated peer through the UI, send a task request and inspect history,
  then remove it. Verify both success and unavailable-peer feedback.
- Display an actual reporter child session in the fleet and repository views with
  its host, process, CLI and branch; observe stopped/expired state.
- Exercise the assistant UI against a local mock gateway, including configured,
  unconfigured and upstream-error states. Confirm browser responses contain no key.
- Verify visible MAC offline/unresolved indicators and actionable conflict errors;
  fixture outages must preserve cached tasks without enabling local shadow writes.

Record actual results and any unexecuted scenario explicitly. A successful service
health response or generated native test suite alone does not cover these flows.
