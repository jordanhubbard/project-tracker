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


### UI candidate review and next regeneration

- Run10263/PID64523 terminated with `dependencies.lock-edge-missing`: its source BOM omitted @hono/node-server@2.1.1 -> hono@4.13.7. Preserved final source at `_build/ui-final-diagnostic`; no admission or receipt.
- Current board checks pass every interaction at desktop/mobile, including immediate edit/save/move, workflow migration, live task detail, inspector and Settings. Document overflow remains 1526/1440 and 1299/390. Inspector origin is correctly presented as an input; the checker now accepts it and waits for the view before inspection.
- Backend independent suite passes except duplicate local checkout identity through a symlink. Canonical fixture paths allow the real reporter PID and live stopped state checks to run independently; alias rejection remains a separate mandatory assertion.
- Session expiry fails after 110 seconds without activity. Peer UI successfully registers the authenticated receiver but Send message throws Illegal invocation from the unbound browser crypto method. Evidence is retained under `_build/ui-expiry-browser` and `_build/ui-final-peer`.
- Added explicit specification regressions for peer lock edges, actual expiry notification, realpath identity, shrinkable layout and receiver-bound crypto invocation. Lock and documentation review passed; acceptance binding sha256:4195cd54588d2aab087c9d78cc0e7cc96380409c98fd577bc79b80b82723c987 was read back before launch.
- New full lifecycle session68694/PID72610 uses Claude Code with explicit claude-fable-5-1. Logs `_build/tracker-polish-rebuild.log` and `_build/tracker-polish.debug.jsonl`. It is running, not yet accepted. No generated product source or framework implementation was patched.

- Follow-up graph checks now wait for the actual rendered selection/filter/zoom state, click commit circles, and distinguish the selected hash from parent hashes. Equal-time and irregular-time graph behavior passes; the latter yields x=60/115/605 for 0/10/100 seconds. Only board/mobile inspector overflow remains in those runs (`_build/ui-final-graph-ready.log`, `_build/ui-final-graph-irregular.log`).
- Extended the independent service fixture to exercise an unborn checkout before its first commit and a detached HEAD after merging. Both pass in `_build/ui-final-service-states.log`; the overall suite still fails honestly on duplicate symlink identity.
- Visually compared `_build/ui-final-browser/desktop-board.png` with the user attachment. Dark rail/list/card structure and covers are present, but pale native move selects have poor text contrast and the board overflows. These remain review items for the replacement artifact, not a visual pass.

- Added a 1,005-commit fast-import fixture to the service suite. The retained UI candidate returns 200 commits, marks truncation and preserves the one real parent outside the window; all returned parent lists match Git. Evidence `_build/ui-final-service-boundary.log`. Rendering the boundary marker remains part of final browser review.

- Added and ran `verification/check_git_states_browser.py`: desktop/mobile empty history and 1,005-commit truncated graph views pass, including scrolling to the actual boundary-parent marker with no page errors. Captures/results `_build/ui-final-git-states`. Included this checker in `check_all.py`; overall acceptance still requires the unresolved candidate repairs.

- Replacement snapshot `_build/polish-backend-diagnostic` (from c4ea72521bda1646) passes 27 generated native cases and the full independent backend suite, including realpath/symlink deduplication, actual reporter child/stopped lifecycle, bounded/empty/detached Git, MCP, A2A retries and MAC isolation. Evidence `_build/polish-backend-ready.log`, `_build/polish-native-diagnostic.log`. The peer result checker now accepts an explicit response-wrapped JSON-RPC envelope while still rejecting protocol errors and requiring a completed remote Task plus exactly one retry-created board task.
- Generation68694 remains live. The new source has a scheduled session-expiry publisher and shrinkable layout tracks, but these are not browser pass claims. Frontend generation and native admission are still pending.

