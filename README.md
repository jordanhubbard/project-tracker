# Project Tracker

A repository and task workspace built with LitAI: Trello-style boards, live task
updates, physical coding-session activity, Git relationship graphs and timestamp
timelines. The Node.js backend owns SQLite, MAC synchronization, MCP, A2A peering
and LLM credentials.

- [Product objective](PROJECT.md)
- [Application specification](components/tracker/component.md)
- [Active work and verification](docs/roadmap/active-work.md)
- [Project guide](docs/README.md)

MAC synchronization repair is in progress under TRACK-004. Live import, atomic
failure recovery and unresolved-reference/long-text edit preservation pass on the
latest candidate. New dependency selection and a Git branch-filter regression
remain open. See the active work record for current acceptance status.

## Run

After a successful LitAI build, launch the exported application:

```sh
./scripts/litai-service.sh run components/tracker '["service","--host","127.0.0.1","--port","8765"]'
```

Open `http://127.0.0.1:8765`. Readiness is `GET /health`. Add a repository from the
workspace and supply its local checkout path for Git visualizations. Configure the
MAC endpoint and LLM gateway in Settings or through backend environment variables.

For an isolated sample workspace, add `"--demo"` inside the JSON argument array.

When `TRACKER_ACCESS_TOKEN` is configured, the browser presents Sign in. Enter the
token in that form; the backend establishes an HttpOnly session cookie. Reloading
reuses the session. API clients use `Authorization: Bearer ...`; keep the token in
the backend/client environment rather than a URL.

## Build

The wrapper requires the declared Node 22.23.2 and Git 2.50.1 toolchain, and selects
Claude Code with `claude-fable-5-1` for generation. LitAI installs the exact npm lock.

```sh
./scripts/litai-service.sh lock components/tracker
./scripts/litai-service.sh build components/tracker --model claude-fable-5-1 --update-receipt
./scripts/litai-service.sh verify
```

## Backend configuration

| Environment variable | Purpose |
| --- | --- |
| `TRACKER_DATA_DIR` | Private SQLite and settings directory |
| `TRACKER_MAC_URL`, `TRACKER_MAC_TOKEN` | MAC fleet connection |
| `TRACKER_LLM_URL`, `TRACKER_LLM_KEY`, `TRACKER_LLM_MODEL` | LLM gateway connection |
| `TRACKER_ACCESS_TOKEN` | Backend bearer authentication; required for non-loopback binding |

Without `TRACKER_DATA_DIR`, data lives in the platform's per-user application-data
directory (`~/Library/Application Support/project-tracker` on macOS). Set an
absolute directory when running an isolated instance or keeping a separate demo.

Saved settings take precedence over environment defaults. Blank credential fields
preserve stored credentials; explicit clear removes them. Credentials stay on the
backend and API responses report only whether they are configured.

MAC owns tasks for matched repositories. Confirmed absence permits local tracking.
A fleet outage preserves cached tasks and rejects upstream mutations with 503;
existing local tasks require explicit migration before MAC ownership.

## Physical coding sessions

Run the reporter on the host where the coding CLI executes, with the backend URL
and access token in its environment:

```sh
export TRACKER_URL=http://127.0.0.1:8765
./scripts/litai-service.sh run components/tracker '["service","session","--repo","/absolute/repo/path","--cli","codex","--","codex"]'
```

It launches the real child process, reports its host, PID and branch, and records
its stopped lifecycle. A backend outage does not terminate the coding child.

## Agent interfaces

MCP is available at `/mcp` and through the stdio command:

```sh
./scripts/litai-service.sh run components/tracker '["service","mcp"]'
```

The A2A endpoint is `/a2a`, with its card at `/.well-known/agent-card.json`.
Register authenticated outbound peers by their base URL in Agents & peers. REST routes are described
at `/openapi.json`.

## Verification

Verified artifact: `artifact-6119bda93ad771d2ed03` (authority `e09a08c`).
All 28 native tests and nine independent phases passed, plus public launch and
failure-state probes. See [completion evidence](docs/user/verification.md)
and the [machine-readable result](verification/final-result.json).

Run the independent checks against the exported source:

```sh
_build/browser-qa/bin/python verification/check_all.py generated/artifacts/tracker/artifact-6119bda93ad771d2ed03/source/main.js
```

The retained QA environment uses Playwright and installed Google Chrome. Tests
create isolated data and fixture endpoints. MAC integration was verified against
an authenticated contract fixture, without production fleet mutations.

## Release engineers

No public release or fleet installation is configured or claimed.
