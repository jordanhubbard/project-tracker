# Active work

This file is the durable resumption queue for user-directed and discovered work. Before
implementation, follow `skills/agent/record-user-directed-work/SKILL.md`.
Keep detailed designs in focused roadmap documents and link them here.

## Detailed-roadmap lifecycle

This file is the sole resumable queue. Create a supporting file beneath `docs/roadmap/`
only when one item cannot keep a program's rationale, ordering, and acceptance contract
readable. Put this visible header immediately after the detailed document's title:

```markdown
- **Status:** active
- **Owning queue item:** [AREA-NNN](active-work.md#area-nnn-heading)
- **Completion / archival evidence:** pending while AREA-NNN remains open
```

Status is exactly `active`, `partial`, `deferred`, `completed`, or `historical`. The
owner must resolve to a checkbox or named program heading in this file. A terminal state
requires linked evidence. Keep a completed plan here only when doing so preserves useful
inbound links; move substantial closed programs beneath `docs/history/roadmap/`, retain
their owner, and mark them `historical`. Do not create a separate file for an ordinary
queue item or let `docs/roadmap/` become a plan archive.

## P0

### [ ] TRACK-001 — Repository and task workspace

- **Priority:** P0
- **Owner:** components/tracker
- **Direction:** Build the full repo and task application with LitAI, MAC authority, live physical host sessions, branch timeline and relationship graph, Trello task editing, database, MCP, A2A and backend LLM gateway.
- **Conclusion:** Create specification-led backend and browser frontend; use MAC when a repository matches a configured project and durable local storage only for unmatched repositories. Verify protocols and rendered interaction, not scaffold presence.
- **Depends on:** none
- **Implementation:**
  - [x] Author the complete application and protocol specifications with durable user objective.
  - [ ] Generate and build the frontend and backend through LitAI.
  - [ ] Connect MAC and verify repository matching, task writes and host session freshness.
- **Evidence:**
  - [ ] LitAI acceptance, persistence and authority-routing tests pass.
  - [ ] Browser desktop and mobile interactions and visual reference review pass.
  - [ ] Live MCP and A2A clients, branch DAG and session heartbeat checks pass.

### Current evidence and next action

- `litai onboard create` completed with the full-stack project type.
- `litai lock components/tracker` passed; `litai project validate` passed.
- Independent service probes are authored in `verification/acceptance/tracker.json`; they have not passed yet.
- The first run ended with `dependencies.import-bom-mismatch` for an artifact-generated static-data import; its source also omitted required protocol behavior. Preserve it as failed evidence, not a working app. The corrected Python run is terminal and rejected; its log is `_build/tracker-service-rebuild.log`. The active Node run uses `_build/tracker-node-rebuild.log`. Revalidate the active process before retrying.
- Chrome headless automation was launched successfully from isolated `_build/browser-qa`; product browser checks remain pending.
- No Git remote is configured; LitAI tracker/peer survey reported unsupported forge and skipped remote reconciliation.
- After the build, verify all product requirements, protocol clients and Trello visual fidelity; the initial service probes alone do not prove the whole goal.

### [ ] TRACK-002 — Service runtime flavor and complete candidate

- **Priority:** P0
- **Owner:** flavors/python-service
- **Direction:** Preserve the requested backend protocols and full application rather than accept omitted SDK and upstream integrations.
- **Conclusion:** The portable Python flavor constrains generation to stdlib; select a project-owned service flavor with declared runtime dependencies. The first candidate failed dependency observation and omitted required behavior.
- **Depends on:** none
- **Implementation:**
  - [x] Select a service Python flavor and bind its exact dependencies to an isolated runtime.
  - [ ] Regenerate the full application and review every requirement.
- **Evidence:**
  - [ ] Service builds with the declared SDKs and passes protocol and browser checks.

### Service flavor evidence

- Corrected default selectors resolve the project-owned `python-service` flavor. The greeting sample is retained outside the active product component roots.
- `litai verify` passes authority and current lock gates; the application test receipt is still missing.
- The service runtime imports FastAPI and MCP 2.2.0, including the real SDK Streamable HTTP constructor.
- `scripts/litai-service.sh --version` passed after syncing all 33 pinned runtime packages; the lifecycle selected that isolated interpreter.
- `verification/check_service.py` is an independent disposable-instance verifier for persistence, conflicting edits, and A2A idempotency/get/cancel; syntax checked, product execution pending.

### [ ] TRACK-003 — Supported full-stack dependency lifecycle

