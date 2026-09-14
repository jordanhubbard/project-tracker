# Test matrix

[Documentation](../README.md)

The current product verification target is the local macOS host with the declared
Node/Git toolchain. It does not establish Windows/Linux runtime support, remote worker
readiness, or a passing multi-platform CI matrix.

## Local layers

| Layer | Evidence |
| --- | --- |
| Authority | `project validate`, generated lock/plan and reviewed documentation |
| Supported lifecycle | Source/dependency admission, build, native tests, persistent-service acceptance and receipt |
| Independent service | Actual REST, SQLite restart, official MCP clients, A2A, MAC/LLM fixtures and child processes |
| Independent browser | Chrome at desktop 1440px and mobile 390px, live updates and graph interactions |
| MAC scale and recovery | Complete captured snapshot, synthetic edits, lifecycle and default-timeout fixtures |
| Live MAC | Isolated read-only synchronization against the real hub |
| Portable delivery | Fresh GitHub checkout, exact source-cache reuse and fresh current acceptance |

See [development](development.md#independent-checks) for execution and
[verification](verification.md) for actual results. Each result is tied to its own
artifact; passing an older candidate does not automatically validate a regenerated one.

## Optional private workers

`literate.workers.example.json` and `literate.test.example.json` are inert examples.
Use `litai config paths` to identify the operator's durable configuration destinations.
Keep real worker names, endpoints and credentials out of Git. `LITAI_TEST_CONFIG` and
`LITAI_WORKER_CONFIG` can select private files.

Use the installed `litai worker probe --all` before capability-gated remote work.
Observed worker health does not change declared platform requirements. Do not claim
remote acceptance until the configured worker has built and tested the exact artifact
and returned evidence through the supported lifecycle.

This derived project uses installed `litai` commands. Examples requiring the framework's
own Makefile or sample-suite checkout do not apply here.
