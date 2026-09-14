---
name: Product verification and completeness
summary: Required behavior coverage and complete user-facing integration
kind: verification
---
# Product verification and completeness

## Confirmed regeneration regressions

Async UI renders must not commit an obsolete route after navigation or a completed
mutation. Recheck the active route/render generation after awaited reads, and never
reopen a modal from an outdated registration route. With an SSE connection active,
register a remote-only local repository using the browser form: require exactly one
new repository, navigation to its board, and a closed registration dialog that stays
closed after the repository-created event and subsequent refresh. Preserve the user's
current modal draft during unrelated SSE refreshes. Verify cancellation does not imply
that an already completed registration was undone. The prior candidate persisted and
navigated correctly but a stale render reopened an empty registration form.

Informational toast notifications must not intercept pointer input intended for the
workspace. A status-only toast has no interactive hit target; retain accessible live
announcements while allowing underlying controls to receive normal clicks. At
mobile390x844, save a repository description and immediately navigate to Settings,
edit URL/model/key and click Save settings while the success notification is visible.
The save must complete without forced clicks or waiting for notification expiry.
If a notification contains an explicit action, restrict hit testing to that action
and keep primary controls reachable. Preserve the verified mobile drawer behavior.


Fleet identity indexing must use exactly the same composite key for insertion and
retrieval, including identical delimiters and encoding. Candidate14 introduced a
NUL-versus-space key mismatch during a late scale optimization: all seeded tasks
were skipped during projection. Do not silently skip an established task identity.
Keep first import, dependency-only and combined changes, unchanged polling and
large-response assertions in the complete native run after every optimization.
Use one key constructor or nested maps if indexing composite identities.

Invalid local task dependencies (self-reference, unknown ID, cross-repository ID
or a cycle) are client input errors. Through actual HTTP create/update endpoints,
return 400, 409 or 422 with a useful validation message, never generic HTTP500.
Reject atomically: retain all existing task fields, revisions and durable/live
change events, and create no task on an invalid create. Native service acceptance
must exercise these HTTP contracts as well as direct validation. Preserve imported
MAC dependency semantics; upstream cycles remain readable upstream data.

At mobile390x844, an open navigation drawer must retain a visible, clickable close
control. Menu toggling, Escape and backdrop dismissal must work and aria-expanded
must reflect actual visibility. Selecting a navigation destination closes the
drawer and leaves Activity content and the Settings control usable without pointer
interception. Test open -> Activity -> Settings, reopen -> Escape, and reopen ->
close control using normal pointer/keyboard actions, without forced clicks or DOM
mutation. Keep all existing desktop/mobile task and workflow interactions.


A successful complete fleet snapshot must reconcile disappeared task IDs across all
cached MAC repositories, including repositories no longer in current project discovery.
Use the complete upstream task-ID set, preserve local tasks and repository metadata,
and retain cache on any incomplete/failed read. Execute the removed-project and
successful-empty-snapshot cases in mac-integration.md. Do not reset the database between
lifecycle and scale phases to hide stale tasks left by incomplete reconciliation.

The native rollback fixture must retain its initial import events and compare against
the captured pre-failure task-event count/cursor. Zero new task events is required;
zero total historical events is incorrect. Verify recovery adds exactly two task events
for the two changed projects, without weakening the row/revision rollback assertions.

Native MAC checks must establish fleet-wide identities before dependency projection,
including the alpha-to-later-beta unresolved reference fixture in mac-integration.md.
The measured large-response fixture must exceed 83,886,080 bytes; construct sufficient
padding rather than accepting an undersized fixture or lowering the assertion.

Renaming a populated local workflow state must preserve its stable state ID and every
occupying task's board membership. If tasks persist state names, atomically update those
names along with the workflow row; if tasks persist state IDs, keep those IDs unchanged
and expose the renamed display label consistently. A task may never reference a removed
state name after a successful rename. Preserve unrelated fields/dependencies, advance
changed task revisions once and emit committed events with the final projection.
Native and browser checks must create a task in open, rename open to Ready, verify the
same state ID, fetch the task, and confirm it appears in Ready after reload and restart.
Retain task moves, workflow ordering, populated deletion migration and MAC lifecycle
ownership. Checking only the renamed heading is insufficient.