- Replacement UI snapshot `_build/polish-ui-diagnostic` passes peer UI remote task creation/removal and idle session expiry at 90.03 seconds (row stale, sidebar zero). Board tests now accept the Add repository page, List menu rename/delete prompts, Assistant settings labels, heading-based task selection and change-committed filters. Actual add/delete migration passes; state reordering is absent.
- Both graph modes pass real ancestry/selection/filter/zoom/timestamp-spacing and mobile inspector checks after accepting circle-role buttons. Only board document overflow remains there. Evidence `_build/polish-graph-ready.log`, `_build/polish-graph-irregular.log`.
- Overflow is caused by visually-hidden absolute move labels whose containing block escapes the board scroller. An isolated browser experiment temporarily set card-actions position relative: desktop 1525 -> 1440 -> restored1525; mobile1245 ->390 ->restored1245. Source remained untouched, and verifiers retain the original failure. Evidence `_build/polish-overflow-diagnosis/*position-hypothesis.json`.
- Generation completed; native lifecycle68694 is running. Final retained source `_build/polish-final-diagnostic` differs from the tested UI snapshot only in explicit named form access in dialogs.js and test metadata, plus new README/BOM/spec-map. The previous missing Hono peer dependency edge is present. Pending product repairs are hidden-label containment and real workflow reorder controls; native admission alone will not establish product completion.

- Run68694 terminated2 at independent readiness. The authored acceptance process arguments were empty, while LitAI probes an allocated ephemeral port; the generated server correctly used its default8765. Corrected the contract to pass --host127.0.0.1 --port{port}. A real launch of the retained packaged artifact with those expanded arguments returned health status ok and root HTTP200; evidence `_build/polish-packaged-launch.json`. This was acceptance configuration error, not evidence of a broken server.
- Added concrete hidden absolute-label containment and visible workflow reorder scenarios to quality.md. Lock/review/plan passed; read back acceptance binding sha256:f598058f5d7ec702c69da15db0c32d6b3ebcfd54650ce355a51a2e3356f318e6 and port arguments before starting replacement session30297/PID83930. Explicit Claude Code model claude-fable-5-1; logs `_build/tracker-final-ui-rebuild.log`, `_build/tracker-final-ui.debug.jsonl`.
- The final retained candidate also passes empty/truncated-history UI at both widths (`_build/polish-git-states/result.json`). Its labelled boundary circle and text are valid alternatives to a separate truncated badge. Backend native/admission and full product completion remain distinct.

- Expanded browser task-dialog coverage against final retained polish source: desktop/mobile edits to assignee, branch, due date, cover, priority, labels, dependency selection and completed checklist item persist through page reload while preserving description/state. Both pass in `_build/polish-attributes.log`; known workflow-reorder and overflow failures remain. Added this scenario to the full board checker.

- Extended the real reporter fixture across a backend outage: stop the service for 22 seconds (crossing its 20-second heartbeat), assert reporter and actual child PID remain alive, restart the service, release the child and verify stopped. The full independent service suite passes against final polish source in `_build/polish-reporter-outage.log`. This is an isolated fixture, not a production outage.

- New generation snapshot `_build/final-ui-backend-diagnostic` (45af53adee2cf0b3) passes all44 generated cases. Expanded backend diagnostics pass except `mac_outage_status`: existing MAC writes during an upstream503 are surfaced as502/mac_rejected, contrary to the explicit503 contract. Unknown-repository writes remain503 and no local shadow task is created; evidence `_build/final-ui-backend-containment.log`. Keep this failure until the final source is checked.
- The bounded-history checker now derives truncation from the real1,005-commit repository and preserved outside-window parents; optional `truncated` metadata, when present, must still be true. It no longer requires an undocumented response field.
- Added actual board wheel-scroll verification, including document bounds at the rightmost list. It reproduces the retained polish candidate's overflow at both widths (`_build/polish-scroll/*board-scroll.json`); no injected style is part of this verifier.
- Strengthened MAC transition verification to prove a successful upstream in_progress move and an attempted upstream-rejected completed transition, using the advertised state IDs. Both pass against final polish source with the rest of the expanded service suite (`_build/polish-mac-transitions.log`).
- Active generation has explicit card-action positioning and left/right list controls in source; browser confirmation is pending its web/app.js. Do not treat these source observations as a passing UI result.


