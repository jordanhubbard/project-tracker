---
name: Live MAC operations and agent sessions
summary: Resumable fleet activity, visible agent conversations and audited steering
kind: integration
---
# Live MAC operations and agent sessions

## Scope and upstream authority

Project Tracker is an operations oscilloscope for MAC. Projects, tasks and agent
sessions are equal top-level entities with stable detail routes, live state, bounded
history and explicit links among project, task, repository, agent, machine, branch and
session identifiers. MAC remains authoritative for MAC project, task, agent and machine
state. The tracker may cache and index that state, but it must not infer a task transition
or agent outcome from terminal text.

Use MAC's authenticated `GET /events/stream` newline-delimited event feed as the primary
incremental source and persist the last committed upstream sequence. Reconnect from that
cursor without skipping or duplicating records. Use `GET /events` to fill a bounded gap
when a stream is unavailable and the existing `/projects`, `/tasks`, `/agents` and
`/machines` snapshot synchronization to reconcile current state at startup, after a gap
and every 30 seconds. A hub without the stream endpoint falls back to five-second
snapshots and clearly reports polling mode. `/news/stream` is a human summary, not the
canonical state feed.

The upstream and downstream streams are separate obligations. For every configured MAC
fleet, service startup must actively open `GET /events/stream` on that fleet with its
`Authorization: Bearer` credential and an NDJSON-compatible `Accept` header, parse
complete newline-delimited records, and reconnect from the committed cursor. Implementing
only the tracker's client-facing `/api/events` SSE endpoint or periodic `/events` polling
does not satisfy upstream streaming. Start the upstream connection alongside initial
snapshot reconciliation rather than waiting for a browser to connect or for the first
poll interval. The generated fixture must observe this authenticated request on the real
service startup path before native acceptance succeeds.

Each imported upstream event is committed with its current-state projection in one
SQLite transaction, then published through the tracker's authenticated SSE stream. Key
deduplication is `(upstream_instance, upstream_sequence)`; local event IDs remain ordered
and resumable through `Last-Event-ID`. A reconnect, identical snapshot or repeated event
must not advance entity revisions or create duplicate activity. A cursor discontinuity
sets `resyncing`, performs a full snapshot, and returns to `live` only after the snapshot
commits. Preserve last-good state and show `stale` with the last event time during an
outage.

Retain at most 10,000 live-operation events or seven days, whichever is smaller, while
keeping the current projection for every known entity. Prune only events older than every
connected listener's replay cursor; disconnect a listener whose lag would exceed the
bound and require a snapshot refresh. Paginate and virtualize large collections so a
fleet containing at least 10,000 tasks remains usable without loading every history row
into the browser.

## First-class agent sessions

An agent session is distinct from a MAC agent registration, a task assignment and the
existing physical coding-session heartbeat. Store: session_id, source, agent_id,
hermes_instance_id when supplied by MAC, repo_id, mac_project, task_id, machine_id,
hostname, CLI, model, branch, pid, capabilities, status, started_at, last_seen_at,
ended_at, last_sequence and transcript availability. Sources are `tracker-cli`,
`mac-task-transcript` and `mac-agentbus`; never merge two sources without an explicit
shared session ID.

Import visible task work from authenticated `GET /tasks/{task_id}/transcript`, retaining
the upstream transcript ID, sequence, kind, actor attribution and timestamp. MAC
transcript turns carry their operator-visible body in `content`; import that string as
the conversation record text, while tolerating `text` as a compatibility alias.
AgentBus streams may be linked when their membership authorizes the configured tracker
principal;
read chunks through `GET /agentbus/streams/{stream_id}/chunks` with `agent_id`,
`after_sequence` and a bounded limit. Do not broaden AgentBus membership or copy a private
conversation merely because its task is visible. MAC agent `hermes_instance_id` is an
identity link only.

