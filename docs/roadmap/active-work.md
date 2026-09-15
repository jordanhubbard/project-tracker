# Active work

This is the durable queue for the requested Project Tracker application. The local
implementation passed isolated acceptance; live MAC synchronization repair is active
under TRACK-004. Earlier scoped evidence is in
[product completion evidence](../user/verification.md) and
[the consolidated result](../../verification/final-result.json).

## P0

### [x] TRACK-001 — Repository and task workspace

- **Priority:** P0
- **Owner:** components/tracker
- **Direction:** Build the full repo/task frontend and backend with MAC authority,
  physical host sessions, Git timeline/graph, Trello editing, database, MCP, A2A
  and backend LLM gateway settings.
- **Conclusion:** The verified local artifact implements the requested workspace.
  MAC remains authoritative for matched projects; only confirmed absence permits
  local work. Outages preserve cached data and reject upstream mutations.
- **Depends on:** TRACK-003
- **Implementation:**
  - [x] Author the complete application/protocol specifications and durable objective.
  - [x] Generate and build the frontend and backend through LitAI.
  - [x] Connect MAC and verify matching, writes, live status and host-session freshness.
- **Evidence:**
  - [x] Native acceptance, SQLite persistence and authority routing pass.
  - [x] All 15 board interactions pass at desktop1440/mobile390; screenshots reviewed.
  - [x] Official MCP clients, authenticated A2A peers, both Git timing fixtures,
    real reporter lifecycle and heartbeat expiry pass against the final source.
  - [x] Public exported launch, protected login, live events and Settings pass.
- **Completion evidence:** Authority e09a08c, artifact 6119bda93ad771d2ed03;
  28 native tests and nine independent phases plus failure-state probes pass.
  Run/configuration/reporter instructions are in the root README and project guide.

### [x] TRACK-002 — Service runtime flavor and complete candidate

- **Priority:** P0
- **Owner:** flavors/node-service
- **Direction:** Preserve the complete application and official SDK integration
  through a supported service dependency lifecycle.
- **Conclusion:** The initial Python route was unsupported by the installed
  dependency resolver. The supported Node/npm flavor fulfills the same product
  scope, using built-in SQLite and the official MCP SDK.
- **Depends on:** TRACK-003
- **Implementation:**
  - [x] Evaluate the Python service route and retain its rejection evidence in Git history.
  - [x] Select the supported service runtime and exact dependency closure.
  - [x] Generate the complete frontend/backend and review every product requirement.
- **Evidence:**
  - [x] Native dependency admission, protocol checks and browser interactions pass.
- **Completion evidence:** The final artifact and framework receipt are current;
  [product evidence](../user/verification.md) records the full scope.

### [x] TRACK-003 — Supported full-stack dependency lifecycle

- **Priority:** P0
- **Owner:** flavors/node-service
- **Direction:** Keep the full application and official SDK despite the installed
  Python dependency resolver limitation.
- **Conclusion:** Node 22.23.2, Git 2.50.1 and the exact npm dependency graph build
  successfully through the installed LitAI lifecycle. No framework/cache edits or
  handwritten generated-product patches were used to bypass acceptance.
- **Depends on:** none
- **Implementation:**
  - [x] Declare the Node service flavor with the locked npm graph and official SDK.
  - [x] Generate the complete backend/frontend with all requested integrations.
- **Evidence:**
  - [x] Native dependency admission and all 28 native tests pass.
  - [x] Independent service, SDK, MAC and browser checks pass on final source.
  - [x] The supported build updates both the public run export and current receipt.
- **Completion evidence:** `verification/current.json`,
  [final-result.json](../../verification/final-result.json) and the verified public
  launch command in the root README.

### [ ] TRACK-004 — Complete live MAC task synchronization

