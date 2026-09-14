---
name: MAC integration behavior
summary: Discovery, authority, synchronization and host association scenarios
kind: integration
---
# MAC integration behavior

## Resolve relationships after fleet-wide identity discovery

Within one snapshot transaction, discover every repository and establish stable task
identities for every project before projecting any task relationships. A per-project
seed-and-project loop is insufficient: when alpha references a beta task and beta sorts
later, the first poll misclassifies the reference as missing and the next identical poll
changes the projection. Build a fleet-wide upstream-ID lookup, with repository ownership,
then distinguish same-project dependencies, known outside-project references and truly
missing IDs. Keep known foreign Tracker IDs in unresolved details on the first poll.

The native unresolved_preservation gate must create alpha/x referencing alpha/pre,
beta/f-1 and missing, with alpha processed before beta and all records new. After the
first snapshot, pre is a normal Tracker-ID dependency, f-1 is outside_project with the
known beta Tracker ID, and missing is missing. An identical second snapshot must not
change any revision, raw reference, resolved/unresolved projection or task event count.
Repeat with reversed discovery and task order and after restart. Existing write/poll
stability and atomic rollback requirements remain mandatory.

## Admit full fleet response sizes

Use a 256 MiB aggregate response-body limit for production MAC HTTP transport.
The captured fleet has 9,717 records in an 80,765,554-byte JSON task response;
a 48 MiB limit rejected that valid response even though adapter-level snapshot
checks passed. Task count alone does not establish transport capacity. Keep byte
accounting bounded and destroy owned handles on overflow, while accepting valid
collections of at least80 MiB through the default production client. Do not drop
metadata, truncate collections, or shrink the fixture to pass the limit.

The native complete_reconciliation gate must also execute a separate authenticated
HTTP /tasks read with at least80 MiB of synthetic valid JSON under the production
client's default size limit and ordinary read deadline. Construct the data
programmatically with a measured margin: for example 10,000 short tasks each with
9,216 ASCII padding characters exceeds 80 * 1024 * 1024 bytes. Merely using 8,192
characters per task yields about 79.35 MiB with ordinary fields and fails the threshold.
Assert Buffer.byteLength of the fully serialized JSON is at least 83,886,080 bytes
before serving it, then assert the received serialized byte count and the complete decoded record count and
preserved padding. Exercise the actual client and adapter; do not inject a fake
transport or an enlarged test-only size limit. This focused transport fixture need
not insert its padding into SQLite: retain the separate ordinary10,000-task/201-project
snapshot, lifecycle, rollback and stability checks. Release large fixture data
and connections promptly so the entire native suite stays within its runner budget.

Independent final service acceptance replays the captured80,765,554-byte snapshot
through actual HTTP and verifies every project-scoped task and relationship in the
read store. Raw captures remain private; only aggregate sizes/counts are public.
The largest captured record is120,931 bytes (title719 characters, description up
to106,757 characters), so retain the existing720/110,000-character unchanged-text
mutation fixture and do not reduce the outbound body budget below that scenario.

## Own the transport until the response completes

Use Node's built-in HTTP/HTTPS request and response handles for production MAC
transport. A verified Node22 fetch candidate rejected at its default60-second
deadline but left the original HTTP1 socket open after65 seconds; catching a
locked ReadableStream.cancel rejection merely prevented a crash. Abort delivery
and body-stream cancellation do not prove resource release.

Retain the actual ClientRequest and IncomingMessage until completion. One absolute
wall-clock deadline must cover connection establishment, headers and the entire body.
On expiry, reject the caller and explicitly destroy both owned request and response
handles (and their connection) before releasing ownership. Observe error events on
both so destruction cannot cause an uncaught exception. Clear the deadline exactly
once on terminal success/failure, bound accumulated response bytes, and ensure late
callbacks cannot resolve twice or persist partial data. Disable authenticated redirects.
An inactivity timeout alone is insufficient: a trickling body must still meet the
absolute deadline. Preserve authenticated HTTP and HTTPS, JSON/non-JSON error handling,
60-second reads and the specified bounded writes. This transport change does not
alter any task, synchronization, protocol or browser semantics.

