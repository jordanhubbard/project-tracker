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
