# Project Tracker

A repository and task workspace with live boards, physical coding-session activity,
Git relationship graphs and timestamp timelines. A Node.js backend owns SQLite,
MAC synchronization, MCP, A2A peering and LLM credentials.

[Start here](docs/user/getting-started.md) · [Full documentation](docs/README.md) ·
[Verification status](docs/user/verification.md) · [Active work](docs/roadmap/active-work.md)

The project is persisted on [GitHub](https://github.com/jordanhubbard/project-tracker).
MAC repair acceptance is tracked separately from source publication; consult the current
verification record before treating an export as the accepted application.

## Build and run

The current toolchain is macOS, Node.js 22.23.2, Git 2.30.0 or newer, and installed
Literate AI 1.0.1. Git 2.50.1 is the version recorded by the accepted build evidence.
The wrapper selects Claude Code by default; the coding provider must be configured for
generation. See [setup](docs/user/getting-started.md) for requirements and limitations.

```sh
make build
export TRACKER_DATA_DIR="$HOME/Library/Application Support/project-tracker"
make run
```

After a successful build, open `http://127.0.0.1:8765`. `GET /health` reports service
readiness; repository sync status reports MAC health. Add `"--demo"` inside the argument
array, or use `make demo`, for an isolated sample workspace. Stop the foreground service
with Ctrl-C. Run `make help` for lifecycle shortcuts and configurable host, port, model,
and Component values. The Makefile delegates to `scripts/litai-service.sh`; it does not
replace the selected JavaScript/npm application build strategy.

## Work with projects and tasks

Register a local checkout or remote repository URL and open its board. Create, edit,
label and move tasks; customize local workflow lists; inspect dependency references;
and receive committed changes live. A local checkout enables Graph and Timeline with
real forks, merges, refs, task links and physical-host session associations.

MAC owns tasks for matched projects. Confirmed absence permits local tracking. Upstream
outages preserve cached data and reject MAC writes instead of creating shadow local work.
Read [projects and tasks](docs/user/projects-and-tasks.md) and
[MAC integration](docs/user/mac-integration.md) for the full behavior.

## Configure connections

| Variables | Purpose |
| --- | --- |
| `TRACKER_DATA_DIR` | Private database/settings directory |
| `TRACKER_ACCESS_TOKEN` | Browser sign-in and client bearer authentication |
| `TRACKER_MAC_URL`, `TRACKER_MAC_TOKEN` | Backend MAC connection |
| `TRACKER_MAC_FLEETS_FILE` | Private JSON file for multiple named MAC fleet connections |
| `TRACKER_LLM_URL`, `TRACKER_LLM_KEY`, `TRACKER_LLM_MODEL` | Backend assistant gateway |
| `TRACKER_URL` | Host-side reporter destination |

Saved settings override environment defaults. Blank secret inputs preserve credentials;
explicit clear removes them. Non-loopback service binding requires an access token.
See [configuration](docs/user/configuration.md) and [security](docs/user/security.md).

## Agents and physical coding sessions

MCP is available at `/mcp` and through `["service","mcp"]`. A2A 0.3.0 uses `/a2a`,
with its card at `/.well-known/agent-card.json`. REST schemas are at `/openapi.json`.
See the [API reference](docs/reference/api.md) for authenticated client examples.

Run the reporter on the host where the coding CLI actually executes:

```sh
export TRACKER_URL=http://127.0.0.1:8765
./scripts/litai-service.sh run components/tracker '["service","session","--repo","/absolute/repo/path","--cli","codex","--","codex"]'
```

It wraps the child and reports physical hostname, PID, branch and lifecycle without
requiring database access. See [sessions and peers](docs/user/sessions-and-peers.md).

## Development and operations

- [Development](docs/user/development.md): change specifications and use the supported lifecycle.
- [Architecture](docs/architecture/application.md): shared service, authority and transaction boundaries.
- [Operations](docs/user/operations.md): backup, restore, shutdown and upgrades.
- [Troubleshooting](docs/user/troubleshooting.md): diagnose runtime, connection and toolchain problems.
- [Product objective](PROJECT.md), [Component specification](components/tracker/component.md),
  root `CHANGELOG.md`, and [contributing](docs/user/contributing.md).

## Release engineers

- `jordanhubbard`

The first stable release is being prepared as v1.0.0. Publication requires accepted
tracker tests and verified packages. Current runtime evidence and remaining gates
are reported in [verification](docs/user/verification.md).

## License

[BSD 2-Clause](LICENSE).
