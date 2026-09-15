# MAC integration

[Documentation](../README.md)

MAC is the upstream project and task authority. Project Tracker supplies the board,
local read cache, Git views and protocol interfaces. Configure the backend MAC URL and
credential in Settings or through the [environment](configuration.md).

## Authority decisions

| Situation | Result |
| --- | --- |
| No MAC connection configured | Local tracking is available |
| Successful project and registry discovery finds a match | MAC owns the matched project's tasks |
| Both discovery collections succeed with no match | The repository may use local tracking |
| Discovery is unavailable or incomplete | A new registration remains unresolved; failure does not establish absence |
| Previously matched MAC project encounters an outage | Preserve MAC authority and cached tasks; reject upstream mutations |
| A local repository with tasks later matches MAC | Preserve local work and mark migration required; do not silently replace it |

Matching uses canonical repository URLs or paths, with an explicit MAC project selection
for ambiguous cases. The registry's `source` field describes a source kind such as `git`;
it is not itself a repository URL. Discovery reads project and registry metadata.

Viewing projects, opening Settings and configuring a URL do not register upstream projects.
**Register with MAC** is an explicit operation. Existing local work requires a deliberate
migration decision before switching its ownership.

## Synchronization and scale

The backend synchronizes on startup and schedules polls every five seconds. Overlapping
polls share one in-flight synchronization, so a slow upstream does not accumulate concurrent
polls. Discovery reads `/projects` and `/bridge/repositories`; task import reads `/tasks`.
Fleet information also reads `/agents` and `/machines`.

A successful import reconciles the complete project-scoped snapshot, including records
beyond the UI's first page. Task dependencies are translated after identities are known,
so upstream ordering cannot drop forward references. The import commits atomically;
failure keeps the previous complete task snapshot and publishes no partial task changes.

The tracker preserves exact upstream task state, MAC ID, owner and foreign metadata.
Tracker-specific labels, cover, checklist and branch information use
`metadata.project_tracker`. Missing and cross-project dependency references remain durable
and visible. Repeated identical snapshots do not create new revisions or task events.

## Writes and failures

Create and edit operations use MAC's APIs through the same service used by REST, MCP and
A2A. Field edits and lifecycle transitions are separate upstream operations. A transition
rejection remains a rejection. On partial multi-step success, the application refreshes
actual upstream state and reports what applied; a timeout never proves success.

When MAC is unavailable, cached boards stay readable and upstream mutations return an
unavailable error rather than creating shadow local tasks. A 503 remains an outage even
when its body is HTML, empty or malformed JSON. Authentication and validation failures
must be addressed at their cause.

Reads have a 60-second deadline through body consumption; writes have a 30-second budget.
The deadline must release its connection and allow recovery, including when a successful
HTTP response starts but never completes. Check [verification](verification.md) for the
current evidence covering this behavior.

## Diagnosing a connection

1. Confirm the configured URL is the MAC API base and that the credential is valid.
2. Inspect the repository authority, last successful sync and displayed error.
3. Check both project and registry discovery; one healthy endpoint is insufficient.
4. Compare all paginated tracker tasks with a stable upstream snapshot when auditing scale.
5. After an outage, confirm synchronization recovers and cached task revisions remain stable
   when upstream data is unchanged.

For the installed MAC CLI, the verified project-list syntax is `mac --json project list`.
`mac list` is not its supported command. CLI filters may differ from raw HTTP collections;
compare the same scope before treating different counts as missing data.

This project's live acceptance reads the real fleet through an isolated tracker. Mutation
checks use authenticated synthetic fixtures. It does not claim production write testing
or fleet deployment. See [operations](operations.md) for data protection and
[troubleshooting](troubleshooting.md) for common symptoms.