- Run30297 terminated with standard_rebuild.project_changed after the service acceptance launch. Documentation was edited and its review marker refreshed during generation; this invalidated the frozen project authority. This is an operator sequencing error, not product admission. Future runs freeze all tracked files until terminal.
- Retained final-ui source passes44 native cases, peer UI registration/remote task creation/removal, desktop/mobile task attributes, rapid moves, drag, SSE, filtering, rename and actual add/reorder/reload/delete migration, inspector and settings. Session idle expiry passes at95.39 seconds; empty/truncated Git browser views pass both widths. Evidence `_build/final-ui-board-ready2`, `_build/final-ui-peer-ready`, `_build/final-ui-expiry`, `_build/final-ui-git-states`.
- Remaining demonstrated product failures are matched MAC outage status502 instead of503 and document overflow1657/1440 and1167/390. Hidden absolute labels on newly introduced list-move buttons escape the board scroller; card labels were fixed. Added concrete requirements for all control labels and upstream5xx classification. Browser selector updates preserve behavioral assertions and support labelled custom workflow dialogs and Back to board navigation.

- Current graph verification exposed an additional product defect: parseRefs uses for-each-ref %x1f literals then splits unit-separator bytes, discarding all refs. A real host Git invocation confirms literal %x1f output. Added command-specific delimiter and real branch-filter requirements; graph ancestry alone does not establish a working branch view. Evidence `_build/final-ui-graph-ready2.log` and retained lib/git.js.


- Run76435/PID92290 finished at persistent-service readiness with no such column: message_id. The fixed acceptance data directory contained an earlier candidate's schema. Tracked-file SHA256 audit shows no authority drift. Preserve that fixture and bind a fresh unique acceptance data directory before the next run. This is isolated acceptance data, not a user database.
- Retained final source `_build/contained-final-diagnostic` changes main.js to lazy mode imports; backend/UI source is identical to the tested snapshot. Full desktop/mobile board suite passes all interactions and viewport containment; peer UI, passive expiry95.11 seconds and empty/truncated Git views pass. Graph/timeline interactions and proportional timestamps pass while retaining the missing PID failure.
- Remaining product defects: only occupied upstream task states are installed, preventing in_progress/completed MAC transitions from open-only projects; Fleet omits actual PID; timeline inspector displays Lane undefined. Added concrete regression requirements. Backend outage503 and real Git refs are repaired.
- Promoted diagnostic checker adaptations for symbolic task-state keys, display names, custom workflow dialogs, role-based peer dialog closing, visible origin prefixes and graph inspector alternatives. State representation is inferred from an actual created task instead of assuming UUIDs or names. Keep native admission and final product proof distinct.

- Final lazy-import entrypoint repeats the full board pass at both widths and the backend passes except missing MAC lifecycle states. Graph tests retain explicit PID and undefined-inspector failures. Actual packaged artifact launches with a fresh disposable database, healthHTTP200/statusok and rootHTTP200: `_build/contained-packaged-launch.json`. This confirms the previous acceptance startup error was the reused fixture schema; it does not create an admission receipt.


### Scoped dependency and task editor follow-up

- The workflow/PID generation terminated before admission with a scoped npm BOM
  name mismatch. All tracked authority remained frozen throughout the run. The
  source used group plus basename while this installed adapter matches the full
  manifest name. Runtime authority now specifies full scoped names and canonical
  purls for every scoped dependency; no generated source or framework was patched.
- Independent backend checks pass, including the full MAC workflow and actual
  reporter outage survival. Graph/timeline, peer registration/message/removal,
  empty/truncated Git and board workflow/inspector/navigation checks pass. Board
  task attribute editing fails because Priority has no control. Added explicit
  create/edit/reload requirements; preserved the failing checker assertion.
- Generated direct Node tests pass 89 of 90. The failing effective-settings test
  correctly finds an environment-only LLM key usable but reported unconfigured.
  Added effective configuration projection and explicit-clear regression coverage.
- Browser checkers now recognize explicit Edit buttons, title-cased list labels,
  scoped generic Save, current mobile drawer labels, peer confirmation, and a
  cleared zero-session badge. These changes retain backend persistence, event,
  workflow migration, real-PID and expiry assertions.