Both the short native timeout regression and independent actual default60 service
acceptance must use this same production transport against real loopback HTTP,
including healthy follow-up requests. Test seams must not replace the production
transport in these checks. Retain all prior regression scenarios below.

## Genuine relationship changes advance revisions and notify clients

Avoid duplicate post-edit events by comparing complete task projections, never
by suppressing revisions on changed relationships. A prior candidate imported
an upstream dependency-only change but kept revision1 and emitted zero durable
or live task events. Existing tasks must advance once when their fields or their
dependency/reference projection changes. Construct the complete desired task,
including resolved and unresolved references, before comparing and updating it.
Apply at most one revision increment and one task-change event per changed task
per successful snapshot. If an event includes a task object, that object must
reflect the final committed relationship projection.

Identity seeding for a newly discovered task may establish its initial revision
before relationships are resolved. That does not authorize keepRevision-style
suppression when an existing task's relationships change. Preserve the atomic
fleet transaction and publish only after the complete snapshot commits.

The native mac-selfcheck dependency_identity gate must exercise an upstream-only
change through the real authenticated HTTP fixture, synchronization and store:
start with existing alpha tasks a and p, with a having no dependencies. Change
only a's upstream dependencies to `[p]`, then synchronize. The new tracker-ID
relationship must be present, a's revision must advance by exactly one, and its
durable event rows and connected listeners must each contain exactly one committed
task change. Repeat the identical poll and require no further revision or event.
Then change a's title and remove the dependency in one upstream snapshot: require
exactly one revision/event again, and any emitted full task object must contain
the new title and empty relationship list. Inspect results for a, not merely
global event totals. Retain the mutation-response/unchanged-poll checks below.

## Enforce the response-body deadline

A read timeout must bound the entire client operation, including consuming a
successful response body. A confirmed Node 22 regression sends HTTP200 headers,
Content-Length100 and the single byte `[`, then never finishes the response.
With the ordinary 60-second read budget, the abort signal fires but awaiting the
body can remain pending indefinitely. Calling AbortController.abort alone does
not establish a deadline. The caller must reject by the configured deadline
(allow at most five seconds of scheduling margin), release owned response-body
resources, clear its timer, and permit later requests and synchronization attempts.
Enforce the deadline independently of whether fetch or its body promise settles.
Keep successful reads delayed beyond eight seconds valid within that budget.

Timeout cleanup must not crash the service. A response body may be locked by its
active reader; calling body.cancel() in a synchronous try/catch can still produce
an unhandled rejected promise. Own and settle all asynchronous cleanup operations,
including cancellation failures and losing deadline-race promises. Release the
original HTTP connection, not just the caller promise, and keep the service alive
for a healthy follow-up request. Do not suppress global unhandled rejections.

The packaged native test runner has a fixed 60-second total process budget. Its
mac-selfcheck serialized_reads gate therefore uses a short configurable read deadline
against the same authenticated incomplete-body fixture, asserts caller rejection,
connection closure before fixture cleanup, process survival and healthy follow-up.
Retain the successful 8500ms read and overlap tests; bound and close every fixture.
Keep the entire native suite and each diagnostic under the runner's budget.

Separately, delivery acceptance MUST execute the actual default 60-second read path
through the exported service against an authenticated disposable HTTP fixture:
HTTP200, Content-Length100, single byte `[`, then no body completion. Do not shorten
that independent check's deadline or substitute a fetch mock. Require caller failure
and original HTTP1 connection closure before65 seconds, cached tasks/revisions
preserved, truthful failed health, continued process survival, and healthy later
synchronization. A watchdog at70 seconds is only failed-test cleanup; it must never
supply a passing result. A native short-deadline pass alone does not prove this
separate default-budget acceptance. Neither test contacts the real fleet.

