# Getting started with Project Tracker

[Project guide](../README.md) → getting started

Project Tracker brings repository boards, task activity, physical coding sessions,
and real Git history into one workspace. The browser displays and edits this data;
the backend owns SQLite, upstream credentials, MAC synchronization, MCP and A2A.

## Current availability

The application is still being verified. There is no accepted installation or
background service registration yet. Do not use a retained diagnostic snapshot as
a production installation. The [active work record](../roadmap/active-work.md) and
`verification/product-evidence.md` identify the current
candidate, passing checks and remaining work.

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
configure the reporter's backend connection. The exact installed reporter command
will be recorded here after the accepted artifact's launch path is verified.

Agents can use the official MCP endpoint or A2A. In Agents & peers, register a peer
instance and its backend-stored token, then address a repository ID belonging to
that receiving instance when sending a task request. Retrying the same A2A message
ID must return the original task instead of creating a duplicate.

## Data and operations

`TRACKER_DATA_DIR` selects the backend data directory. Back up the complete directory
while the service is stopped, including its SQLite files and credential file.
Copying a changing database and WAL independently is not a verified backup method.
Restore into a stopped service's data directory and verify health and repository
contents before resuming clients.

The intended default bind is loopback. Remote use requires an access token and an
operator-managed secure endpoint. Final startup, health, upgrade and cleanup
commands remain pending the accepted installation; no service or distribution
package is currently claimed.

## Contributor verification

Specifications are the application authority. The local lifecycle wrapper uses the
pinned Node/npm dependency closure and the selected coding CLI:

```sh
litai lock components/tracker
./scripts/litai-service.sh
litai verify
```

The independent checks under `verification/` exercise
isolated databases, synthetic MAC/LLM endpoints, actual child processes and Chrome.
They do not write to the production fleet or substitute for a LitAI admission
receipt. Generated source and diagnostic output live in disposable build storage.
