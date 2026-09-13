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
- The reusable browser capture checker now inspects SVG geometry attributes for NaN, Infinity and undefined, covering the rendered graph regression that visible-text checks can miss. This check remains alongside console, request and overflow checks.

### Visual rebuild snapshot checks

- Preserved an isolated snapshot of the still-running visual rebuild in `_build/visual-diagnostic`; this is not an admitted artifact. Independent runtime checks pass the LLM URL-prefix mock and actual Git/reporter child-process phase.
- Snapshot peer messaging discards the supplied A2A message and returns invalid DataPart data. MAC discovery creates a repo but task import fails with `UNIQUE constraint failed: states.repo_id, states.name`. The verifier now waits for the initial task import before testing confirmed absence, and includes health diagnostics if import fails. Recheck the generator's final output because it is still revising these modules.
- Snapshot browser checks show working colored covers under CSP, no console errors or document overflow at 1440/390px, and passing task create/edit/keyboard move/workflow rename. Second-client browser updates fail the four-second observation window; snapshot source only flushes SSE subscribers on a 15-second timer. Screenshots and interaction results are under `_build/visual-browser`.

- Visual rebuild 4636 terminated with exit 2 after successful source validation and native npm compilation. The new exact failure is `dependencies.source-range-unresolved`: the npm adapter cannot resolve the external Git range. Locally verified `git --version` is 2.50.1; runtime authority now records that exact observation and the wrapper fails on drift. The installed exact-version resolver accepts this declaration.
- Preserved final source separately as `_build/visual-final-diagnostic`. Its independent service checks retain the same peer and MAC import failures, while LLM and reporter phases pass. Authored explicit peer message forwarding/idempotency, repo-scoped MAC state mapping and prompt SSE delivery scenarios before the next rebuild.
- Final-source graph diagnostics confirm finite coordinates, exact Git parents and functioning initial selection/zoom/reset. Branch filtering drops the selection callback: selecting a filtered feature node leaves the merge commit in the inspector. Mobile styles also move the inspector off-screen; the long-path board fixture has 488px document width at a 390px viewport. Added explicit filter callback, sidebar-style scoping and route-focus requirements. Evidence: `_build/visual-final-graph`. The diagnostic script captures observations and does not itself certify all these interactions.

- Added reusable browser behavior and graph checkers in `verification/`. Both launch an isolated local service and return nonzero for failed behavior. Ran them against the retained final diagnostic: task create/edit/move/workflow/activity pass on desktop and mobile, while prompt SSE delivery fails. The graph checker distinguishes the selected hash from parent hashes and checks actual inspector screen bounds, detecting stale filtered selection and the mobile off-screen panel. Settings save/reload/redaction is included. These results are diagnostic evidence, not current-build acceptance.

- Extended independent MCP coverage to stdio using the official Python client and the portable service/mcp command. The retained final diagnostic passes local stdio creation with HTTP-visible database persistence. A separate stdio MAC-write assertion is ready but remains unreachable until MAC import succeeds; do not count it as passed. Log: `_build/visual-stdio-service-check.log`.

- Verifiers now accept equivalent REST entity/collection envelopes (for example repository vs direct entity, repositories vs items) without altering entity content or JSON-RPC. Workflow display names are normalized for case/spacing when selecting In progress. This avoids treating unspecified envelope presentation as a behavioral defect. The integration snapshot then passes peer roundtrip and initial MAC discovery/local routing; it still fails MAC writes through MCP and the portable JSON stdio/reporter invocation. Generator output remains mutable until terminal.

- Updated browser selectors for equivalent accessible navigation links/buttons, human-readable workflow labels, whole-workflow prompt editing and modal settings. The integration revised snapshot passes board create/edit/move, prompt SSE, workflow rename and settings persistence/redaction on desktop/mobile. Activity-created entries render task IDs instead of titles. Graph initial and filtered selection, zoom/reset and finite coordinates pass on desktop; mobile inspector remains off-screen. Evidence: `_build/integration-revised-browser` and `_build/integration-revised-graph`.
- Investigated generator configuration after repeated full-scope omissions: prior CLI trace reports gpt-5.6-sol with reasoning effort none. Installed LitAI supports an explicit `rebuild --model` pipeline selector but no reasoning-effort argument. Official Codex configuration documents reasoning controls; no user/global configuration was changed and the active build was left intact. A stronger model pass is available if the terminal source retains these omissions.

### Explicit-model rebuild

- Integration run 63702 / PID 41488 ended with `coding_cli.output_limit` after roughly 27 minutes: source-generation stderr exceeded the installed 16 MiB cap. This cap has no supported CLI/environment override in the installed adapter. Source is preserved in `_build/integration-final-diagnostic`; the terminal source retains the stdio/reporter portable-argument failures and MAC MCP-routing failure. No accepted artifact was produced.
- Added bounded generation-output guidance, exact portable service/mcp/session command examples, shared MAC-aware mutations for all protocol transports, and meaningful task titles in Activity. Refreshed lock/review/acceptance binding. The next plan explicitly resolves gpt-6-astra using the supported --model selector; no user/global Codex settings or framework code were changed. The default no-argument lifecycle wrapper now records this model choice.

