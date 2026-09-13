---
namespace: project-tracker
version: 1.0.0
display_name: Project Tracker
profiles: ["application", "service", "full-stack"]
specification_roots: ["component.md", "runtime.md"]
sample: false
inheritable: false
provides:
  - name: application.portable-json
    version: 1.0.0
requires: []
authoring_inputs:
  - kind: specification-to-source-skill
    uri: skills/specification-to-source/portable-application-implementation/SKILL.md
  - kind: specification-to-source-skill
    uri: skills/specification-to-source/portable-specification-planning/SKILL.md
  - kind: specification-to-source-skill
    uri: skills/specification-to-source/mcp-application/SKILL.md
workflow_definition: workflows/production/staging/dev/workflow.md
routing_policy: routing/production/staging/dev/routing.json
flavor_slots:
  - slot_id: language
    axis: implementation.language-ecosystem
    cardinality: exactly-one
    capability_contract: application.portable-json
  - slot_id: os
    axis: platform.os
    cardinality: exactly-one
    capability_contract: application.portable-json
  - slot_id: build-system
    axis: build.system
    cardinality: zero-or-one
    capability_contract: application.portable-json
  - slot_id: package
    axis: packaging
    cardinality: bounded
    capability_contract: application.portable-json
    minimum: 0
    maximum: 6
entrypoints:
  - name: service
    kind: persistent-service
    path: service
acceptance_contracts: []
source_dependencies: []
---
# Project Tracker

Implement a complete usable application, with a Node.js HTTP backend and semantic HTML,
CSS and browser JavaScript frontend served at `/`. Keep distinct backend service,
SQLite store, MAC adapter, Git reader, protocol adapters and static frontend modules.
No browser build tool is required. Use Node 22.23.2 or newer with node:sqlite and the official MIT MCP JavaScript SDK.
The exact npm manifest and complete lock are specified in runtime.md. Serve an OpenAPI
document at /openapi.json describing the REST request and response schemas.
This component specification overrides inherited read-only/worker-only-write guidance:
operator and peer commands intentionally mutate tasks through one shared service layer.

## Runtime and durable state

`service --host 127.0.0.1 --port 8765` runs the full app. Recognize framework
`--litai-serve --host HOST --port PORT` with identical behavior and `/health` readiness.
Provide `service mcp` stdio transport and `service session` heartbeat reporter modes.
Use TRACKER_DATA_DIR (default platform user application-data directory), never generated
source, for SQLite WAL storage and private settings. Create directory mode 0700 and
secret settings mode 0600. Never seed fake projects in ordinary startup. Provide an
explicit `--demo` isolated sample database for visual inspection, clearly marked Demo.
Support graceful shutdown, transactional schema versioning, foreign keys, revision
checks (409 on conflicting task edits), UTC timestamps and durable append-only events.
A task mutation and its event commit in one transaction. SSE `/api/events` supports
Last-Event-ID replay, keepalives, and resumable ordered IDs across process restarts.

## Repositories and authority

`GET/POST /api/repos`, `GET/PATCH /api/repos/{id}`; fields id, name, local_path,
remote_url, default_branch, authority (local/mac/unresolved), mac_project, description,
last_synced_at, sync_error. Collections use bounded pagination. Register local Git
paths and remote URLs; canonicalize SSH and HTTPS identities, remove trailing .git,
but do not equate unrelated repos just because basenames match. Inspect Git using
subprocess argv with timeouts, never shell interpolation or network clone on user input.