- Evidence remains under `_build/workflow-pid-*`. No accepted artifact, public
  installation or completion claim exists. No remote forge is configured; the
  local worktree/branch survey found only this main worktree.

- Visual review found pale-on-white native task move selects. Stopped the next run
  during preflight (exit143, no generation child) to include dark control styling
  before spending another generation. The browser screenshot is retained at
  `_build/workflow-pid-board-final/desktop-board.png`.


### Native rebuild accepted; hidden dialog repair

- The editor/contrast rebuild completed successfully with no tracked authority
  drift. Exact result and artifact identity are retained in
  `_build/editor-contrast-native-result.json`. This is native lifecycle success,
  not a claim that the requested application is ready for delivery.
- The final service passed independent backend checks, including effective LLM
  settings, explicit key clear across restart, MAC transitions and rejection,
  official MCP/A2A, SQLite/SSE and actual coding-child outage survival. The native
  hook passed all 35 cases. The full scoped npm BOM passes reconciliation.
- Unmodified browser checks fail because the empty dialog root's display:flex
  overrides its hidden attribute and intercepts clicks. A clearly labelled,
  browser-only diagnostic override isolates that defect: board/task attributes,
  workflow lifecycle, inspector, Settings, peers, expiry and equal/irregular and
  empty/truncated Git views all work at the tested desktop/mobile widths. These
  probes do not count as acceptance and are never promoted into normal checkers.
- Added the hidden-dialog lifecycle requirement. Promoted only API and accessible
  selector compatibility fixes from the normal diagnostic checkers: key/name/id
  state inference, nested repository detail, current workflow/Settings/peer controls
  and branch clearing by label. Real persistence and protocol assertions remain.
- Regenerate through LitAI, then require all unmodified browser checks and the
  public launch path to pass before claiming the complete objective.


### Native acceptance and remaining rendered layout repairs

- The hidden-dialog rebuild finished with native acceptance and all 41 generated
  cases passing; exact result is `_build/hidden-native-result.json`. The final
  application files match the unmodified source used in independent browser tests.
- Backend persistence, SSE restart replay, MCP, A2A, actual child reporting and
  outage survival, MAC authority/transitions and effective LLM settings pass.
  All task editing, workflow lifecycle, live updates, inspector and settings
  interactions pass on desktop and mobile. Peer UI and real 90-second expiry pass.
- Three rendered failures remain: the narrow header puts Settings 23px outside a
  390px viewport; nearby unequal-time labels intercept timeline node clicks; a
  null-dated outside-window parent placeholder incorrectly suppresses all valid
  commits in a bounded timeline. The hidden overlay itself is fixed.
- Evidence: `_build/hidden-independent/summary.json`, `_build/hidden-board2`,
  `_build/hidden-graph2`, `_build/hidden-bounded-timeline`, and the per-file
  snapshot hashes in `_build/hidden-native2-provenance.json`. No styling override,
  forced clicks or generated-source changes were used for this acceptance audit.
- `visual.md` now specifies responsive header bounds, collision handling for nearby
  unequal timestamps and valid bounded-history timelines. Regenerate and require
  unmodified browser checks plus public launch verification before completion.
  Native test success alone does not fulfill the product goal.


### Final layout audit and remaining interaction repairs

- The layout rebuild passed LitAI native acceptance with 48 tests. The final
  unmodified source passes independent backend, peer UI, real session expiry,
  empty-history and bounded-history graph/timeline checks. The 390px header fits.
- Final board tests pass task creation/editing/all attributes, live updates,
  search, moves, rename, inspector, Activity and Settings. The list menu omits
  Delete, and the checkout-needed graph view omits navigation back to the board.
- Graph tests prove the first Zoom in leaves the small graph's actual circle
  diameter unchanged. Timeline clicks and timestamp spacing work, but label
  rectangles intersect adjacent node targets in both viewport sizes. Visible
  overlap is retained as failure even where later circles receive clicks.
- Evidence: `_build/layout-native-result.json`, `_build/layout-final-provenance.json`,
  `_build/layout-final-independent/summary.json`, and `_build/layout-final-graph4`.
  The latter corrects DOM-order assumptions and measures rendered geometry.