- Explicit Codex/Astra run84493 ended after bounded metadata retries. Its transcript says it could not finish reading the long request because the framework's generation header forbids shell invocation and no direct file reader was exposed. Root `.literate/spec-map.json` also triggered unexpected-output validation; no source was admitted. Preserve `_build/tracker-astra*`. No safety/lifecycle restriction was removed.
- Switched through LitAI's supported `CODING_CLI=claude` selection. Installed Claude Code is 2.1.269; the plan selects provider claude and cli-configured-default, with direct Read/Write/Edit tools. Run50677 is active; actual model and product success remain unverified. Wrapper default selects this frontend while preserving explicit CODING_CLI overrides.
- Added MAC regression assertions for unchanged-poll revision stability and equivalent SSH registration resolving to the discovered repository. These are authored/syntax checked and await execution on a candidate that passes earlier MAC protocol checks.

### Claude generation diagnostics

- Initial Claude generation completed, then LitAI rejected test metadata. Reproduced the precise error with the installed canonical JSON function: case 28 contains a fractional coordinate (0.1), which canonical JSON v1 rejects. Stopped the unchanged retry (run50677, PID49230, child53528) to author this exact constraint before another build. Retained complete first-pass snapshots; no artifact was admitted.
- Independent service diagnostics pass local CRUD/persistence, stdio MCP, backend LLM mock, actual Git/reporter session, equivalent SSH MAC registration and MAC creates through REST/HTTP MCP/stdio MCP/A2A. Failures include A2A restart loss, peer-token disclosure in the registration response, missing imported labels, revision churn on unchanged MAC polling, success status for rejected completion, and false local authority during an outage. Logs: `_build/claude-service-outage.log`.
- Browser network evidence identifies HTTP 404 on /api.js: the server's prefix API classification swallows a required static module. The shell renders but the application never starts. Evidence: `_build/claude-browser-network/desktop-startup-errors.json`. Added durable HTTP failure capture and diagnostic phase isolation; these checks do not constitute acceptance.
- Added precise regression scenarios to quality.md, including integer-only generated metadata, durable A2A retry state, peer response redaction, HTTP route boundaries and MAC outage behavior. Full requested scope remains pending.
- Explicit-model run67702 / PID54031 is launched with Claude Code `--model claude-fable-5-1`, confirmed in the adapter subprocess trace. Current source workspace and snapshot location are recorded in ignored `_build/active-run.json`; model availability and final success require the actual result.
- Added `--irregular-times` to the independent graph browser checker. Its real Git fixture uses 0/10/100/110-second commit intervals and asserts horizontal node spacing through SVG transforms. Executed against the retained integration snapshot: proportional spacing and desktop interaction pass; the already-known off-screen mobile inspector still fails. Evidence: `_build/integration-irregular-graph`. This verifies the checker and that snapshot, not the active build.
- Peer diagnostics now separate response redaction from forwarding and accept equivalent REST wrappers around a valid A2A Task. The retained Claude candidate passes authenticated forwarding, retry idempotency and peer removal; response token disclosure still fails independently. Evidence: `_build/claude-service-peer-final.log`. JSON-RPC itself is not normalized or weakened.
- Added `verification/check_all.py` and a short verification README. The suite runs the independent service, board, equal-time graph and irregular-time graph checks, retains per-phase evidence and returns nonzero if any fail. Executed all four phases against the retained failing Claude snapshot and confirmed failure reporting. Summary is initialized as incomplete for each run and replaced atomically; it is explicitly not a LitAI receipt.

### Explicit Fable backend checkpoint

- Preserved `_build/fable-backend-diagnostic` from the active generation, with the approved installed npm closure linked only in that diagnostic copy. No active generated source or native admission was edited.
- Adapted independent REST normalization for raw collection arrays while preserving JSON-RPC responses. A fresh stdio MCP process initially returns explicit mac_unavailable during discovery; the verifier now retries only that readiness response for at most ten seconds and still requires the actual fleet write. It does not retry other protocol errors or permit a shadow local task.
- `_build/fable-backend-ready-check.log` passes the complete independent service suite: local persistence/conflicts/SSE, A2A restart/idempotency, official HTTP and stdio MCP, peer authentication/redaction/retry, backend LLM mock, real Git/reporter PID lifecycle, MAC import/unchanged polling/SSH equivalence/all-protocol writes/metadata preservation/lifecycle rejection/outage without fallback. This is a mutable-generation snapshot checkpoint, not an admitted artifact or product completion. Browser/native lifecycle checks remain pending.

### Fable frontend and generated-test checkpoint