- **Priority:** P0
- **Owner:** flavors/node-service
- **Direction:** Keep the complete application and official SDK integration despite the installed Python dependency resolver limitation.
- **Conclusion:** The installed lifecycle rejects every requirements.txt or pyproject dependency declaration. Use its supported npm lock graph path with Node SQLite and the official MCP SDK; preserve the full product contract. Retain a sanitized upstream issue draft without unauthorized external posting.
- **Depends on:** none
- **Implementation:**
  - [ ] Declare a Node service flavor with a real locked npm dependency graph.
  - [ ] Regenerate the complete backend and frontend with explicit coverage of previously omitted integrations.
- **Evidence:**
  - [ ] Native dependency admission and all independent service, SDK and browser checks pass.

### Node lifecycle preflight

- The corrected Python run exited with `dependencies.python-lock-unsupported`. The installed resolver rejects all Python dependency manifests; there is no supported typed Python lock format to author in this version. Do not restart that run.
- Product implementation now selects Node, built-in SQLite, and the official JavaScript MCP SDK. The full application scope remains unchanged.
- `components/tracker/runtime.md` records the exact npm manifest and lock. `npm ci --ignore-scripts` passed. The installed LitAI lock projector accepted 95 package nodes and 160 dependency edges.
- One orphan optional peer-metadata entry in the npm-produced debug package lock was removed; it named no declared dependency. No package, version, integrity or actual dependency edge changed. npm ci verified the normalized lock.
- The new component lock passes. Next action in progress: generate using the supported Node/npm lifecycle, then execute all independent and browser checks.
- The independent verifier now also drives the official MCP SDK client and constructs a real Git fork/merge fixture. These checks are authored but have not yet run against a passing artifact.
- Upstream issue draft: Python service generation guidance currently permits SDK dependencies while Standard acquisition unconditionally rejects requirements.txt and pyproject dependency declarations. A future typed Python lock projection must enumerate exact packages, parents and source BOM coverage. No parent source was changed.

- npm and an explicit Make build profile cannot be combined by the installed Standard lifecycle. The product now explicitly removes Make and uses the supported npm profile. The final revised lock and documentation review pass; the Node build is active.

### Independent MAC and live-state checks

- Added `verification/mac_fixture.py` from the current public MAC project-summary contract (`project`/`project_id`, not raw `name`/`id` records), with authenticated requests and a controlled outage. Its HTTP schema/outage smoke check passed.
- The service verifier now checks MAC discovery, write routing, metadata preservation, integer priority compatibility, lifecycle rejection and no local fallback during outage. It also checks heartbeat/stopped records and SSE replay across restart.
- These product checks remain unexecuted until the active Node candidate passes the native lifecycle. Fixture verification is not evidence that the app integrates correctly.
- Corrected diagnosis: repeated Node Codex invocations were timeout retries, not plan/generate stages. The installed lifecycle defaults to 900 seconds and clears the source tree for each retry. The request still names `generate`, and the second child was replaced after roughly 15 minutes. The former stage explanation was incorrect.
- Added `verification/capture_browser.py` for desktop/mobile screenshots, accessibility snapshots and rendering failures. It is syntax checked; actual application rendering and control interactions remain pending.
- The independent service verifier now prints its disposable server log on failure so startup and protocol failures retain diagnostics.
- Pending specification correction after the current build: `/projects` returns summaries with `project` and `project_id`, not raw project records with `id` and `name`. The fixture already reflects the actual contract. Also explicitly specify integer MAC task priority.
- Added a disposable localhost LLM gateway check to the service verifier: verify the requested model and repository context, gateway bearer header and redacted browser responses. Syntax passes; application execution remains pending.
- Stopped lifecycle PID 22445 and current generator PID 27312 deliberately after diagnosing the repeated generation limit. Session 42461 is terminal (143); do not resume it. The partial third tree is preserved under `_build/interrupted-node-attempt`.
- Next action: set the supported `LITERATE_AI_CODING_CLI_TIMEOUT_SECONDS` override to 3600, correct the MAC contract and regenerate. Native admission and independent acceptance remain required.
- The timeout override and MAC corrections are committed; refreshed lock and authority gates pass. Fresh lifecycle session 16642 / PID 27607 is active, logging to `_build/tracker-node-long-rebuild.log`.
- The MAC acceptance fixture now additionally requires local task work for a confirmed unmatched repository while the fleet is configured, and unresolved authority for a new repository registered during an outage. Syntax checked; app execution pending.
- Extended the service verifier to run the real host-side reporter with a disposable child command and verify its physical hostname, child PID, repo/branch and stopped status. This tests reporter behavior; it does not claim deployment on remote hosts. Execution against the app remains pending.

### Final Node candidate diagnosis