- **Priority:** P0
- **Owner:** components/tracker
- **Direction:** Fix the live integration failure and verify project and task handling against the accessible MAC hub.
- **Conclusion:** Live import aborts on valid upstream dependency IDs after three projects; requests also time out. Correct upstream/local identity translation, complete fleet reconciliation and observable synchronization failures. Use isolated read-only live verification; production writes remain deliberate UI actions.
- **Depends on:** none
- **Implementation:**
  - [ ] Reject stale discovery as proof of absence after a healthy-to-unavailable MAC transition; new unmatched registrations remain unresolved and cannot create local shadow tasks.
  - [ ] Correct candidate16 session expiry: a persisted stale session must project as stale, never stopped, across events, REST and browser views; retain exactly-once expiry and heartbeat reactivation checks.
  - [ ] Give every checklist completion checkbox an accessible name, including newly added rows.
  - [ ] Preserve upstream MAC identity and owner fields in public task list/detail projections. Candidate16 stored these fields but omitted them from REST responses, preventing external reconciliation.
  - [ ] Prevent obsolete asynchronous route renders from reopening registration dialogs after successful saves and navigation.
  - [ ] Make status-only toasts non-intercepting; verify immediate mobile Settings saves during visible notifications.
  - [x] Rebind the reviewed persistent-service contract without changing its probes or isolated data directory. Candidate15 then passed the supported build using the retained generation checkpoint (7 native groups); independent UI findings still block final acceptance.
  - [ ] Correct candidate14's late fleet identity-index regression: insertion and lookup must use the same composite key; retain real dependency-only update assertions.
  - [ ] Return a useful client-validation error for invalid local dependencies, preserving rows, revisions and events on rejection.
  - [ ] Keep the mobile navigation drawer dismissible and close it after navigation; verify Activity and Settings remain reachable.
  - [ ] Re-run the complete native lifecycle after these corrections. Candidate14 was rejected; provisional earlier-source checks do not establish acceptance.
  - [x] Specify order-independent upstream dependency import and outbound identity translation with fleet-scale reconciliation.
  - [ ] Regenerate the exported application through the supported lifecycle. Candidate
    7a1f3cd0aa4d08717013 passes 46 native tests, fleet import, atomic rollback,
    unresolved-reference/long-text edits and non-JSON outage checks. See
    [candidate evidence](../../verification/track004-candidate3.json).
  - [ ] Correct newly selected dependency translation on existing MAC tasks; native
    regression must inspect actual upstream writes, including the first edge.
  - [ ] Preserve Git filtering during regeneration when a branch and filename collide;
    verify exact reachable hashes and both timestamp browser fixtures.
  - [ ] Preserve every upstream lifecycle state during import and install MAC's full
    supported workflow. The next generation was interrupted after its provisional
    snapshot mapped 7,622 tasks to open; its dependency/Git fixes passed focused
    checks. Correct the MAC-only fixture's unsupported in_progress assumption,
    retain local defaults, and add native state-preservation coverage. See
    [candidate-four evidence](../../verification/track004-candidate4.json).
  - [ ] Enforce a deadline on response-body consumption itself. Candidate five's
    provisional backend preserves all captured states and passes its nine native
    MAC flags, but a stalled successful response stays pending after the 60-second
    abort signal. Require the real default-budget regression in the native gate.
  - [ ] Keep the dependency projection identical after a write and the next
    unchanged poll. Candidate five temporarily drops a cross-project link from
    that projection, then restores it with an extra revision. Raw upstream
    references remain intact. See [candidate-five evidence](../../verification/track004-candidate5.json).
  - [ ] Advance revisions and publish one committed event for genuine dependency-only
    upstream changes. Candidate six fixes the default body deadline and connection
    cleanup, but suppresses revisions/events while applying changed relationships.
    Verify both dependency-only and combined field/dependency changes. See
    [candidate-six evidence](../../verification/track004-candidate6.json).
  - [ ] Handle rejected asynchronous timeout cleanup without crashing. Candidate seven
    passes focused dependency/event and Git collision checks, but its timeout
    cleanup crashes and its native suite exceeds the fixed 60-second runner limit.
    Use short native timeout coverage plus full default-budget exported-service
    acceptance. See [candidate-seven evidence](../../verification/track004-candidate7.json).
  - [ ] Own MAC request/response handles through an absolute deadline. Candidate
    eight rejects at60seconds without an asynchronous cancellation crash, but the
    original connection remains open past65seconds. Use the built-in HTTP/HTTPS
    transport with explicit handle destruction and retain both timeout test scopes.
    See [candidate-eight evidence](../../verification/track004-candidate8.json).
  - [ ] Accept the full byte volume of a fleet response through the actual HTTP
    transport. Candidate nine passes default deadline/socket/follow-up, Git,
    dependency events and adapter-level snapshot checks, but its48MiB cap rejects
    the80,765,554-byte captured collection. Require256MiB production capacity,
    native >=80MiB synthetic transport coverage and final actual-service replay.
    See [candidate-nine evidence](../../verification/track004-candidate9.json).
  - [ ] Establish task identities across all discovered projects before resolving
    cross-project references, and preserve populated local workflow membership on
    rename. Candidate ten passes full captured HTTP replay, default transport cleanup,
    synthetic writes and backend protocols, but native MAC acceptance rejects a
    later-project reference initially classified as missing. Its synthetic response
    fixture also measures below 80 MiB. A populated-state rename leaves tasks in a
    nonexistent state. See [candidate-ten evidence](../../verification/track004-candidate10.json).
  - [ ] Reconcile disappeared upstream task IDs across every cached MAC repository,
    including projects absent from the latest successful discovery snapshot, while
    preserving local tasks and repository metadata. Candidate eleven fixes first-poll
    foreign references and populated-state rename, but leaves tasks from disappeared
    projects in the read store. Its native rollback assertion also incorrectly expects
    zero historical task events instead of zero new task events. Retain existing
    events and assert against the pre-failure cursor/count. See
    [candidate-eleven evidence](../../verification/track004-candidate11.json).
  - [ ] Verify dependency preservation from actual upstream and cached task state,
    allowing unchanged fields to be omitted from an update request. Candidate twelve
    passes removed-project cleanup, empty-fleet local retention, default timeout,
    all eleven independent HTTP write checks and native protocol checks, but its
    native explicit-removal test requires an unchanged dependency field in the PUT
    payload. Correct that assertion without weakening preserved-edge, explicit
    removal, new-edge translation or unchanged-poll checks. See
    [candidate-twelve evidence](../../verification/track004-candidate12.json).
  - [ ] Track the exact socket serving the native stalled-response request, including
    keep-alive reuse. Candidate thirteen passes eight native MAC groups but the
    timeout assertion inspects only newly accepted connections. An independent
    actual-client probe confirms reuse, deadline rejection, closure of that exact
    socket before fixture cleanup, and healthy recovery. Preserve these positive
    assertions in the native diagnostic. See
    [candidate-thirteen evidence](../../verification/track004-candidate13.json).
  - [ ] Deliver the accepted repair through the supported committed-source cache;
    verify portable isolated acceptance and cache reuse in a fresh GitHub checkout.
    These runtime-delivery checks remain here after the workspace import lands.