The running synchronizer must schedule transcript reads; a client class or table without
calls from the service lifecycle is incomplete. After each successful task snapshot,
request `/tasks/{encoded-task-id}/transcript` for every task with an owner agent or a
running/review state, with at most four reads in flight. HTTP 404 means transcript
unavailable and does not fail the snapshot. A successful response creates or updates the
deterministic session `mac-task-transcript:{task_id}`, source `mac-task-transcript`, linked
to the imported repository, MAC project, task, owner agent and that agent's machine and
`hermes_instance_id`. Upsert turns by their upstream transcript ID and sequence so repeat
polls add nothing. Preserve last-good turns and mark the session stale on a later failure.
Resolve the machine and Hermes links from the already imported agent inventory using the
task's `owner_agent_id`; a transcript response may be a bare turn array and need not
duplicate agent metadata. Looking only for an optional `agent` object inside the transcript
payload and leaving known inventory links null is incomplete.
Expose `agent_id` and `machine_id` on the session as their stable upstream fleet IDs (for
example the task's `owner_agent_id` and that agent record's `machine_id`), not tracker-local
database UUIDs. The fleet-scoped upstream IDs are the identities used by MAC API consumers
and remain stable across reimport; internal row keys must not leak into these response fields.

Do not expose or synthesize hidden model reasoning. A conversation contains only text
and tool/status records that the coding CLI, Hermes, MAC transcript or AgentBus source
explicitly made visible to the operator. Preserve `operator`, `agent`, `tool` and
`system` record kinds, source sequence and timestamps. Render untrusted content as text.

`GET /api/agent-sessions` is a bounded, filterable collection. `GET
/api/agent-sessions/{id}` returns identity, links, status and capability fields. `GET
/api/agent-sessions/{id}/conversation?after=SEQUENCE&limit=LIMIT` returns ordered visible
records and a next cursor. Repository and task detail responses include compact linked
session summaries. Local SSE emits named `project`, `task`, `agent-session`,
`conversation` and `steering` events whose payload shapes match these APIs.

Decode each dynamic URL path segment exactly once before identity lookup. In
particular, the deterministic `mac-task-transcript:{task_id}` session ID is emitted
by the collection and clients correctly percent-encode its colon when requesting
session detail, conversation or commands. Those encoded routes must resolve the
same stored session; comparing the literal `%3A` pathname segment to the database
ID and returning 404 is a service-readiness failure. Generated native acceptance
must list such an imported session and then fetch its conversation through the
percent-encoded collection-provided ID.

Import the same upstream transcript twice and prove that its records remain unique and
the fleet remains healthy. When SQLite implements transcript idempotency with a partial
unique index such as `(session_id, upstream_id) WHERE upstream_id IS NOT NULL`, the
upsert conflict target must include the matching predicate (or use an equivalent valid
strategy). A runtime `ON CONFLICT` mismatch that rolls the transcript transaction back
and degrades the fleet to `sync_failed` is a failed native test, even if the upstream
transcript request itself succeeded.

## Tracker-owned live CLI adapter

Implement `service agent-session --repo PATH --cli NAME [--task-id ID] [--model MODEL]
-- COMMAND...`. It registers the canonical repository, starts the command in a PTY with
inherited environment, and reports a new session plus heartbeat every 20 seconds. It
uploads bounded visible output records and polls for steering commands by sequence until
the child exits, then reports the actual exit status in `finally`. Backend outages must
not kill the child; reconnect resumes uploads and command reads from acknowledged
sequences. `TRACKER_URL` and `TRACKER_ACCESS_TOKEN` configure the adapter, and credentials
must never appear in argv, transcript, logs or browser data.

Dispatch this adapter from the two-token `service agent-session` mode after decoding
the complete JSON argument array. A top-level `agent-session` alias does not satisfy
the contract, and `service agent-session` must not fall through to the HTTP-service
listener or interpret `agent-session` as a host/port-independent server subcommand.

The reporter must handle SIGINT and SIGTERM as orderly shutdown requests: forward the
signal to the child, wait for its exit, stop heartbeat and command polling, flush bounded
visible output, and make one bounded final stopped report before the reporter exits.
Process termination must not bypass that cleanup merely because JavaScript `finally`
handlers do not run for an unhandled signal.

The child must observe a terminal on stdin, stdout and stderr; ordinary `pipe` stdio is
not a PTY and does not satisfy this adapter. Preserve terminal byte order when combining
stdout/stderr and operator input. The generated native test launches a child that exits
nonzero unless all three standard streams are TTYs, steers one line through it and checks
the echoed line in the stored conversation.