Configure TRACKER_MAC_URL and TRACKER_MAC_TOKEN on backend, with settings UI for URL
and write-only password input. Synchronize `/projects`, `/bridge/repositories`,
`/tasks`, `/agents`, `/machines` on startup and every 5 seconds via a background job.
MAC `/projects` returns summaries with project/project_id/repository_url/metadata;
bridge repositories have id/name/path/source/project/metadata. `source` is a kind such
as "git", not a repository URL. Prefer metadata.repository_url, then project summary
repository_url, then canonical local path. Match normalized repository URL from registry
metadata or canonical local path, with explicit mac_project override for ambiguity.
MAC `/projects/{project}` is project detail. Registry and projects successful enumeration
is needed before declaring absence. A configured unavailable fleet yields unresolved
for new registrations, preserves existing MAC authority and cached last-good data, and
refuses mutations (503), never creates shadow local tasks. No fleet configured permits
local authority. Existing local tasks must not silently vanish if a MAC match appears:
mark migration required and keep local work visible until explicit migration; do not
claim these tasks belong to MAC.

Automatically discover registered MAC repos into overview; registration UI defaults to
matching existing MAC projects, exposes explicit Register with MAC action using
POST `/projects/register` {repository_url,project,default_branch,title,actor:"human"}.
Do not register new MAC projects as a side effect of viewing or configuring the app.
Local repository registration remains available for unmatched repos.

## Tasks and editable workflow

`GET/POST /api/repos/{id}/tasks`, `GET/PATCH/DELETE /api/tasks/{id}`. Fields: id, repo_id,
title, description, state, priority, labels, cover_color, assignee, branch, dependencies,
checklist [{text,done}], due_date, revision, created_at, updated_at, authority. Validate
nonempty titles, known states, bounded text, noncyclic dependencies and repository scope.
Local default states: open, in_progress, blocked, review, completed. Workflow API
`GET/PUT /api/repos/{id}/states` supports adding, renaming, reordering and deleting states;
nonempty deleted states require explicit destination and atomically move tasks. Stable
state IDs differ from display names. Local tasks can move freely; MAC states retain MAC
IDs and lifecycle enforcement, with clear rejection messages and no false success.

MAC task create POST `/tasks` accepts title, description, project, integer priority, metadata,
dependencies and actor. PATCH maps to PUT `/tasks/{id}` for fields; lifecycle change maps
to POST `/tasks/{id}/transition` {target_state,actor:"human",detail:{}}. Store tracker
labels/checklists/cover/branch under metadata.project_tracker while preserving unrelated
metadata. Preserve MAC ID and owner_agent_id. Project-filter task collections locally
if upstream is unfiltered. On multi-step failure refresh actual upstream state and
explain which change applied. Never pretend a network timeout proves absence or success.
Map named UI priorities to documented integer values; default to integer 1, never null.
On each successful sync, upsert every project-scoped upstream task into the board's
read store; preserving a snapshot without updating board reads is insufficient.
Successful projects AND registry enumeration with no match selects local authority.
For example source="git" plus metadata.repository_url="https://example.test/a/b.git"
must match git@example.test:a/b.git; an unrelated URL becomes local after a successful
enumeration, and remains unresolved when either enumeration fails.

## Physical hosts and coding sessions

`POST /api/sessions/heartbeat` and `GET /api/sessions` record session_id, repo_id,
hostname, host_id, cli (codex/claude/cursor/opencode/other), pid, branch, task_id,
model (nullable), status, last_seen_at. Validate heartbeat ownership using backend
access authentication; server supplies time. Active requires running status and heartbeat
within 90 seconds; older sessions show stale, explicit exit shows stopped. Don't equate
agent heartbeat, debug terminal, or task assignment alone to active coding CLI execution.
Show agent assignments separately when MAC only supplies those facts.

`service session --repo PATH --cli NAME -- COMMAND...` registers the canonical repo,
starts the requested CLI with inherited terminal IO, reports physical socket hostname,
pid and branch every 20 seconds until it exits, and sends stopped status in finally.
TRACKER_URL and TRACKER_ACCESS_TOKEN configure this host-side reporter, which must run
on remote hosts without database access. No credentials in arguments or output. Handle
backend outages without killing the coding CLI. Expose install/run instructions.

## Real Git branch visualization

