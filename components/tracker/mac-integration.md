---
name: MAC integration behavior
summary: Discovery, authority, synchronization and host association scenarios
kind: integration
---
# MAC integration behavior

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
