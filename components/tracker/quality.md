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

Before finishing generation, audit every section of this Component against actual source
and tests. Fix omissions instead of declaring requested behavior a known limit. Keep
modules readable and split by backend store, MAC, Git, sessions, settings, LLM, MCP, A2A,
peers, HTTP, frontend board, frontend graph and frontend dialogs. Do not trim the product
to fit a single small file. Tests and smoke modes must call product behavior.