Allocate a fresh controlling PTY for the child even when the adapter itself is launched
by a noninteractive test runner with piped standard streams. Do not choose pipes or
inherited descriptors based on `process.stdin.isTTY` or `process.stdout.isTTY`. The native
probe must print `TTY:true` only when all three child streams are terminals and exit 23
otherwise; acceptance requires exit zero, the stored marker and the steered echo through
the real service read model.

Do not implement this by spawning macOS `/usr/bin/script` with Node `stdio: "pipe"` (or
three pipe descriptors). On macOS those descriptors are sockets, `script` exits before
the child with `tcgetattr/ioctl: Operation not supported on socket`, and an adapter can
misreport that wrapper exit as success while storing no output. The JavaScript
implementation must use the `/usr/bin/python3` standard-library PTY helper contract in
runtime.md. The helper owns the real PTY master and slave while Node retains separate
data and control pipes to the helper for reads, writes, resize and signals; those helper
pipes are not the child's standard streams. Falling back to child_process pipes is
incomplete. Native acceptance must assert the child actually started,
the wrapper/child exit code is propagated, and stderr contains no PTY setup failure.

The adapter advertises capabilities such as `observe`, `steer-text`, `resize`,
`interrupt` and `close`. A session without `steer-text` is read-only. A single visible
output record is at most 16 KiB after UTF-8 decoding and sanitization; split larger PTY
reads without changing byte order. Flush a nonempty partial record to the service within
one second even when it is smaller than 16 KiB and the child remains running; the size
limit is not permission to buffer a prompt until the child exits or fills the record.
Native acceptance must observe a short `TTY:true` marker through the service read model
before sending the input that lets the child continue. Retain at most 10 MiB or 10,000 conversation records
per session, whichever is reached first, and insert an explicit truncation record.
Bound control characters, ANSI escape sequences and strings before storage and render
terminal output in a sandboxed text surface.

Hermes may replace this adapter only when the configured runtime proves all of:
session-specific authenticated transcript reads, monotonic resume cursors, turn input to
that same running session, capability discovery and durable action attribution. The
currently verified MAC `hermes_instance_id` and conversation-to-task adapter do not prove
those properties, so they must not be presented as interactive steering.

## Authenticated and audited steering

`POST /api/agent-sessions/{id}/commands` accepts `idempotency_key`,
`expected_revision`, command `kind` and bounded `payload` fields. Compare the exact
`expected_revision` value with the current session revision; do not substitute a
request field named `revision`. `text` supplies one UTF-8 operator turn;
Conversation/output appends and routine heartbeats must not increment the session
revision: asynchronous visible output arriving after a client reads the session cannot
make an otherwise valid steering command conflict. Increment the revision only for
operator-relevant session-state or capability changes that truly invalidate the command
precondition.
`resize`, `interrupt` and `close` have explicit schemas. Reject unknown kinds, stale
revisions, ended sessions, unsupported capabilities and commands over 16 KiB. A command
is queued once, assigned a monotonic sequence and never reported as delivered until the
adapter acknowledges it. Display queued, delivered, rejected and expired states.

Every steering request requires the same authenticated browser/API boundary as task
mutation, same-origin protection and an operator identity. Persist an append-only audit
record with command ID, session ID, linked project/task, actor, kind, payload byte count,
payload digest, timestamps and outcome. Do not place command text in the audit summary;
the separately protected conversation record may contain the visible operator turn.
Redact case-insensitive secret-shaped keys and bearer-like values before persistence,
and never return configured credentials.

For MAC AgentBus debug terminals, use the existing `mac.agentbus.debug_terminal_open.v1`,
`mac.agentbus.debug_terminal_input.v1` and `mac.agentbus.debug_terminal_output.v1`
contracts with authorized stream membership, bounded TTL and their input/output stream
sequences. Treat this as a separate shell session unless it was explicitly opened for a
tracker agent-session adapter; a debug shell is not evidence that an agent conversation
can be steered.