## Stable dependency projection after writes

Use the same relationship projection for full snapshot import and for importing
a MAC create/update/transition response. The ordinary `dependencies` selection
contains same-project tracker IDs. Preserve foreign and missing IDs in
`upstream_dependencies`; expose their explanation and any known foreign tracker
link in `unresolved_dependencies`. Do not alternate between including a foreign
task in the ordinary selection during polls and excluding it after a write.

After a successful full editor Save on an existing task with prerequisite,
missing and foreign references, capture its returned revision, dependency
selection and unresolved-reference detail. With upstream fields unchanged, the
next complete synchronization must preserve all three and publish zero additional
task changes. This also holds after adding a new prerequisite and after explicit
unresolved-reference removal. Exercise actual shared mutation and synchronization
services in the native dependency_identity check, inspecting store revisions and
committed event rows/listeners rather than only the outbound MAC body.

## Preserve the real MAC lifecycle

The supported MAC states are `open`, `waiting`, `blocked`, `claimed`, `running`,
`needs_review`, `needs_input`, `stopped`, `reviewing`, `completed`, `failed`, and
`cancelled`. Install all twelve for every discovered MAC project, even when its
snapshot is empty or contains only open tasks. These are upstream wire values.
The local Tracker defaults remain open/in_progress/blocked/review/completed;
in_progress and review are not native MAC lifecycle values. Do not impose the
local workflow on MAC projects or translate running to in_progress.

Before projecting any task in a successful snapshot, merge every additional
observed nonempty upstream state into its project's workflow inside the same
transaction. Pass the actual snapshot states through the synchronization path;
an unused helper accepting observedStates is insufficient. Preserve each task's
exact upstream state in storage and API detail. Never silently fall back to open
or the first workflow state when a state is missing. Keep IDs stable and retain
empty lists across unchanged polls, task moves, deletions, and process restart.

The native mac-selfcheck complete_reconciliation gate must verify these behaviors
through the authenticated fixture and actual synchronization/service/store. Give
synthetic tasks all twelve states plus `provider_extra`, discover an open-only
project and an empty project, and assert every imported state and all supported
empty columns. Change an existing task to a newly observed `provider_later` on a
later poll; verify its exact state, one revision change, stable workflow IDs, no
churn on the following unchanged poll, and preservation after restart. Check task
detail as well as rows, so a projector fallback cannot hide corruption. Retain
the existing scale, dependency, rollback and mutation scenarios.

## Newly selected dependency regression

For an existing MAC task whose raw dependencies are `[prerequisite, foreign]`,
select another same-project task that is not already an edge. PATCH
`dependencies: [trackerPrerequisiteId, trackerNewId]` must write MAC IDs
`[prerequisite, new, foreign]`. Build the translation map from all selectable
same-project tasks, not only the task's current upstream dependencies. Never
silently discard a newly selected valid tracker ID. Also verify adding the first
dependency to a task whose upstream array is empty, deselecting an existing
resolved edge, and retaining unresolved/foreign references on each edit. Inspect
the authenticated fixture's actual PUT body and the reimported task, not just the
pure merge helper. These checks belong in mac-selfcheck's dependency_identity gate.

## Observed repair failures that must be closed

An imported task can have dependencies `[prerequisite, missing, foreign]`, where
prerequisite is in the same project, missing has no mirrored task, and foreign is
in another project. A PATCH containing `dependencies: [trackerPrerequisiteId]`
is the editor's resolved selection, not permission to delete the other two edges.
Translate that selection to MAC IDs and retain existing unresolved/outside-project
MAC IDs. Omitting dependencies preserves every upstream edge. Add the optional
PATCH field `remove_upstream_dependencies`, an array of existing unresolved MAC
IDs explicitly selected for removal; validate it and remove only those references.
This removal works without an accompanying ordinary field edit. Task detail exposes
`upstream_dependencies` and `unresolved_dependencies` with `id`, `reason`, and an
optional `tracker_id`. The editor displays each unresolved reference and its reason,
offers a labelled removal control, and submits removals only after that control is
used. A full editor Save with no removal must preserve missing and foreign edges.
The normal same-project dependency selector remains named Dependencies. Preserve
unrelated metadata and references on title-only edits and full editor saves.