The MAC complete_reconciliation gate must execute the >=80MiB real authenticated
HTTP collection-read scenario in mac-integration.md using the production256MiB
response limit. A previous candidate passed adapter-level import of all captured
tasks but its48MiB transport cap rejected the actual80,765,554-byte JSON response.
Keep byte-volume coverage distinct from task-count coverage; retain all ordinary
store/snapshot scenarios and the separate final exported-service captured replay.

Production MAC requests retain Node HTTP/HTTPS request and response ownership through
body completion; absolute-deadline failure destroys both handles. Execute the real
transport in short native and independent default60-second acceptance. A prior
fetch candidate avoided its cancellation crash but left the socket open after65
seconds. Catching stream.cancel rejection is not sufficient cleanup evidence.

The native dependency_identity gate must distinguish unchanged polling from
genuine dependency-only upstream changes. Execute the concrete a/p fixture in
mac-integration.md: dependency-only and combined title/dependency changes each
advance one revision and publish one committed task event, while the following
identical poll does neither. Do not use revision suppression on existing tasks
to make a no-churn assertion pass. Any emitted full task payload must match the
final committed projection. Retain atomic rollback and post-edit stability.

Execute the stalled HTTP200 body scenario from mac-integration.md in two scopes:
the native serialized_reads check uses a short configurable deadline so the full
suite fits the installed runner's 60-second process limit; independent delivery
acceptance uses the actual exported service's default 60-second deadline. Both
must observe caller failure, original connection cleanup before fixture cleanup,
process survival and healthy follow-up. The independent default-budget check must
also preserve cached task revisions and show failed then recovered synchronization.
Never equate a short test, an abort signal, or a watchdog-closed socket with the
full default-budget result. Handle rejected cancellation/cleanup promises locally;
a locked response stream must not cause an unhandled rejection or process crash.

The native stalled-body fixture records the exact request socket serving its
incomplete `/tasks` response and observes that socket's close event before any
fixture cleanup. HTTP keep-alive may reuse a socket accepted during an earlier
healthy poll: do not restrict the assertion to connections accepted after the
stall began. Exercise that reused-connection case deliberately, require caller
rejection by the short deadline and closure of the recorded stalled socket, then
verify unchanged cached revisions and a healthy follow-up. An unrelated closed
socket, an empty slice of newly accepted connections, or fixture shutdown is not
evidence about the stalled response. Retain all other native and independent
default-deadline assertions.

The native dependency_identity check also verifies that an editor mutation and
the next unchanged snapshot expose identical dependency/reference projections,
stable revisions and no duplicate task events. Keep foreign tracker links in
unresolved-reference detail consistently, as specified in mac-integration.md.

The native MAC complete_reconciliation check must preserve all twelve native MAC
states and additional observed states through import, update, task detail and
restart, including empty workflow columns and stable unchanged polls. Execute the
concrete lifecycle scenarios in mac-integration.md. An all-open scale fixture
cannot establish lifecycle preservation: an earlier candidate imported all tasks
but incorrectly mapped most states to open. The successful MAC transition fixture
uses open -> waiting, a native MAC transition; keep local in_progress tests local.

The native MAC dependency_identity check must add a newly selected prerequisite
to an existing task, including the first edge on an empty dependency array.
An identity map containing only existing edges silently drops these selections.
Use the concrete scenarios in mac-integration.md through the real authenticated
HTTP client and shared mutation service, checking actual writes and reimport.

Git Graph and Timeline filtering must work when a checkout has both a branch
named `feature` and a file named `feature` (likewise `main`). A bare
`git rev-list feature` is ambiguous in that checkout. Resolve the selected branch
to a qualified ref or commit and terminate revision arguments with `--` where
required. A Git command failure must not masquerade as successful empty history.
The native `["git-selfcheck"]` must create this branch/filename collision and
verify the service's filtered graph contains exactly the reachable commits.
Fold this assertion into its refs check or an equivalent executed native case.
Retain the equal-time and irregular-time browser fixtures, selection, branch
task/session associations, zoom, keyboard navigation and task editing.

## Native MAC regression gate

The native test suite must execute the MAC integration scenarios below, not merely
pure identity, metadata-merge or error-classification vectors. A candidate with only
those vectors can report all tests passing while dropping missing dependencies,
committing a partial fleet snapshot and turning an HTML503 into tracker502.

