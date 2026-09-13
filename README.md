# Project Tracker

A repository and task workspace built with LitAI. The intended application combines
Trello-style task boards, physical coding CLI session activity, Git branch timelines
and relationship graphs. A Node.js backend owns SQLite, MAC synchronization, MCP, A2A
peering, and LLM gateway credentials. The browser owns visualization and editing.

**Status:** specification and acceptance contract authored; application generation and
verification in progress. There is no verified runnable application yet.

- [Product objective](PROJECT.md)
- [Application specification](components/tracker/component.md)
- [Active work and verification](docs/roadmap/active-work.md)
- [Project guide](docs/README.md)

Build and verify with the installed LitAI CLI:

```sh
litai lock components/tracker
./scripts/litai-service.sh
litai verify
```

The wrapper selects the installed Node 22 runtime, checks the observed Git 2.50.1
build dependency, and selects Claude Code's direct file tools for generation. LitAI replays the
exact npm lock through its supported dependency lifecycle. Build diagnostics and
independent service/browser checks are recorded in the active work document.

MAC is authoritative for matched projects; unmatched repositories use local tasks.
An unavailable configured fleet must never be mistaken for an unmatched repository.
The product defaults to loopback and keeps all upstream credentials on the backend.

## Release engineers

No public release is configured or claimed. Complete the active acceptance checklist
before preparing distribution artifacts.