Imported MAC text may exceed the tracker limits for newly authored local text.
Do not reject a full editor Save merely because an unchanged imported title or
description exceeds those local limits. Preserve unchanged upstream fields byte
for byte and validate the fields actually changed. The editor must not silently
truncate prefilled values. In particular, editing labels on a task with a 720-character
title and a 110,000-character description must succeed and retain both strings.
Keep bounded request sizes and validation of genuinely new/changed input. This
distinction also applies to unchanged imported attributes with stricter local rules.

Snapshot commit is fleet-wide. Start from alpha/task-a titled Old alpha and
beta/task-b titled Old beta. The next snapshot changes both titles. Inject a storage
failure while applying beta, after alpha's update has executed. The failed sync must
leave both old titles and revisions intact, and emit/persist zero task-change events.
Per-repository transactions are insufficient: they leave New alpha committed when
beta fails. Cover repository discovery, workflow changes, task upserts, dependency
data, deletion and success timestamps in the same atomic snapshot boundary. Nested
store helpers must cooperate with that boundary. Queue notifications until commit;
emitting an event inside a transaction that later rolls back is incorrect. On failure
only the failed-attempt health/error status may change. Repeating the same snapshot
without the injected fault applies both changes once and publishes committed events.

Classify HTTP failure status independently of body format. A proxy may return an
HTML, plain-text, empty or malformed-JSON body with HTTP503. Those are all MAC
unavailability and become tracker503 for writes. Parsing a non-JSON503 body must
not replace the status with502/invalid-response. Keep useful bounded sanitized detail
when available, and keep malformed successful responses distinct from upstream503.
Test JSON, HTML, empty and malformed-JSON503 bodies through the actual authenticated
HTTP client and shared mutation service, retaining cached tasks and revisions.

The initial empty tracker database must discover fleet repositories without any
operator registration first. Fetch projects and registry, group their records by
logical MAC project, and upsert those groups before iterating local repositories.
For a project summary, use `project` as the task-routing project name; `project_id`
is its record identifier. For registry rows, use `project` as that same routing name.
Choose metadata.repository_url or the summary repository_url; source="git" is a
source kind. Do not require a remote host's registry path to exist locally.

One project summary and one registry record for the same project are corroborating
records, not two ambiguous matches. Deduplicate by logical project before deciding
whether a canonical repository identity has multiple conflicting project matches.
Use an explicit mac_project override only to resolve genuinely different projects.
Preserve known local paths; remote-only discovered repositories have checkout-needed
graphs until the operator supplies a real local checkout.

On successful complete project and registry reads:

1. Upsert discovered repositories with MAC authority.
2. Match local registrations against deduplicated canonical identities.
3. With no match, choose local authority and allow local task creation.
4. With a match and existing local tasks, preserve those tasks and mark migration
   required; do not silently reassign their authority or hide them.
5. Import all upstream tasks into the read model used by REST, MCP, A2A and the
   browser. A snapshot kept only in the adapter cannot satisfy this requirement.
6. Normalize metadata.project_tracker into visible tracker attributes, while
   retaining the entire original metadata for later merge-preserving writes.
7. Emit durable events for actual upstream changes, including state and deletion.
   Unchanged polling must not increment task revisions every five seconds.

Workflow state names and IDs must not collide during this import. If a newly
discovered MAC repo receives initial local-style states with generated IDs, an
upstream state named `open` must reuse or deliberately replace the existing `open`
state. Inserting a second state with the same repo/name violates the schema.
Prefer installing the MAC workflow when creating a MAC repository. Keep state IDs
valid across multiple repositories; a globally unique ID cannot be the same bare
`open` for every repo. Map workflow IDs to upstream names at the adapter boundary.
Verify with an empty database, one discovered repo and an existing upstream open
task, then with a second discovered repo also containing an open task. Both task
collections must load, complete sync must become available, and a subsequently
registered unmatched repo must become local. Readiness of the HTTP socket alone
does not establish that this import succeeded.