- Refined `visual.md` for visible workflow deletion/migration, navigation in
  diagnostic graph states, scaling the full fitted canvas, collision-free labels,
  and accurate branch-associated task/session annotations. Regenerate through
  LitAI and require the complete rendered and public-launch checks before delivery.

- The branch-association audit uses distinct main/feature tasks and an actual
  coding reporter child. It confirms the graph omits the active host annotation
  and the feature-filtered inspector incorrectly includes main-only tasks.
  `_build/layout-branch-audit` retains these results and screenshots. The next
  generation must implement these associations, not only the underlying API data.


### Runtime admission after passing interaction verification

- The interaction generation passes all seven independent phases: backend protocols,
  all board interactions at both viewport sizes, peer UI, real session expiry,
  empty/bounded history, equal-time and irregular-time graph checks. Workflow
  migration, zoom geometry, label spacing and real branch task/host associations
  now pass without generated-source edits or browser overrides.
- Evidence: `_build/interactions-independent/summary.json` is complete and passing;
  `_build/interactions-final-provenance.json` binds the final unmodified source.
  Final application code is unchanged from the complete-source test snapshot.
- Native rebuild exited with `dependencies.source-range-unresolved` because its
  SBOM declared generic Node only as a range. Runtime authority now requires the
  independently observed exact Node 22.23.2, alongside exact Git 2.50.1.
- Next action: rebuild with exact runtime metadata, require native admission and
  final artifact checks, then verify the supported build/run path before delivery.
  Independent test success does not stand in for native acceptance.


### Empty repository regression after runtime admission

- Exact-runtime generation passed LitAI native admission (19 tests); retain
  `_build/runtime-exact-native-result.json` and final per-file provenance.
- Independent backend checks found an empty-history regression: `git log --all`
  succeeds with no output on a newly initialized repository. The generated reader
  probes unborn HEAD only after a failed log command, returning state `ok` with no
  commits; both browser widths consequently omit the required empty-state message.
- Desktop/mobile board interactions, peer UI, real session expiry, and irregular
  timeline spacing/selection/zoom/branch associations pass. The timeline checker
  now waits for the exact selected full hash to avoid matching a previous parent.
- Next action: specify successful-empty-log behavior and an actual `git init`
  regression fixture, regenerate, then require final independent checks and the
  supported public build/run path. Native acceptance alone remains insufficient.


### Final interaction and configuration regressions

- The unborn-history generation passed native admission with 60 tests. Actual
  empty and bounded Git browser checks and real session expiry pass. The final
  source is retained in `_build/unborn-final-diagnostic` and bound by per-file
  `_build/unborn-final-provenance.json`; native result is `unborn-native-result.json`.
- Independent API checks reveal raw TRACKER_* environment variables passed to a
  settings helper expecting lowercase fields. Environment-only LLM and MAC fail;
  a separate stored-settings diagnostic proves their downstream integrations.
- Rendered sidebar Activity/Agents/Settings buttons have data-route attributes but
  no event handlers. Repeated workflow deletion then addition leaves duplicate
  positions. Zoom scales coordinates while commit circles remain 16px. These are
  product failures, not satisfied by native test success.
- Board rerun passes 12/13 desktop and 11/13 mobile interactions. Graph rerun
  confirms selection, real timestamp spacing and branch/host associations; only
  geometry zoom remains. Exact selected Hash-field waits avoid confusing parent
  hashes with the selected commit. Evidence: `_build/unborn-board2`,
  `_build/unborn-graph4`, `_build/unborn-independent/summary.json` and
  `_build/unborn-stored-settings2.log`. The MAC rejection status discrepancy also
  needs an explicit 4xx contract while retaining upstream detail and cache state.
- Visual comparison to the supplied Trello reference finds truncated list titles
  under permanent header controls and overly dense card controls. Preserve compact
  dark cards, colored labels/covers and legible list names in the repair.
- Next action: regenerate from the clarified configuration, workflow and visual
  authority; require all final independent checks and supported public launch.


### Physical host annotations in branch views

- The wiring generation passed native admission with 45 tests. Its backend
  diagnostics, all 13 desktop/mobile board interactions, peer UI, actual session
  expiry and empty/bounded-history views pass. Equal and irregular timestamp
  checks confirm real edges, selection, spacing, zoom and branch task filtering.