Provide the maintenance diagnostic JSON invocation `["mac-selfcheck"]`. It starts
disposable authenticated loopback MAC fixtures and isolated tracker storage, invokes
the real synchronization, HTTP client and mutation service, and cleans up all servers,
processes and files. It never consumes the operator's fleet URL, credentials or data.
Register this invocation as a native manifest case and run it from --litai-test.
Its deterministic result is `{"ok":true,"checks":{"dependency_identity":true,
"unresolved_preservation":true,"explicit_removal":true,"snapshot_rollback":true,
"commit_events":true,"non_json_outage":true,"complete_reconciliation":true,
"serialized_reads":true,"restart_persistence":true}}` only when those assertions
actually pass. Compute each check from observed service/store/HTTP results; a constant
success object, mocked success helper or standalone unused regression file is invalid.
Any failed assertion makes the native test fail. Retain the existing native coverage.

Use the concrete alpha/beta failure and prerequisite/missing/foreign edit scenarios
in mac-integration.md. Verify full dependency selection preserves both unresolved
references, then explicitly remove just missing and verify foreign remains. Observe
both durable event rows and connected service listeners during an injected failure
after alpha changed but before beta commits; zero task events may escape rollback.
Recover and require exactly one committed change per changed task. Exercise JSON,
HTML, empty and malformed JSON HTTP503 bodies. Complete-reconciliation coverage must
include 10,000 tasks, 201 projects, updates and deletions beyond item200, stable repeat
polls and late dependency resolution. Serialized-read coverage overlaps manual/timer
polls, delays a response beyond eight seconds and verifies a bounded body-read timeout.
Restart the store and verify relationships survive. Keep native fixtures synthetic.

Dependency-preservation assertions observe the actual upstream task after the write,
the returned Tracker task, and a subsequent complete synchronization. A full editor
save may omit unchanged fields from its outgoing update: absence of `dependencies`
in that request is valid when the upstream edges remain intact. Do not require an
unchanged field to be retransmitted merely to satisfy a fixture-body assertion.
For the explicit_removal gate, first save labels with the original resolved selection
and require prerequisite, missing and foreign references to survive upstream and in
the Tracker projection. Then remove only missing and require prerequisite and foreign
to remain. Also select a genuinely new same-project prerequisite, inspect its translated
MAC ID in the actual outgoing write, and require stable projections and revisions on
the following unchanged polls. If an update does send dependencies, verify the sent
IDs and preserved unresolved references as well. No assertion may be replaced by a
constant, a mocked success, or a synthesized fixture request field.

The unresolved_preservation check also covers one synthetic imported task with a
720-character title and 110,000-character description. Submit the full editor payload
with only labels changed: it must succeed and preserve both text fields byte for byte.
Do not use large text for all 10,000 scale-fixture tasks. Verify the same unchanged-text
save in the browser alongside unresolved-reference display and explicit removal.

## Fleet dependency and scale regression acceptance

Use authenticated disposable MAC HTTP fixtures through the actual service. Return
dependent tasks before their prerequisites, put those prerequisites beyond item200,
include another project's dependency, a missing reference and an upstream cycle.
Require complete import, correct tracker-ID links, durable raw upstream references,
visible unresolved-reference detail, last_sync_ok true, and an unchanged second
poll with no revision/event churn. Restore the missing task in a later poll and
verify the relationship resolves. Restart and verify dependency persistence.

Capture upstream create/edit bodies: each selected tracker dependency becomes the
corresponding MAC ID. A title-only edit and the browser's full editor Save preserve
missing/cross-project references and foreign metadata. Explicit removal of an
unresolved reference must work through a labelled control. Keep local dependency
cycle and cross-repository rejection tests. Imported upstream cycles are read data,
not an excuse to bypass local mutation validation.

Import at least 10,000 tasks and at least201 projects. Change and delete tasks beyond
the first200, verify exact totals and unchanged revisions elsewhere, and verify all
repositories show outage/recovery. Inject an import failure after enumeration and
assert rollback to the last-good snapshot, truthful failed health and recovery.
Overlap explicit synchronize calls with a slow fixture and assert one in-flight
poll; verify reads delayed beyond eight seconds can succeed and response-body stalls
remain bounded. No native test may contact the real fleet. Bind separate read-only
live evidence to the exported source identity and compare all snapshot IDs/counts,
not only a healthy HTTP socket or the first page of repositories.

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


