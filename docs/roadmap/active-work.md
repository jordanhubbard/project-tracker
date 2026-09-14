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
    b37824adbd2ff5093391 passes full live import but fails three repair gates; see
    [candidate evidence](../../verification/track004-candidate1.json). Next action:
    close atomic snapshot, unresolved-reference/unchanged-long-text edit preservation
    and non-JSON outage regressions.
    Native acceptance must execute the new MAC self-check, not only pure vectors.
- **Evidence:**
  - [ ] Native authenticated fixtures cover reverse-order dependencies, missing and cross-project references, unchanged polls, deletion beyond 200 tasks, failure recovery and nonoverlapping slow synchronization.
  - [ ] Replay the real hub snapshot and verify complete project/task counts and dependency preservation.
  - [ ] Verify an isolated exported tracker completes live read-only synchronization and renders MAC tasks.

### [ ] TRACK-005 — Persist the Project Tracker workspace on GitHub

- **Priority:** P0
- **Owner:** repository
- **Direction:** Use git@github.com:jordanhubbard/project-tracker.git to persist this project.
- **Conclusion:** Origin is reachable and contains an unrelated starter commit. Preserve its ancestry and BSD license while retaining the established LitAI project authority; publish through the repository review workflow without force-pushing.
- **Depends on:** none
- **Implementation:**
  - [x] Configure origin and back up the previously verified workspace history.
  - [ ] Integrate starter ancestry and land the verified repaired workspace through a GitHub pull request.
- **Evidence:**
  - [x] Verify workspace-import exists on GitHub at 6ef7b8b4f39be4c23aec55d47414029c190aca4b.
  - [ ] Verify the merged GitHub main and local main agree after landing.

## Scope and retained history

TRACK-001 through TRACK-003 used isolated databases, authenticated MAC/LLM fixtures
and real child processes. TRACK-004 adds isolated read-only live fleet checks.
TRACK-005 adds the requested GitHub persistence; origin now points to the user-supplied
repository. Production fleet writes, background-service registration and fleet-wide
installation remain outside this work. Historical candidates and results remain in
Git history and ignored diagnostics; current repair status is recorded above.