- Adapted browser checks for accessible tab roles, labelled branch filtering, a class-based commit inspector, a real workflow editor dialog and descriptive LLM setting labels. Settings reopening now waits for visible controls rather than reading a hidden prior password input. These are equivalent UI presentations, not changed product requirements.
- `_build/fable-graph-detail` and `_build/fable-graph-irregular` pass desktop/mobile graph/timeline finite geometry, actual ancestry, selected hashes before/after branch filtering, zoom/reset, reachable inspectors and unequal timestamp spacing.
- `_build/fable-browser-settings-ready` passes create, prompt SSE, workflow rename, Activity and desktop settings persistence/redaction. Reproducible product defects remain: immediate edit-then-move uses the old revision and fails 409; mobile CSS hides the only Settings button. No accepted completion is claimed.
- Expanded checks show search and desktop drag/drop pass. Dragging to an off-screen column with Playwright at mobile width did not complete; mobile gesture behavior remains unverified. The durable mobile check uses the supported accessible move control after loading, while retaining the failing rapid edit/move sequence as a separate regression.
- All 33 generated native tests pass in `_build/fable-test-diagnostic`; the current 33-case manifest also passes the installed canonical JSON serializer. This is diagnostic execution only. The active generator still must finish the source BOM and native lifecycle admission.
- Expanded browser review passes repository origin display and description persistence at desktop/mobile, search and the settled mobile accessible move. The actual reporter appears in Fleet with its real hostname, child PID, CLI and branch, but the stopped state does not arrive live. Source review confirms the browser event list omits session events and the session store does not publish a change event. This joins the rapid edit/move revision race and hidden mobile Settings control in the next authored repair.
- The render loop also drops refresh requests while another render is pending; future repair must queue a follow-up render and refresh overview counts rather than retain stale cached overview state. Keep these as authoritative observable regression scenarios, not manual edits to the generated candidate.

### Fable terminal result and interaction repair

- Run67702 / PID54031 ended with exit 2 after native dependency resolution/build and all 33 generated tests passed. Acceptance rejected the old specification binding captured at startup. The operator's binding extraction initially failed on the structured identity and the shell nevertheless launched rebuild before the subsequent correction; current on-disk binding was corrected, but that could not alter the already-captured run. This was an orchestration mistake, not an application or user configuration failure.
- Preserved terminal source at `_build/fable-final-diagnostic`. No accepted receipt exists. The next cycle must complete and verify lock/review/acceptance binding before starting rebuild in a separate dependent tool call.
- Authored explicit immediate edit/save/move consistency, retained failed drafts, queued render invalidation, mobile Settings reachability, and live session/overview updates. These preserve the full existing scope and target the observed browser defects.
- Stopped interaction run96697 / PID61426 during preflight (terminal143), before its coding CLI child started, to include a newly confirmed peer UI defect in the same repair. In a real two-instance browser fixture, the Remote repository id select offers only the sender's local ID and cannot address the receiver's disjoint repository. Evidence: `_build/fable-peer-ui/result.json` and `remote-selection.png`; backend peering itself already passes. Added a remote catalogue or explicit remote-ID input scenario to quality.md.
- Added a durable two-instance `verification/check_peer_browser.py` and included it in the independent suite. It verifies UI peer registration, ability to address the receiver's repository, remote task creation, redaction and removal. Executed against the retained final Fable candidate; it correctly fails on the local-only remote selector. Run10263 / PID64523 now uses the fully revised specification and pre-verified acceptance binding.
- Extended the independent persistence test to cover assignee, branch, cover color, due date and dependency references in addition to existing fields, plus rejection of a dependency cycle. The retained final Fable candidate passes the complete expanded service suite (`_build/fable-all-attributes-check.log`).
- Browser SSE checks now verify a second client's task creation and subsequent title/description update without reload; both desktop/mobile pass on the retained candidate (`_build/fable-live-attributes-browser`). Existing rapid-move and mobile Settings failures remain. Added `verification/product-evidence.md` to map the full objective to current evidence and pending final-artifact checks.
- The expanded live-attribute browser check opens the task detail dialog after a second-client update and confirms the new description, in addition to the changed card title. Both desktop/mobile pass on the retained final candidate (`_build/fable-live-detail-browser`).
- Full workflow UI lifecycle passes at desktop/mobile on the retained candidate: add a list, reorder it, create a task in it, delete it with an explicit destination and verify task migration (`_build/fable-workflow-lifecycle`).
- The browser also verifies the remote-only graph's checkout-needed explanation, absence of fabricated commit nodes and return to Board at both sizes (`_build/fable-remote-graph-browser`). These checks are included in the durable browser suite for the final artifact.
- The durable peer browser fixture now creates the sender's first repository through the empty-state registration dialog, verifies its saved URL/local authority via the API, then continues to peer setup. Registration passes on the retained final candidate; the subsequent known remote-selector failure remains (`_build/fable-repo-registration-ui/result.json`).
- Added `verification/check_expiry_browser.py` to the full independent suite. It posts one clearly synthetic heartbeat, then observes the browser without additional application API requests through the real 90-second deadline. At 110 seconds the retained final Fable candidate still shows active and one active session, so the check correctly fails (`_build/fable-expiry-browser/result.json`). The current authored repair already requires expiry/status/count updates.
- Reporter verification accepts either running or active as the fresh session's status presentation; it still requires the actual spawned PID, repository, host, branch and stopped lifecycle. The current replacement exposes derived active status separately from reported running status.
