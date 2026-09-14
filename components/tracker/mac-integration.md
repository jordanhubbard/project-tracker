---
name: MAC integration behavior
summary: Discovery, authority, synchronization and host association scenarios
kind: integration
---
# MAC integration behavior

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
the cached task unchanged, and create no local task. Test a successful in_progress
transition and a rejected completed transition independently of this outage case.


Install the full supported MAC lifecycle, including states with no tasks currently
occupying them. Do not replace the workflow with distinct states from the imported
task snapshot. In particular, discovering a project with only open tasks must still
advertise in_progress and completed so the operator can request those transitions.
Use the authoritative lifecycle definitions (or the known supported lifecycle when
no discovery endpoint exists), merging additional observed states. Keep the workflow
stable as lists become empty. Let MAC enforce whether a transition is allowed.
Test an open-only upstream project: in_progress succeeds through the actual transition
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
