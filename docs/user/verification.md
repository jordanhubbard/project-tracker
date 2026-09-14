# Product completion evidence

The application is built and verified locally on macOS. Authority commit
`e09a08c` produced `artifact-6119bda93ad771d2ed03` through the supported
`build --update-receipt` lifecycle. The final source is exported under
`generated/artifacts/tracker/`; `verification/current.json` is the framework-owned
receipt. [final-result.json](../../verification/final-result.json) records source hashes and evidence.

| Requirement | Final-artifact evidence |
| --- | --- |
| LitAI build, dependencies and receipt | 28 native tests passed; authority, lock and receipt verification passed |
| Repository overview, registration and inspector | Browser registration, metadata editing, counts and authority display passed |
| Trello-style board | Desktop 1440px and mobile 390px screenshots reviewed; dark sidebar, horizontal lists, cards, colored covers and readable controls |
| Task detail and editable workflow | All 15 interactions passed at both widths: all task attributes, priority, dependencies, checklist, drag/accessible move, list rename/add/reorder/delete and migration |
| Realtime tasks and durability | Second-client create/edit, SQLite restart, SSE replay and optimistic revision rejection passed |
| Physical coding sessions | Real child hostname/PID/CLI/branch, stopped status, actual heartbeat expiry, graph associations and child survival through backend outage passed |
| Git DAG and timeline | Real fork/merge edges and refs, proportional irregular timestamps, equal-time layout, selection, zoom/reset, branch filtering and related-task editing passed at both widths |
| Mobile chart sizing | Selected-inspector Timeline viewport measured 240px client height; real node clicks passed |
| Missing/empty/bounded Git | Missing checkout feedback/navigation, empty history and 500 loaded commits from a 1005-commit repository with genuine boundary context passed |
| MAC authority | Authenticated discovery, canonical matching, task mutation through REST/MCP/A2A, metadata preservation, genuine rejection, confirmed absence and outage without shadow local writes passed |
| Live MAC status | Already-open overview and inspector update on outage/recovery without task changes, shadow writes or duplicate status events |
| Official MCP | Actual SDK clients initialized and read/mutated through HTTP and stdio |
| A2A peering | Durable task state, retry idempotency, terminal cancellation rejection, authenticated peer UI messaging/removal and unavailable-peer feedback passed |
| Backend LLM settings | Gateway path/model/context/auth, redaction, UI persistence, blank credential preservation and explicit clearing without environment fallback passed |
| Browser authentication | Visible valid/invalid login, HttpOnly SameSite session, reload/session-loss recovery, denied unauthenticated data/events and cross-origin login, no token in URL/storage/text |
| Public launcher | Supported `litai run` export returned healthy, signed in through Chrome, connected events and opened Settings |

The independent suite is `_build/mobile-canvas-independent`. Its first bounded-Git
probe used the prior renderer's control/name representation; the corrected probe
passed in `_build/mobile-canvas-git3`, preserving every loaded-commit, boundary and
uniqueness assertion. Both logs remain available. The consolidated result references
the passing rerun rather than rewriting the original failure.

Extra final-source evidence is retained under `_build/mobile-canvas-conflict`,
`_build/mobile-canvas-missing-path`, `_build/mobile-canvas-peer-outage`, and
`_build/mobile-canvas-public`. The temporary public-launch instance was stopped
following verification. Use the [run instructions](getting-started.md#current-availability) to start it.

These checks used isolated databases, authenticated MAC contract fixtures, a local
LLM gateway fixture, actual Git repositories and physical child processes. They
prove this local application; they do not claim production fleet deployment,
remote publication, background-service registration, or validation on other host
platforms. Those actions are outside the requested local implementation.