Example: projects contains a summary with project="alpha", project_id="p-1",
repository_url="https://example.test/team/alpha.git". Registry contains id="r-1",
project="alpha", source="git", and the same metadata.repository_url. Tasks contains
id="t-1", project="alpha", state="open", priority=1. Starting with an empty tracker
must produce one MAC repository and one visible MAC task. Registering
git@example.test:team/alpha.git refers to that repository; the two upstream records
do not create ambiguity. Registering https://example.test/team/beta.git after the
successful enumeration produces a local repository whose tasks never write to MAC.

During a failed enumeration, a new registration remains unresolved. Existing MAC
repositories retain their authority and last-good tasks; mutations return 503.
Failed reads never prove absence. Changing an existing MAC task while upstream is
unavailable must not update the local cache optimistically or create a shadow task.

For a MAC edit, load its current complete metadata, merge only changed tracker keys
under metadata.project_tracker, and PUT supported MAC fields. Use the separate
transition endpoint for state changes. Keep integer priority (default 1). Preserve
upstream ID, owner_agent_id, foreign metadata and lifecycle rejection details.
If a field update succeeds and the transition fails, refresh actual upstream state
and return a useful rejection; never mark the transition as completed in the cache.

Host reporters resolve or register their canonical repository with the backend,
then include its repo_id in every heartbeat. Heartbeats include the spawned child's
PID, actual physical hostname and checked-out branch, and finish with stopped state.
A record with a host and PID but no repository association does not fulfill the
repo-centric session view.


Translate unavailable upstream responses consistently: HTTP 500, 502, 503, 504,
connection failure and timeout during a MAC task mutation return tracker HTTP 503
with a useful unavailable error. Do not map every non-404 upstream response to
502/mac_rejected. Preserve genuine upstream 4xx lifecycle rejection details and a
non-success client response separately. Test an existing discovered MAC task edit
when the upstream deliberately returns HTTP 503: tracker must return 503, retain
the cached task unchanged, and create no local task. Test a successful waiting
transition and a rejected completed transition independently of this outage case.


Install the full supported MAC lifecycle, including states with no tasks currently
occupying them. Do not replace the workflow with distinct states from the imported
task snapshot. In particular, discovering a project with only open tasks must still
advertise waiting and completed so the operator can request those transitions.
Use the authoritative lifecycle definitions (or the known supported lifecycle when
no discovery endpoint exists), merging additional observed states. Keep the workflow
stable as lists become empty. Let MAC enforce whether a transition is allowed.
Test an open-only upstream project: waiting succeeds through the actual transition
endpoint, while a completed request reaches that endpoint and returns its deliberate
lifecycle rejection. Rejecting both locally as unknown_state is incomplete integration.


A genuine upstream 4xx lifecycle rejection returns a tracker 4xx response (preserve
the upstream status where possible), with its useful rejection detail. HTTP 502
is not the response for a valid upstream lifecycle denial. Keep that denial distinct
from 503 unavailability and preserve the cached task's actual state. Test a rejected
completed transition, including both HTTP status and unchanged local/upstream state.


## Live fleet synchronization status

When a configured fleet changes from reachable to unavailable, persist sync_error
on matched repositories and publish the repository status change through the same
SSE refresh path used by the browser. An already-open overview and inspector show
that failure without reload within one polling interval plus transport delay.
Cached tasks and counts remain visible, and attempted mutations remain upstream
operations that fail during the outage; no local shadow task is created.

When the fleet recovers, clear the error and publish that change even if every
upstream task is identical to its pre-outage contents. A healthy-to-failed or
failed-to-healthy status transition is observable repository data. Avoid duplicate
events on repeated polls with unchanged failure state. Verify healthy -> HTTP503
-> healthy using the isolated fleet fixture, without browser reload or task edits.