## Final concrete board regressions

A horizontally scrollable board must contain absolutely positioned accessibility
labels as well as visible cards. A visually-hidden move label with an initial
static position outside the viewport can use the page as its containing block and
increase document.scrollWidth even when its visible card is inside an overflow
auto scroller. Give each card action container an appropriate positioned containing
block (for example position:relative on .card-actions), or use an equivalent
containment that retains accessible names. Verify every task and list remains
reachable through board scrolling. Reproduce with five columns and at least two
cards per column: at 1440 and 390 pixels the document stays at viewport width,
including after scrolling to the rightmost list. Merely adding min-width:0 and
hiding body overflow does not fix this absolute-label escape.

The browser must expose actual workflow reordering controls. A List menu containing
only rename/delete and an Add list button is incomplete, even when the backend
reorder API works. Provide visible, labelled Move list left/right or equivalent
keyboard-operable controls. Add a list at the end, move it one position earlier,
then reload: the order must persist and card assignments remain unchanged. Keep
rename/add/delete with populated-state task migration working. The controls must
be usable at desktop and 390px, not only via an undocumented API or internal IDs.


Contain every absolutely positioned accessibility label, including the list header's
new Move list left/right controls. Positioning only task card actions is insufficient:
list buttons also scroll outside the viewport. Give each control a positioned
containing block, use aria-label instead of an offscreen text node, or provide an
equivalent accessible implementation. In the observed regression the hidden label
inside a static .mini-button escapes .board-lists even though .card-actions is fixed;
document widths become 1657 at 1440 and 1167 at 390. Test after adding and moving a
list as well as with the initially seeded five columns. Keep controls reachable by
board scrolling; do not mask escaped content with document overflow clipping.
Each checklist text input must also have a programmatic accessible name, including
items added dynamically, so keyboard and assistive-technology users can edit them.


Verify real Git refs as well as commit parents. Create main and feature branches in
a temporary repository, then assert graph.refs includes both names and their actual
rev-parse hashes, and the browser branch filter can select feature. Git for-each-ref
format escapes use %1f for a unit separator; git log pretty-format uses %x1f. Using
%x1f with for-each-ref prints a literal token and silently empties parsed refs when
splitting on the unit-separator byte. Use the correct command-specific format (or
another correctly parsed format), and retain refs/heads, remotes and tags. Empty
refs on a nonempty branched repository is a failure, not an acceptable fallback.


The Fleet/Physical host sessions table must visibly include the actual spawned child
PID, alongside hostname, CLI, branch, task, last heartbeat and derived status. Storing
pid in SQLite and GET /api/sessions is necessary but insufficient: the operator must
be able to identify the process from the rendered row. Verify a real reporter child,
find its exact PID in the Fleet row, then stop it and observe stopped without reload.

A timeline layout node need not have the graph layout's lane property. Its commit
inspector must never print "Lane undefined". Either resolve the real graph lane for
that commit, or omit an inapplicable lane field. Verify selected and branch-filtered
commit details in both Graph and Timeline views; retain real timestamp spacing.


## Effective settings regression

With gateway URL, model and key supplied only through TRACKER_LLM_* environment
variables, a real assistant request succeeds against a disposable gateway and
Settings GET reports the effective URL/model and llm_key_configured true without
returning the key. Project the same effective configuration used by the request,
not only persisted database settings. Blank secret edits retain the effective
credential; an explicit clear must suppress the environment fallback until the
operator configures a replacement. Test these behaviors through HTTP.


## Actual empty Git history regression

The generated native tests must create a disposable `git init -b main` repository
without committing, register/read it through the actual Git reader or service, and
assert explicit unborn/empty state, no commits and a no-commits message. This test
must exercise actual Git, not a mocked nonzero `git log` result. Verify the successful
empty-output path of `git log --all --topo-order`; zero exit status alone does not
mean history exists. Do not mark an unborn branch as detached. Retain nonempty and
true detached-HEAD fixtures so the empty fix does not suppress valid history.


## Integration wiring regressions

