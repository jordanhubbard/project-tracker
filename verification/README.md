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
run` launch, and review of the remaining product flows in `docs/user/test-matrix.md`.

Individual checkers accept `--help`, except `check_service.py`, whose command is:

```sh
_build/browser-qa/bin/python verification/check_service.py -- /path/to/node /path/to/main.js
```

Its optional `--diagnostic-continue` flag records independent failures and proceeds
to later phases, then still exits nonzero. Use it to investigate a disposable
candidate, never to turn a failed check into a pass.