Detect the status transition across the complete synchronization operation. Read
and retain each repository's previous sync_error before discovery, repository
upsert, task import or reconciliation can change it; compare that original value
with the final persisted status. Publish the actual change after persistence. A
repository upsert that clears sync_error must not erase the information needed to
publish recovery. Repeated healthy polls with identical tasks emit no duplicate
recovery updates. Test recovery of an existing discovered repository, not just a
helper that clears an untouched error field.

Normalize MAC transport and rejection errors in the shared task service before
REST, MCP or A2A adapters handle them. This includes new-task creation as well as
field edits and lifecycle transitions. A MAC client exception carrying upstream
unavailability must become the same service unavailable error on every path;
it must not fall through a generic HTTP500/internal-error handler. With a matched
repository and upstream503, POST a new task: return tracker503, insert no cache
or local task, and preserve existing task revisions. Retain useful genuine4xx
rejection details separately. Exercise creation, editing and transitions through
the real shared service with an HTTP fleet fixture.

## Complete fleet snapshots and dependency identity

MAC dependency values are upstream task IDs; tracker task IDs belong to a separate
namespace. Import is independent of task order and project order. Establish every
discovered repository and task identity before resolving dependency relationships,
or use an equivalent stable mapping that supports forward references. A dependent
task arriving before its prerequisite must import successfully. Translate resolved
dependencies to tracker IDs for public task APIs and the editor, and translate
tracker IDs back to MAC IDs on explicit upstream creates/edits. Never send tracker
UUIDs to MAC as dependency IDs. Preserve unchanged dependencies on unrelated edits.

MAC is authoritative for its existing dependency graph. References to another MAC
project, missing/archived tasks and upstream cycles must not abort discovery, erase
relationships or prevent unrelated tasks from importing. Preserve the complete raw
upstream dependency list in durable upstream data. Expose unresolved references with
their upstream IDs and a useful missing/outside-project explanation in task detail;
resolved cross-project references may link to the corresponding tracker task. Do not
force the stricter local-task repository/cycle validation onto an imported upstream
snapshot. Local task mutations retain those validations. An unrelated MAC edit must
not clear missing or cross-project references. Explicit dependency edits translate
selected local IDs and retain unresolved references unless the operator explicitly
removes them. Recheck references on later snapshots so missing tasks can resolve.

Reconcile the full snapshot, not just the first API page. Public page limits must
not cap internal import, deletion, identity resolution, dependency validation or
failure-status propagation. Verify more than 200 tasks per repository and more than
200 repositories with changes/removals beyond the first page. Use complete keyed
lookups and transactions or equivalent bounded work; avoid rescanning the entire
fleet per imported task. A fleet of at least 10,000 tasks must remain practical.
An unchanged complete poll emits no task changes and keeps revisions stable.

Serialize synchronization: at most one poll may be in flight, even when a poll
takes longer than its interval or a manual refresh overlaps the timer. All exits,
including import errors after successful HTTP reads, update last_sync_at and
last_sync_ok and expose a sanitized actionable sync_error. Never silently swallow
an import exception and leave health indeterminate. Preserve last-good snapshots
on failure and do not publish partial import success. Recovery clears errors and
emits the required status transition after the entire snapshot is reconciled.

Enumeration reads must tolerate the real fleet's response time while remaining
bounded. Use a 60-second timeout for read requests through response-body consumption;
keep mutations bounded separately and never automatically retry a write. Avoid
serial project-detail calls when summaries plus the known lifecycle suffice; any
optional detail enrichment uses bounded concurrency and cannot block all task import.
The HTTP service must remain available during synchronization, with readiness clearly
distinguished from socket liveness. Native acceptance uses disposable fixtures only;
separate operator-authorized live verification uses an isolated tracker database and
read-only MAC requests, never automatic fleet writes.