Exercise the actual service entrypoint with raw process environment names
TRACKER_MAC_URL, TRACKER_MAC_TOKEN, TRACKER_LLM_URL, TRACKER_LLM_MODEL and
TRACKER_LLM_KEY. A settings projection helper accepting normalized lowercase keys
must receive the normalized environment, not raw process.env. Secret consumers
and configured booleans must use the same effective values. Test real HTTP
requests after starting only with these environment variables: discover a MAC
fixture project and call a mock LLM gateway. A pure helper test with hand-normalized
keys does not cover the wiring. Keep database settings and explicit-clear tests.

Workflow ordering remains a strict, contiguous sequence after deleting a list.
After creating a final list, moving it left once and deleting it with migration,
repeat that sequence in the same repository. Each newly added list appears last
and moves exactly one position left. Do not insert at states.length while leaving
old position gaps: that can duplicate a remaining position. Persist unique ordering
and retain it across reloads; test at least two complete add/reorder/delete cycles.


## Branch-to-physical-host integration

Start an actual disposable session reporter child on main in a fork/merge fixture.
Confirm its physical hostname in the stored session, graph response association and
Fleet row. Open Graph with no branch filter, select main's tip and assert the exact
hostname is visibly rendered. Repeat in Timeline and verify feature filtering
excludes a main-only host. Stop the child and observe stopped status. A graph
projection containing only session_id, branch, cli and status fails this contract;
the actual hostname must survive that projection and reach the branch view.


Exercise the raw framework service invocation with all trailing options:
`node main.js --litai-serve --host 127.0.0.1 --port PORT`. Select a fresh nondefault
port and require /health there, with no silent fallback to port8765. Preserve the
complete raw argv for framework modes as well as decoding complete JSON arrays
for service, MCP and reporter commands. Include this startup regression in native
tests while retaining the supported JSON service path.

Browser review includes the entire short list names at desktop1440/mobile390,
without truncation by action buttons. It also observes a MAC fleet outage and
recovery in an already-open overview/inspector without reload, with unchanged
upstream tasks. Status changes must reach the view and cached tasks stay visible.

The MAC status regression must run the complete service synchronization path with
an HTTP fixture and an existing discovered repository: healthy, fleet503, then
healthy with byte-equivalent upstream tasks. Capture emitted repository events and
persisted repository data after each step. Require one failure update and one
recovery update, and none for repeated unchanged polls. In the browser keep the
overview and inspector open before the outage, observe both transitions without
reload, and confirm cached tasks/revisions remain unchanged. A direct test of an
error-clearing helper alone does not cover discovery/upsert ordering.

In the same HTTP fixture exercise new-task creation during upstream503, in
addition to existing-task edits and transitions. Require tracker503 and no cache
insertion from REST, and the equivalent unavailable result from MCP and A2A.
Typed client errors must cross the shared-service boundary as recognized service
errors. Do not count a generic internal500 as an actionable fleet outage.

Browser acceptance for related tasks must activate a task link from a selected
feature commit in both Graph and Timeline at desktop and mobile widths, then
assert the opened task editor's Title control contains that task's exact title.
Showing the title as plain text in a branch-association summary is insufficient.
Retain the graph's parent-edge, timestamp-spacing, zoom, selection and physical
host assertions while adding this navigation check.

Locate the dependency multiple-select by role listbox and accessible name
Dependencies (or an equivalent visible label) before selecting the prerequisite
task. A nearby span referenced only through aria-describedby does not satisfy
this accessible-name requirement. Save and reopen the task to verify the selected
dependency persists together with its other editable attributes.

Test protected browser access at desktop1440/mobile390 using an isolated backend
with TRACKER_ACCESS_TOKEN and a fresh browser context. Without a cookie, require
the accessible password input and Sign in control, with no repository data or
authenticated event stream. An invalid token keeps the form visible and shows an
error. Entering the valid token through the visible form opens the overview and
establishes the live event connection. Verify the cookie is HttpOnly and SameSite,
reload retains the session, and clearing the session cookie followed by reload
returns to the usable login form. No token may appear in the URL, localStorage,
sessionStorage or rendered page text. A direct API login request or manually
injecting a browser cookie does not prove this browser interaction contract.


At mobile390x844, measure the chart scroller after selecting Feature and switching
Graph/Timeline with the inspector retained. Its client height must be at least
180px and real circle clicks must succeed. Repeat for equal and irregular commit
timestamps, after applying/clearing the branch filter and after Zoom/Reset. The
inspector remains reachable through normal vertical scrolling without shrinking
or overlaying the chart. Record both viewport and SVG geometry on failures.