`GET /api/repos/{id}/graph` returns bounded commits (hash, parent hashes, author,
subject, authored_at, committed_at), refs and heads, and worktrees. Use `git log --all
--topo-order` and `for-each-ref`; detached HEAD and unborn repositories are handled.
Include parents outside the bounded window as boundary nodes. Display actual merge
edges, forks, branch tip labels, timestamps and active task/session branch overlays.
Graph mode draws SVG node-edge DAG; timeline mode positions by time with lanes and
explicit timestamp axis. Both offer zoom/reset, scroll/pan, node selection with commit
inspector, branch filter and task links. Never infer parent edges from chronological
adjacency. Remote-only repos show checkout-needed state, not a fabricated graph.

## Backend LLM configuration

Backend settings include gateway URL, API key, model and request timeout. Environment
TRACKER_LLM_URL, TRACKER_LLM_KEY and TRACKER_LLM_MODEL supply defaults. Settings GET
returns only configured booleans for secrets; password fields never refill existing
keys. Blank preserves; an explicit clear operation removes. Backend-only call
POST `/api/assistant` accepts a question and repo_id and uses gateway `/chat/completions`
with bounded repository/task context, server-side bearer key and timeout. Return answer
and source context IDs; no key in browser requests, SSE, errors, logs or database
exports. LLM unconfigured has a clear UI state; core task work never depends on LLM.
Assistant only summarizes/suggests, does not execute commands or silently mutate tasks.

## MCP and agent peering

Use the official @modelcontextprotocol/sdk for stdio and mounted Streamable HTTP `/mcp`, supporting SDK
initialize, list and tool calls. Share task authorization and data service, not a second
store. Tools: list_repositories, list_tasks, get_task, create_task, update_task,
list_sessions, get_branch_graph. Resource tracker://repositories. Validate all input;
unknown tools and missing tasks return protocol errors. Do not claim an unsupported
protocol version; advertise the negotiated SDK-supported version. Use real SDK clients
in tests. HTTP auth protects MCP mutations just as REST.

Implement A2A JSON-RPC at `/a2a`, publish `/.well-known/agent-card.json`; pin and
explicitly advertise supported A2A 0.3.0 (not unsupported latest). Use protocol-conformant
message/send, tasks/get, tasks/cancel, Task with kind/id/contextId/status/artifacts,
Message with kind/role/messageId/parts, DataPart with kind:data and validated operation.
Operations list_repositories/list_tasks/get_task/create_task/update_task share REST
service. Returned A2A Tasks and input message IDs are durable; retries are idempotent.
Completed synchronous operations cannot be cancelled (TaskNotCancelable error), unknown
methods -32601, malformed params -32602, unknown task -32001. Card declares only
implemented capabilities and required auth. A2A task IDs must not be confused with work
board IDs. Support peer registration GET/POST/DELETE `/api/peers`, stored URL and fetched
validated agent card, plus POST `/api/peers/{id}/messages` for outbound message/send
using a per-peer backend-only token. Explicit operator registration authorizes card fetch;
no automatic requests to arbitrary message-provided URLs or redirects. Peer failures
show errors and retain history. Protocol references:
https://a2a-protocol.org/v0.3.0/specification/ and
https://github.com/modelcontextprotocol/typescript-sdk .

## Access and validation

Loopback is default. Non-loopback bind requires TRACKER_ACCESS_TOKEN. Accept bearer
auth for API, MCP and A2A and authenticated same-origin browser session using HttpOnly
SameSite cookie login. Reject cross-origin mutation and SSE requests. Don't put bearer
secrets in URLs or browser localStorage. Token protected deployments serve only login,
health and discovery publicly, never project data. Reject foreign Host/Origin for local
unauthenticated requests to protect against DNS rebinding. No external CORS wildcard.
Configured upstream URL must be HTTP(S), no embedded credentials; disable redirects
on authenticated upstream requests. Bounded timeouts and sanitized errors everywhere.

## Visual and interaction contract