- Final frontend matches the tested snapshot. Both graph checks retain one
  failure: the graph API projection drops session hostname, and the branch panel
  renders only CLI/status. Fleet correctly shows the actual host and child PID.
  The required branch-to-physical-host association is therefore still incomplete.
- Evidence: `_build/wiring-native-result.json`, `_build/wiring-final-provenance.json`,
  `_build/wiring-board2`, `_build/wiring-peer2`, `_build/wiring-git-states2`,
  `_build/wiring-graph2` and `_build/wiring-graph-equal2`. Original fullsuite logs
  include selector failures corrected by these reruns. Late backend changes
  preserve local tasks during MAC discovery and correct entrypoint handling;
  `_build/wiring-final-backend.log` records their final-source verification.
- Next action: retain actual hostnames through the graph session projection and
  rendered selected-branch association, regenerate and require all final checks
  plus the supported public build/run path. Preserve the current passing behavior.


### Hostview final-source verification and list heading review

- Hostview generation at 5a236ef completed native admission with 57 tests. Preserve
  `_build/hostview-native-result.json` and the 35-file final source hashes in
  `_build/hostview-final-provenance.json`.
- Early snapshots discarded raw startup options; final generation corrected that
  before native completion. The final independent suite now runs the required
  raw --litai-serve command, with no JSON launch workaround. Its current evidence
  is `_build/hostview-final-independent` and `_build/hostview-final-verify.log`.
- Early JSON-launch diagnostics pass all seven behavior scopes after adapting
  observed contracts: expected_revision for conditional task edits, seq for SSE
  cursors, nested title buttons, Remove peer confirmation, and exact selected
  Hash-field waits. These adaptations preserve the original assertions.
- Actual reporter hostname associations now pass in graph/timeline checks. The
  additional final-source browser stale-editor probe shows an actionable error
  and preserves the concurrent saved title (`_build/hostview-extra-browser`).
- Visual inspection of desktop/mobile screenshots still shows short list headings
  such as in_progress crowded and truncated by four permanent action buttons.
  This contradicts the existing visual authority despite passing interactions.
- Next action in progress: finish final-source and additional browser review, then
  reinforce list-name layout acceptance in the component's visual authority and
  regenerate if final rendering retains the defect. Supported public build/run,
  current receipt and complete handoff remain pending.


### Additional hostview outage review

- All seven final-source independent phases pass (`_build/hostview-final-independent/summary.json`).
  Additional missing-checkout navigation and stale-editor conflict browser probes pass.
- The isolated unavailable-peer UI probe passes and records last_error after failure
  (`_build/hostview-peer-outage/result.json`). No external service was contacted.
- MAC outage browser probe rejects the edit and preserves upstream task state, but
  the already-open overview never shows the recorded backend sync_error. Runtime
  `_build/hostview-mac-outage/outage-state.json` shows the repository error while the
  page still has no indicator; sync-failure storage updates do not notify the UI.
- Include realtime MAC sync-status notification and recovery in the next specification
  repair, together with fully legible short list headings. Preserve cached tasks and
  upstream-only mutations throughout outage and recovery.

### Live-status final-source verification and MAC recovery repair

- Generation at efc644d completed native acceptance with 50 tests. Final34-file
  provenance is `_build/live-status-final-provenance.json`; native result is
  `_build/live-status-native-result.json`. Every application file matches the
  independently tested snapshot; final additions are tests and documentation.
- Six of seven independent phases pass in `_build/live-status-independent/summary.json`:
  board, peer UI, actual session expiry, empty/bounded Git, equal-time graph and
  irregular-time graph. All15 board checks pass at desktop1440/mobile390,
  including complete short list headings without clipping or overlapping actions.
- Additional stale-editor conflict and missing-checkout navigation probes pass.
- MAC outage now reaches already-open overview and inspector, but recovery does
  not. `_build/live-status-transition-confirm/recovery-failure.json` records API
  sync_error null while both views still show failure and only an outage event
  arrived. Repository discovery clears the error before transition detection.
