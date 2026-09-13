---
name: Product verification and completeness
summary: Required behavior coverage and complete user-facing integration
kind: verification
---
# Product verification and completeness

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

Publish committed changes to already-connected SSE clients promptly (within one
second locally); the 15-second keepalive timer is not the delivery mechanism.
Verify a second HTTP client creates and edits a task while the browser stays on its
board, and observe each change within two seconds without navigation or reload.

The outbound peer endpoint accepts `{message: <A2A Message>}`. Validate and forward
that complete message to the registered peer using JSON-RPC message/send. Preserve
its messageId and DataPart contents so retries create one remote task and return
the same remote A2A Task ID. Do not replace it with an empty `input.data` object or
mint a new messageId for each retry. The browser peer form must construct this same
documented shape. Test two actual local service processes with a token on the
receiving process, register the peer, send a create_task message, retry it, and
verify one remote board task. Keep credentials backend-only throughout history.

Before finishing generation, audit every section of this Component against actual source
and tests. Fix omissions instead of declaring requested behavior a known limit. Keep
modules readable and split by backend store, MAC, Git, sessions, settings, LLM, MCP, A2A,
peers, HTTP, frontend board, frontend graph and frontend dialogs. Do not trim the product
to fit a single small file. Tests and smoke modes must call product behavior.

Keep generation output bounded: avoid repeatedly printing the full lockfile, source
BOM or whole minified modules. Write files and inspect concise summaries or selected
ranges. The installed source-generation transport has a 16 MiB stderr limit; avoid
exhausting it with repeated dumps while retaining all required source and metadata.

The portable application entrypoint consumes one JSON array argument. Decode that
array before dispatching service, mcp and session subcommands; also retain direct
--litai-serve/--litai-test/--litai-smoke flags. Explicitly exercise
`["service","mcp"]` through an official stdio client and
`["service","session","--repo",PATH,"--cli","other","--",COMMAND,...]`.
Treating the complete JSON string as an unknown argv item and starting the default
HTTP server is a regression. Standard I/O MCP, HTTP MCP, A2A and REST must all invoke
the same MAC-aware service mutations; no protocol adapter may call the local store
directly for a MAC task. Initialize required MAC readiness for stdio as for HTTP.
Implement MAC field edits and transitions completely; returning 501 for the named
MAC edit flow is not an acceptable partial implementation.

## Concrete regression scenarios

Framework test metadata uses canonical JSON v1, which permits integer numbers but
rejects fractional numbers. Choose native test vectors whose full expected results
are representable (or test a specified textual SVG response); do not put a fractional
coordinate such as 0.1 into the generated manifest. This metadata constraint does not
remove timestamp-proportional spacing from the browser product.

Load the root page and every transitive ES-module import through the real HTTP
server. A module named /api.js is a static asset, not the /api namespace: match route
boundaries (/api or /api/...), never an arbitrary startsWith('/api'). Assert the
seeded repository card appears and the connection indicator becomes connected.

Persist A2A Task records and messageId-to-Task associations in SQLite. After a full
service restart, tasks/get returns the same Task, and retrying message/send with the
same messageId returns that Task without creating a second board task. An in-memory
Map alone does not meet durable peering behavior.

Register a peer with a disposable bearer token, then inspect both the POST response
and GET listing. Neither may contain the token; expose only credential presence.
Use the stored token exclusively for backend outbound authentication.

With MAC configured, import a task whose metadata.project_tracker.labels is ['fleet']:
the board task labels must be ['fleet']. Repeat an identical successful poll: task
revision, updated_at and SSE task-change events remain unchanged. Preserve unrelated
metadata on subsequent edits. If MAC rejects a completion transition, return a clear
non-success response and preserve cached state; do not return HTTP 200 for a rejected
operation. After a successful discovery, make MAC unavailable and register a previously
unknown repository. Its authority remains unresolved and task creation returns 503;
absence from a stale cached snapshot never confirms local authority during an outage.

## Interaction and session regressions

A completed task save updates the visible card and its revision before another card
operation uses that object. Verify edit description -> Save -> immediately Move to
another state with no reload or artificial pause: the move persists and the saved
labels/description remain intact. Do not leave the pre-save task object in a move
callback. A failed save keeps the editable draft available. Genuine concurrent
external edits still produce a conflict with explicit reload/reapply controls; never
silently overwrite them to make this sequence pass.

Coalescing asynchronous renders must retain a pending refresh. If a mutation, SSE
event or navigation occurs during an in-flight fetch/render, schedule a follow-up
render for the newest state and route. Returning the old pending promise and dropping
the new request is incorrect. Refresh repository overview/sidebar counts when tasks
or sessions change rather than keeping the first fetched overview forever.

At 390px, Settings remains reachable via a visible labelled control in the header or
sidebar. Do not hide the only Settings button with a mobile media query. Exercise the
same saved URL/model and blank write-only key flow on desktop and mobile; a compact
button or sidebar control is acceptable when header space is tight.

A physical session heartbeat is a committed live change: publish an SSE session event
for start/update/stop and subscribe to it in the frontend. Keep the Fleet/Agents rows,
repo inspector and overview active-session counts current. In a real reporter test,
show the spawned child's hostname, PID, CLI and branch; release the child and display
stopped within two seconds without navigating or reloading. Expiry must also update
the visible derived status and counts after the configured heartbeat deadline.
Persist relevant session events for replay. The event name is an implementation
choice, but emitting and subscribing must agree across every entity change surface.

Peer messaging UI addresses the receiving instance's repository IDs. Never populate
"Remote repository id" from the sender's local overview: two instances assign
different IDs even when they track similar URLs. Either accept a validated explicit
remote ID in a labelled text input, or discover the peer's repositories through the
backend using its stored credential and present that remote catalogue. In a two-
instance UI scenario with disjoint repositories, register the receiver, choose or
enter its repository ID, send a create_task request and observe that task in the
receiver's database plus a useful result/history entry in the sender. Keep tokens
backend-only; do not require a direct authenticated browser fetch to the peer.


## Additional observed browser and identity regressions

A running session whose last heartbeat reaches 90 seconds must become stale in an
already-open Fleet view and its sidebar active count must become zero, without any
new HTTP mutation, heartbeat, navigation or page reload. A read-time status helper
alone cannot notify an idle browser. Schedule bounded deadline checks in the service,
publish persisted expiry changes exactly once per status transition, and refresh
all session views/counts. A subsequent fresh heartbeat can reactivate that session.

Canonicalize existing local checkout paths through filesystem realpath before
identity matching. Register a real checkout, then register a symlink to it: return
the same repository or an explicit duplicate conflict without a second record.
The reporter's Git-resolved root must associate with this same repository. On macOS,
/var and /private/var aliases must not create different repositories. Preserve the
specified remote-origin canonicalization and MAC authority rules.

Constrain application grid/flex tracks and children so their intrinsic board widths
do not widen the document. At both 1440px and 390px, document.scrollWidth must not
exceed the viewport; the board itself scrolls horizontally to reveal every column.
Use shrinkable tracks/children (for example minmax(0,1fr) and min-width:0) where
needed. Do not merely clip body overflow and leave controls offscreen. Repository
metric labels use human state names, never UUID-prefixed internal state IDs.

Click Send message on a registered peer and assert a usable dialog opens with no
browser exception, then send an actual remote task. Browser crypto methods require
their receiver: use crypto.randomUUID() as a method call or bind it explicitly;
extracting the function and invoking it unbound throws Illegal invocation in Chrome.
Generate the retry-stable message ID once per message draft and retain it on retry.