- Session 16642 is terminal (exit 2). The lifecycle rejected duplicate installed copies of content-type before the native build. Its first invocation had retried; the final source remained available. The source snapshot watcher (10566) has ended.
- A compatible npm closure retains MCP SDK 1.30.0 and pins body-parser 2.2.1, type-is 2.0.1 and negotiator 1.0.0 within their upstream semver ranges. npm ci passes and the actual native `load_npm_source_authority` accepts all 91 packages. This is stronger than the earlier graph-projector-only preflight.
- An isolated diagnostic copy of the final source passed local edits, revision conflicts, restart persistence, heartbeat/stopped records, SSE replay, A2A idempotency/get/cancel/restart and official MCP tool/resource roundtrip. This is diagnostic execution, not LitAI admission.
- Corrected verifier assumptions: local state IDs are obtained from the workflow endpoint; A2A uses repo_id/task DataPart fields; installed Python MCP SDK uses input_schema/is_error attributes.
- LLM verification failed because the generated client discarded the configured /v1 gateway path. Preserve this regression check. Subsequent Git/reporter/MAC/browser checks have not yet run in this suite.
- Next authority repair: adopt the preflighted npm closure, clarify MAC discovery/deduplication/reporter association and gateway URL prefixes, then rebuild with a structured debug log.

### Diagnostic browser review

- Ran the preserved final candidate in a disposable database with the preflighted compatible npm closure. Desktop (1440px) and mobile (390px) screenshots are under `_build/diagnostic-browser`; neither viewport has page-level horizontal overflow.
- Visually inspected the board and task modal. The navy sidebar, dark columns, horizontal board and cards render, but CSP blocks the inline card-cover colors; this reduces fidelity and produces console errors. A favicon request also returned 404.
- Browser actions passed: create task, edit description while preserving labels, keyboard move with persisted state, second-client SSE update and workflow rename. Initial textarea selector failures were corrected using accessible textbox roles; they were verifier issues.
- Verified defect: Activity navigation renders the project overview instead of an activity feed. Source inspection shows the Agents & peers navigation uses the same overview fallback; that control still needs execution verification.
- These are diagnostic results from the previous candidate, not acceptance of the active revised build. Recheck the final revised frontend; if retained, fix cover styling under its actual CSP and implement the missing navigation views.
- Exercised a real temporary Git fork/merge fixture. The API returned the exact parent edges. Rendered Graph produced NaN node/edge coordinates and an effectively empty canvas; Timeline overlapped commits sharing the same timestamp. Screenshots and API evidence are under `_build/diagnostic-graph`. Both modes still need usable layouts, selection, zoom/reset and branch filtering in the final candidate.
- Added an explicit `--diagnostic-continue` mode to the independent service verifier. It collects later phase failures and still exits nonzero; ordinary acceptance remains fail-fast. Reporter invocation now uses the framework-required JSON argument array and a disposable token.
- That diagnostic run confirmed three failing phases on the old final candidate: LLM gateway path prefix, host reporter failing to publish its running child, and MAC auto-discovery returning an empty repo collection after the fixture's successful upstream reads. Log: `_build/node-remaining-diagnostics.log`. The active revised build already includes contract clarification for those behaviors; retest its final output.

### Exact source SBOM retry cause

- Structured tracing identified `coding_cli.generated_metadata_invalid`. Extracted the rejected BOM from the generation diff and reproduced its underlying cause: `sbom.source-version-missing` for the external Git component, which omitted both version and versionRange.
- A diagnostic copy adding Git's purl and versionRange `vers:generic/>=2.30.0` passed both strict source validation and the exact authority reconciliation path. No lifecycle evidence was modified or admitted by this diagnostic.
- Deliberately stopped build 74422 / PID 32931 and generator PID 36217 after identifying this concrete repair. Build is terminal (143). Preserve its debug trace and rejected BOM; do not resume that handle.
- Next repair is authoritative: state the Git runtime range and clarify the verified graph, timeline, cover-style and navigation requirements in a separate visual specification, then regenerate with existing full acceptance gates.
- Added and executed an independent two-instance A2A peer check against the preserved diagnostic candidate. It passed authenticated outbound task creation, retry idempotency, peer-token redaction and peer removal. The receiving instance rejects unauthenticated repository reads. The overall diagnostic remains failed on the previously identified LLM, reporter and MAC phases; this is not product acceptance.
- Extended the MAC fixture checks to require actual fleet writes from official MCP and A2A task creation, in addition to REST. These checks are authored and syntax checked; they have not executed past the old candidate's failed discovery step. All protocol paths must share MAC authority, not write shadow local tasks.
