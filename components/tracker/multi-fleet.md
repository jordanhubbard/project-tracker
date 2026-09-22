---
name: Multi-fleet monitoring and selection
summary: Named MAC fleet configuration, namespaced identity, isolated health and global UI scope
kind: integration
---
# Multi-fleet monitoring and selection

## Configuration and safe fleet projection

`TRACKER_MAC_FLEETS_FILE` points to a mode-0600 JSON file containing an array of
`{id,name,url,token}` records. `id` is a stable URL-safe operator-chosen identifier;
display names need not be unique. Preserve `TRACKER_MAC_URL` and `TRACKER_MAC_TOKEN` as
the legacy single fleet with stable ID `default` only when no fleets file or saved fleet
records exist. Reject duplicate IDs, embedded URL credentials and an ambiguous mix of
legacy and multi-fleet configuration.

Before reading the file, inspect the actual file mode and require no group or other
permission bits (`mode & 077 === 0`); a merely documented mode or private parent
directory is insufficient. Reject a symlink or non-regular file and return a sanitized
configuration error that does not include file contents or tokens. Either refuse startup
with that diagnostic or, if the service remains available, expose the diagnostic through
the safe fleet/settings projection; silently starting with an empty fleet list is invalid.

Settings manages named rows with URL and write-only token input. Adding, renaming or
removing a fleet is explicit; removal requires confirmation, never exposes its token,
and retains cached records as stale until the operator separately confirms data deletion.
Stored and file tokens remain backend-only. `GET /api/fleets` returns safe ID, display
name, configured state, sync state, last success, bounded error and entity counts, never
tokens or URLs containing credentials. It also returns a safe `source` discriminator of
`file`, `environment` or `settings` so the UI can explain which rows are editable.

Provide authenticated `POST /api/fleets`, `PATCH /api/fleets/{id}` and
`DELETE /api/fleets/{id}` management. Create accepts stable ID, name, URL and token;
patch may rename, replace URL, replace a nonblank token or explicitly clear it but never
returns the stored token; stable ID cannot change. Delete unconfigures after explicit
confirmation and retains cached data. Validate duplicates and URLs before persistence,
apply each mutation atomically, and immediately refresh the synchronizer's configured
clients without service restart. Prove retention by reading the cached fleet-scoped data;
do not invent a mandatory `retained_cache` or `cached_data_retained` response field that
is not otherwise part of the API contract. A Settings display that only lists environment/file
fleets or tells the operator to edit a file does not satisfy fleet management.
When the service started with zero fleets, adding the first Settings fleet must also
perform initial discovery and start periodic synchronization; merely reloading a client
map while leaving the synchronizer stopped is not immediate refresh. PATCH performs a
refresh with the replacement URL/token, and DELETE stops requests for that fleet.

Fleet ownership is explicit. File and legacy-environment rows are read-only in the UI:
show their source and do not render Rename, Replace token or Remove controls that will
fail. `PATCH` or `DELETE` for those rows returns a useful conflict directing the operator
to its source. `POST` rejects an ID already present in any configured source, including a
file, environment or configured Settings record; it never silently shadows or replaces
that row. A `POST` using the same ID as a retained, unconfigured Settings record is the
explicit reactivation path: update that record with the supplied name, URL and token,
resume its existing namespace and return 201. Fleets created through Settings support the
complete
rename, URL update, token rotation/clear and confirmed removal flow above. File records
and Settings records with different stable IDs may coexist.

## Identity and synchronization isolation

Every MAC-owned repository, task, agent, machine, transcript, assignment, event and
derived session carries `fleet_id`. Internal and public identity uses
`(fleet_id, upstream_id)`; a bare upstream ID is never globally unique. Persist fleet
identity across polling and restart, include it in REST, SSE, MCP and A2A projections,
and qualify links and writes with the owning fleet. Relationships resolve only inside
the owning fleet unless a future explicit cross-fleet contract exists.
Repository matching is fleet-scoped too. A canonical Git remote may help match a local
registration to one MAC project, but it must never cause a MAC-owned repository from one
fleet to be reused or reassigned by another fleet. Lookups for an existing MAC repository
must include `fleet_id`; North and South reporting the same project name and identical
canonical remote produce two repository rows, each containing only its owning fleet's
tasks. Their per-fleet counts must agree with the aggregate repository collection.

Synchronize all configured fleets with bounded concurrency. Each fleet owns independent
discovery completeness, snapshot transaction, upstream cursor, request budget, health
and last-good cache. A slow or unavailable fleet must not delay, roll back, mark stale or
change revisions for a successful fleet. Removing configuration stops new requests and
marks retained data unconfigured/stale; it does not delete records or make them local.
Re-adding the same stable fleet ID resumes that namespace.

## Aggregate and selected API scope

All collection APIs accept `fleet=all`, `fleet=local` or an existing fleet ID and return
the effective scope. This includes top-level `GET /api/repos`, `GET /api/tasks`,
`GET /api/sessions`, `GET /api/agent-sessions`, activity/event/timeline collections and
the data sources used by Fleet, Live and Graph views, as well as repository-scoped task
collections. A generated service that omits `GET /api/tasks` and only exposes
`GET /api/repos/{id}/tasks` does not provide an aggregate task collection. Detail routes
resolve fleet-qualified tracker IDs and expose `fleet_id`. Unknown filters return a
useful 404 or validation error, never an empty success that resembles a healthy fleet.
Aggregate counts sum visible namespaces without deduplicating matching display names or
upstream IDs. SSE event IDs remain tracker-global while payloads carry `fleet_id` and
upstream cursors remain per fleet.

## Global selector and stable navigation

The labelled header selector contains **All fleets**, **Local**, and every configured
fleet by display name. It persists as `fleet=all|local|FLEET_ID` in the URL, restores on
reload and Back/Forward, and visibly falls back to All fleets if a saved fleet disappears.
It scopes repository cards, boards, tasks, Activity, Fleet, Live, agent/session tables,
Timeline and Graph without changing stored records. All fleets is a real aggregate, not
an alias for the first connection. Local shows tracker-owned entities. A named fleet
excludes other fleets and local entities.

All-fleet rows, cards and events show a text fleet badge. Same-named projects and
overlapping upstream IDs remain distinct and navigate to fleet-qualified stable URLs.
Health remains per fleet; one failed fleet produces **Partial outage** while healthy
fleets continue to display Live. Steering and mutation always route by the selected
entity's stored fleet identity, never merely by the current selector value.

## Required generated acceptance

Run two authenticated fixtures named North and South that deliberately reuse project
`shared`, task `task-1`, agent `agent-1`, machine `host-1`, event sequence `1` and
transcript sequence `1`. Native and independent service checks must prove distinct
durable entities across restart, independent cursors and health, a one-sided outage,
correct aggregate counts, and one write routed to each fixture without crossing URL or
bearer token. Browser acceptance at desktop1440 and mobile390x844 switches among All,
Local, North and South; verifies scoped data, text badges, partial-outage state, stable
deep links, reload and Back/Forward; and operates the selector by keyboard without
overflow or browser errors. Through Settings, add North and South with write-only tokens,
rename North, replace South's token, remove North after confirmation and re-add the same
stable ID; prove synchronization changes immediately, token inputs stay blank and cached
North data is stale rather than deleted. Native configuration tests must accept a 0600
regular fleets file and reject 0640, 0644 and symlink inputs without leaking secrets.
