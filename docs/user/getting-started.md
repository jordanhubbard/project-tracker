# Getting started with Project Tracker

[Project guide](../README.md) → getting started

Project Tracker brings repository boards, task activity, physical coding sessions,
and real Git history into one workspace. The browser displays and edits this data;
the backend owns SQLite, upstream credentials, MAC synchronization, MCP and A2A.

## Current availability

The local application is built and verified. See the
[completion evidence](verification.md) for the artifact,
passing checks and validation scope. Launch the exported application from the
repository root:

```sh
./scripts/litai-service.sh run components/tracker '["service","--host","127.0.0.1","--port","8765"]'
```

Open `http://127.0.0.1:8765`. `GET /health` reports readiness. Add `"--demo"`
inside the argument array for a separate sample workspace. If
`TRACKER_ACCESS_TOKEN` is configured, sign in through the visible token form.

This local build targets macOS with Node.js 22.23.2, the observed Git 2.50.1 host
runtime, and the installed LitAI CLI. Other host installations have not been
validated. A local checkout is needed to display a repository's real Git history;
a remote URL alone is enough to identify a repository and track its tasks.

## Repository and task workflow

The overview lists tracked repositories and their task/session counts. Open a
repository to use its board. Each list represents a workflow state. Create a task,
open a card to edit its details, or move it through the accessible move control or
drag and drop. Task details include description, labels, priority, assignee, branch,
due date, cover, checklist and dependencies. Changes arrive live from other clients.

The repository inspector shows origin, local checkout, authority, synchronization
state and task/session information. Graph shows actual parent relationships;
Timeline spaces commits by time. Select a commit to inspect its hash, parents,
author and subject. Branch filters and zoom controls help explore the history.
Activity shows task changes. Fleet shows reported physical-host sessions.

## MAC authority and settings

Configure the MAC fleet URL and credential in Settings when the tracker should
use an existing fleet. Matching MAC projects remain authoritative: edits use MAC's
APIs and rejected transitions stay rejected. A successful discovery with no matching
project permits local tracking. An unavailable configured fleet cannot establish
that a repository is unmatched; unresolved writes fail until discovery succeeds.
Existing cached fleet data remains visible during an outage.

Settings also holds the assistant gateway URL, model and backend-only key. The
tracker appends the chat-completions path to the configured gateway prefix. Blank
credential fields preserve saved secrets; explicit clear controls remove them.
The browser never receives saved secret values. Core repository/task work does
not require an LLM connection.

## Physical coding sessions and peers

Session visibility requires a reporter on the physical host running the coding
CLI. It wraps the actual child process and reports hostname, PID, CLI, checkout and
branch to the tracker. A stopped child is shown as stopped; a lost heartbeat expires
instead of remaining active indefinitely. `TRACKER_URL` and `TRACKER_ACCESS_TOKEN`
configure the reporter's backend connection. Run it on the physical host where the coding CLI executes:

```sh
export TRACKER_URL=http://127.0.0.1:8765
./scripts/litai-service.sh run components/tracker '["service","session","--repo","/absolute/repo/path","--cli","codex","--","codex"]'
```

The reporter survives a backend outage without terminating the coding child.

Agents can use the official MCP endpoint or A2A. In Agents & peers, register a peer
instance by base URL and its backend-stored token, then address a repository ID belonging to
that receiving instance when sending a task request. Retrying the same A2A message
ID must return the original task instead of creating a duplicate.

## Data and operations

`TRACKER_DATA_DIR` selects the backend data directory. Back up the complete directory
while the service is stopped, including its SQLite database and sidecars.
Copying a changing database and WAL independently is not a verified backup method.
Restore into a stopped service's data directory and verify health and repository
contents before resuming clients.

The default bind is loopback. Remote use requires an access token and an
operator-managed secure endpoint. Stop the foreground service with Ctrl-C. Rebuild through the supported lifecycle
and restart the exported application when changing specifications. No background
service or distribution package is required for this local workspace.

## Contributor verification

Specifications are the application authority. The local lifecycle wrapper uses the
pinned Node/npm dependency closure and the selected coding CLI:

```sh
./scripts/litai-service.sh lock components/tracker
./scripts/litai-service.sh build components/tracker --model claude-fable-5-1 --update-receipt
./scripts/litai-service.sh verify
```

The independent checks under `verification/` exercise
isolated databases, synthetic MAC/LLM endpoints, actual child processes and Chrome.
They do not write to the production fleet or substitute for a LitAI admission
receipt. Generated source and diagnostic output live in disposable build storage.