## Live operator interface

Add **Live** to global navigation. Its default scope shows status (`live`, `polling`,
`resyncing`, `stale`), event rate, connected entities and last upstream event. Three
filterable lanes show projects, tasks and agent sessions on one shared time axis; selecting
an item freezes neither ingestion nor the other lanes. Filters cover project, task,
session, agent, machine, state and event kind. Pause stops visual motion while buffering
within the same replay bound; Resume catches up from the displayed cursor.

Session detail is a stable URL and shows identity/link fields, current status, visible
conversation, tool/status records, follow-tail toggle and connection state. New records
arrive without reload. Steering controls appear only for advertised capabilities, retain
an unsent draft across incoming events, show command delivery state and remain keyboard
operable. Never let incoming rendering replace a draft or steal focus. At 390px the lanes
stack, filters collapse behind a labelled control, conversation wraps or scrolls locally,
and the document has no horizontal overflow.

The global Fleet selector scopes Live without restarting ingestion. In All fleets, each
lane item, conversation identity and connection indicator shows its fleet badge, and the
summary reports health separately per fleet instead of collapsing partial failure into a
single Connected/Offline value. A selected fleet shows only its projects, tasks, agents,
machines, sessions and events; Local shows tracker-owned sessions. Preserve the selected
fleet in Live and session-detail URLs and browser Back/Forward. Steering a selected
session must route through its stored fleet identity, never the displayed selector value.

## Required generated acceptance scenarios

Generated native tests must launch the real service, a synthetic authenticated MAC hub
and a real disposable `service agent-session` child. They must verify:

1. An initial snapshot containing multiple projects, 10,000 tasks, agents and machines
   creates complete current projections while bounded APIs paginate; ordered stream
   events update all linked entities and reach an authenticated browser within two
   seconds.
2. Disconnect after sequence N, append events while offline, reconnect from N and prove
   each event commits once. Exercise a cursor gap, visible `resyncing`, atomic snapshot
   recovery, stale last-good outage state and the polling fallback.
3. Import attributed task transcript turns and an authorized AgentBus conversation while
   refusing a stream whose configured principal is not a member. No hidden reasoning or
   fixture secret appears in SQLite, API data, DOM, storage or logs.
4. Spawn a PTY adapter, observe its session and visible output, submit a text command,
   see the child receive it, observe ordered output and delivery acknowledgement, then
   interrupt/close and show the real exit state. Repeat an idempotency key and prove one
   input plus one audit record. Reject unauthenticated, stale-revision, oversized and
   unsupported commands without delivering bytes.
5. Open Live and session detail at 1440px and 390px, filter each entity lane, pause and
   resume from a cursor, retain an unsent steering draft while new records arrive, use
   every control by keyboard, and prove no page-level horizontal overflow or browser
   exception.
6. Connect two named fleets with overlapping project, task, agent, machine and sequence
   IDs. Switch between All fleets, each fleet and Local; verify badges, aggregate counts,
   stable deep links and Back/Forward. Take one fleet offline while the other emits events
   and prove its lane stays live while only the failed fleet becomes stale.

The native MAC fixture must record requests and require at least one authenticated
`/events/stream` connection plus an encoded transcript request for every eligible task.
It must query `GET /api/agent-sessions` and the session conversation to prove that the
upstream turn entered the actual service read model. Assert that the imported session
also exposes its MAC project, tracker repository/task, owner agent, and that agent's
machine and `hermes_instance_id`; creating a conversation with those links null is a
failure. The transcript fixture returns a bare array of turns while the owner agent's
machine and Hermes identity exist only in `/agents`, proving that synchronization joins
the imported inventory rather than depending on undocumented transcript metadata. Testing
an unused importer, schema or route in isolation is insufficient.

That same running fixture exposes `GET /projects/{encoded-project}`. Generated acceptance
must prove one service instance populates project detail, imports a task transcript,
connects to `/events/stream`, launches a child whose stdin, stdout and stderr are TTYs,
and carries a steered input round trip into visible conversation output. Passing these
behaviors in separate implementations, replacing the PTY with inherited or piped stdio,
or leaving any one of them dormant is a failure.