Faithfully reinterpret the supplied Trello screenshot. Dark charcoal application chrome,
navy left rail (~280px), wide horizontal scroll board, near-black rounded columns
(~290px), charcoal task cards with rounded 10px corners, white-grey text, small colored
label pills and occasional full purple/blue/green/orange card covers. Top search field,
workspace title and toolbar; blue action buttons. Calm subtle landscape-like CSS board
background, no external image dependency. Do not reproduce browser tabs or the Trello
billing warning. Use system sans-serif, comfortable 14px body text, strong focus rings.

Header Project Tracker, global search, connection status, Create and Settings. Left
sidebar Repositories with All projects and selectable repo rows, active session counts,
Activity and Agents & peers. Main overview shows repo cards with task-state counts,
authority and host activity; click leads to that repo board and Inspector button. Board
has title, authority badge, Board/Timeline/Graph/Fleet tabs, filter and Add task. Cards
show title, labels, checklist progress, branch, assignee and actual task state. Click
opens accessible modal/task drawer editing all task fields; save commits, cancel does
not. Drag between lists updates server, keyboard-accessible Move to select does the same.
A failed save/move retains draft, restores card position, and shows actionable error.
Add list and list menu edit workflow. Persist board selection in URL hash (deep links).

Repo inspector shows Git origin/path/default branch, authority/sync freshness, MAC link,
active physical host sessions, task metrics and editable description. Fleet view shows
host, CLI, branch, task, last heartbeat and explicit active/stale/stopped status. Activity
feed shows human-readable task creation, state and attribute edits in time order.
All live SSE events update counts/cards/details without page reload or discarding an
unsaved edit; flag conflicting edits. Distinct loading/empty/offline/stale/error views.
At 390px viewport use collapsible sidebar and locally horizontally scrolling board;
no page-level horizontal overflow. Accessible form labels, semantic landmarks, focus
trap/escape for dialogs, keyboard operable controls, reduced-motion support.
Settings UI manages MAC and LLM URLs, write-only credentials, peers, connection tests.

## Required verification

Generated tests exercise real HTTP and SQLite persistence after restart, replayed SSE,
concurrent edit conflict, workflow migration, task metadata/dependencies validation,
MAC fixture match and task writes, outage without local fallback, SSH/HTTPS identity,
heartbeat expiry, real temporary Git fork and merge graph with bounded ancestry,
LLM mock verifying server-side secret and browser redaction, MCP SDK tool roundtrip,
A2A malformed methods/idempotency/get/cancel and two peer app instances.
Browser tests at desktop and mobile verify overview -> board -> create/edit/move task,
state editing, search, inspector, graph/timeline selection, SSE update from second client,
settings redaction, peer flow, no console errors and no page overflow. Isolate tests
from user's real fleet and database. Never contact production upstreams during tests.
Document launch, configuration, backup, MAC authority behavior, reporter deployment,
protocol client examples and known limits in generated README. Smoke run verifies actual
store/API, not fabricated summary output. Acceptance must launch the full service.

## Completeness requirements from candidate review

Implement every named UI view in this application. Graph and Timeline must render
interactive SVG edges/nodes and a timestamp axis; a JSON dump or instruction for other
clients to render them is not an implementation. Provide working repository registration,
workflow editing, settings, peer management, session fleet and repository inspector
controls. Task editing must preserve fields the user did not change, including cover,
checklist, dependencies and due date. Support drag and accessible move controls.

Instantiate and schedule the MAC adapter in the actual application lifecycle. Successful
snapshots must import/match projects and route writes to the right MAC endpoint. A
standalone unused client class does not implement the integration. Implement persistent
settings and peer routes, with their UI forms connected to actual backend writes.
Register named SSE event listeners (or handle every event through a stream parser): an
onmessage-only listener does not receive named task events. Update cards on remote edits.

Before finishing generation, audit every section of this Component against actual source
and tests. Fix omissions instead of declaring requested behavior a known limit. Keep
modules readable and split by backend store, MAC, Git, sessions, settings, LLM, MCP, A2A,
peers, HTTP, frontend board, frontend graph and frontend dialogs. Do not trim the product
to fit a single small file. Tests and smoke modes must call product behavior.