- **Evidence:**
  - [ ] Native authenticated fixtures cover reverse-order dependencies, missing and cross-project references, unchanged polls, deletion beyond 200 tasks, failure recovery and nonoverlapping slow synchronization.
  - [ ] Replay the real hub snapshot and verify complete project/task counts and dependency preservation.
  - [ ] Verify an isolated exported tracker completes live read-only synchronization and renders MAC tasks.

### [x] TRACK-005 — Persist the Project Tracker workspace on GitHub

- **Priority:** P0
- **Owner:** repository
- **Direction:** Use git@github.com:jordanhubbard/project-tracker.git to persist this project.
- **Conclusion:** The development workspace is persisted on main through
  [PR #1](https://github.com/jordanhubbard/project-tracker/pull/1), merge
  f455508a85b487d9290375993fec16420a93763f. Starter ancestry and the BSD license are
  preserved. A fresh main clone passes integrity checks and matches the imported
  tree. Runtime repair and accepted-cache delivery remain open under TRACK-004;
  the import makes no final application-acceptance claim.
- **Depends on:** none
- **Implementation:**
  - [x] Configure origin and back up the previously verified workspace history.
  - [x] Integrate starter ancestry and land the validated workspace through a GitHub pull request.
- **Evidence:**
  - [x] Verify workspace-import exists on GitHub at 6ef7b8b4f39be4c23aec55d47414029c190aca4b.
  - [x] Verify merged GitHub main and local main both equal f455508a85b487d9290375993fec16420a93763f before follow-up repair work.
  - [x] Verify a fresh main clone with git fsck, starter/workspace ancestry, and an identical imported tree.

Documentation draft review passes `project validate`, including local links, anchors,
reachability and authority review. Python and shell examples pass syntax checks.
Runtime example checks and final acceptance claims remain pending with TRACK-004.

## Scope and retained history

TRACK-001 through TRACK-003 used isolated databases, authenticated MAC/LLM fixtures
and real child processes. TRACK-004 adds isolated read-only live fleet checks.
TRACK-005 adds the requested GitHub persistence; origin now points to the user-supplied
repository. Production fleet writes, background-service registration and fleet-wide
installation remain outside this work. Historical candidates and results remain in
Git history and ignored diagnostics; current repair status is recorded above.

### [ ] TRACK-006 — Complete Project Tracker documentation

- **Priority:** P1
- **Owner:** documentation
- **Direction:** Write all project documentation alongside the MAC integration repair.
- **Conclusion:** Provide a coherent product and contributor manual grounded in authored contracts and verified behavior; distinguish supported setup from pending runtime acceptance.
- **Depends on:** TRACK-004
- **Implementation:**
  - [x] Write setup, configuration, project/task workflows, Git and fleet guides, API examples, architecture, development, backup and troubleshooting documentation.
  - [x] Replace stale completion claims and connect every guide from the documentation index and README.
- **Evidence:**
  - [ ] Validate documentation links and project authority; check commands and examples against the accepted artifact and supported CLI.
  - [ ] Persist reviewed documentation on GitHub with the repair and record the final verification scope.

### [ ] TRACK-007 — Publish the first Project Tracker release

- **Priority:** P0
- **Owner:** project
- **Direction:** Make the first release on GitHub. The user explicitly authorizes native npm packaging with archive verification and GitHub upload for this cut.
- **Conclusion:** Publish v1.0.0 from an accepted application and complete documentation. Replace the inherited sample release gate with tracker acceptance, resolve current native failures, package and verify artifacts, land the repair, and verify remote release publication.
- **Packaging follow-up:** Literate AI 1.0.1 cannot build npm packages. Filed [upstream issue #411](https://github.com/NVIDIA-dev/literate-ai/issues/411), assigned to milestone 1.1. Use native `npm pack` for this release, bind it to accepted source and verify extraction, installation, runtime and uploaded bytes.
- **Depends on:** TRACK-004, TRACK-006
- **Implementation:**
  - [x] Configure the tracker release policy and verified native npm packaging. Candidate15 archive passed exact47-file verification, fresh installation,7 native groups,22 service checks,6 rejected-write checks and byte-for-byte GitHub draft download verification. See [candidate15 evidence](../../verification/track004-candidate15.json).
  - [ ] Resolve native acceptance failures and finish final service, browser, live and portable-cache checks.
  - [ ] Prepare, check and publish v1.0.0 with truthful notes and verified release artifacts.
- **Evidence:**
  - [ ] Current native and independent runtime acceptance passes for the exact release revision.
  - [ ] The GitHub release, tag, downloadable artifacts and source revision are verified remotely.

### [x] TRACK-008 — Deploy published v1.0.0 to puck.local

- **Priority:** P0
- **Owner:** operations
- **Direction:** Deploy the published release to puck.local.
- **Conclusion:** Install unchanged verified release assets with durable private storage, managed startup, protected browser access and read-only MAC synchronization; verify actual health and remote access.
- **Depends on:** none
- **Implementation:**
  - [x] Inspect host prerequisites and existing configuration; verify the published archive and install locked dependencies.
  - [x] Install and start a managed service with separate persistent data and private credentials.
- **Evidence:**
  - [x] Confirm native diagnostics, remote HTTP readiness, authenticated browser access, managed restart and MAC synchronization when configured.

Deployment completed: unchanged v1.0.0 archive,7 native groups, authenticated browser
access, graceful managed restart and exact MAC comparison of28 repositories/8947tasks
passed. See [deployment evidence](../../verification/deployment-puck-v1.0.0.json) and
[operator guide](../user/deployment.md). The existing release UI limitations remain.

### [ ] TRACK-009 — Show MAC project metadata in repository Inspector

- **Priority:** P1
- **Owner:** component://project-tracker/tracker
- **Direction:** Expose the per-project information and metadata stored by MAC in Project Tracker.
- **Conclusion:** Fetch MAC project detail for each discovered MAC project, retain a bounded safe projection in the local cache, expose it through the repository detail API, and display structured metadata in Inspector while preserving last-good data during outages.
- **Depends on:** TRACK-004
- **Implementation:**
  - [x] Specify the project-detail data model, privacy boundary, synchronization behavior, REST contract and Inspector presentation.
  - [ ] Regenerate the application through the supported LitAI lifecycle.
  - [ ] Verify authenticated MAC project-detail reads, atomic persistence, outage retention, API schemas and desktop/mobile Inspector rendering.
- **Evidence:**
  - [ ] Generated native acceptance and independent service/browser checks pass for the exact artifact.
  - [ ] A read-only deployed-fixture comparison confirms displayed project identity and metadata without production writes.