- The service suite passes all other diagnostic phases, but new MAC task creation
  during an upstream503 returns tracker500. The MAC client's typed unavailable
  error bypasses the shared service error conversion on this path.
- Next action in progress: require status comparison across the complete sync
  transaction and consistent shared-service error normalization for MAC creation,
  editing and transitions; preserve the passing board/protocol/Git behavior and
  regenerate. Public build/run, receipt and complete handoff remain pending.

### MAC recovery final result and task-detail navigation repair

- Generation at315c519 completed native acceptance with52 tests. Final37-file
  hashes are `_build/mac-recovery-final-provenance.json`; native result is
  `_build/mac-recovery-native-result.json`. Service and frontend files match the
  independently tested31-file snapshot. The only existing-file change is the
  diagnostic A2A operation projection; final additions are tests and metadata.
- `_build/mac-recovery-backend2.log` passes the complete independent backend
  suite, including MAC creation/edit/transition outage routing and reporter
  survival. `_build/mac-recovery-status2/result.json` proves already-open overview
  and inspector update through healthy503healthy without reload, cached task
  changes, shadow writes or duplicate events on unchanged polls.
- All15 board interactions pass at desktop1440/mobile390. Dependency selection
  works, but the select has only aria-describedby and no accessible name. The
  board checker retains this failure while testing the remaining attributes.
- Peer UI, actual session expiry, empty/bounded Git and both graph timing fixtures
  pass their existing behaviors. Graph/Timeline related tasks remain plain text;
  `_build/mac-recovery-graph2` and `_build/mac-recovery-irregular2` fail solely the
  required actionable related-task links at both viewports.
- Next action in progress: require related-task controls to open the actual task
  editor from Graph and Timeline, and associate the dependency selector with a
  real accessible label. Preserve the verified MAC recovery and all existing
  behavior, regenerate, then complete public build/run and handoff verification.

### Delivery verification and complete timeline label bounds

- The c49ded4 delivery completed native acceptance (26 tests) and exported a
  runnable artifact. The final independent backend suite passes, including MAC
  recovery, official SDK clients and reporter survival across backend outage.
- Desktop and mobile board interactions, dependency naming, actionable related
  tasks, peer UI, session expiry and bounded Git history pass. The equal-time
  timeline still has a merge label crossing its neighboring commit target at
  both widths; the irregular-time fixture passes. Full source provenance and
  evidence are retained under `_build/delivery-final-provenance.json` and
  `_build/delivery-independent`.
- The public default `litai run` launcher returned ready from `/health`, loaded
  the application and opened Settings in Chrome. This proves the launch path;
  the timeline defect still prevents complete acceptance.
- Next action in progress: clarify that collision bounds include the complete
  composed hash, subject and ref suffix, regenerate with receipt creation in
  the same lifecycle, then repeat full acceptance and public launch verification.

### Timeline bounds result and protected browser login

- Generation at 10201b0 completed with 38 native tests. Final provenance is
  `_build/label-bounds-final-provenance.json`; the native result is
  `_build/label-bounds-native-result.json`. All eight final-source phases pass;
  `_build/label-bounds-git2` supersedes the original hash-label parsing mismatch.
  Additional conflict, missing-checkout and unavailable-peer probes also pass.
- The preserved frontend passes all15 board interactions at desktop1440/mobile390,
  both graph timing fixtures including collisions after Zoom/Reset, and MAC
  outage/recovery and authenticated peer UI checks. Final frontend bytes match.
- A token-protected browser opens a generic authentication error with no password
  input or login control. Direct same-origin POST to the login API creates the
  correct HttpOnly SameSite cookie and permits the overview, proving that the
  missing piece is the browser login flow. The exact final source was tested;
  evidence is `_build/label-bounds-login/result.json` and `before-login.png`.
- Next action in progress: finish the remaining final-source audit and require an
  accessible browser login form with invalid-token feedback, session reuse and
  recovery from an expired session. Preserve the verified board, Git and protocol
  behavior. Use the supported receipt-updating `build` command for the next
  generation so it also creates the public run export; `rebuild` produced a
  receipt and retained artifact but did not update that export.
