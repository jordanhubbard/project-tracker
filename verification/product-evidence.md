# Product completion evidence

Current checkpoint: exact-runtime generation passed native admission with 19 tests
(`_build/runtime-exact-native-result.json`). Independent checks retain a real
empty-repository defect: successful `git log --all` with empty output incorrectly
produces state `ok` and no visible empty-history message. Board interactions at
both widths, peer UI, real expiry and irregular timeline checks pass. The final
unmodified source is bound by `_build/runtime-exact-final-provenance.json`.
Regeneration with the explicit empty-history fixture, complete final checks and
public launch remain pending. See the latest [active work](../docs/roadmap/active-work.md).
Earlier sections below are historical evidence and do not claim delivery.


The latest complete retained source is `_build/contained-final-diagnostic`.
It is not an admitted or delivered application. LitAI run76435 finished with a
persistent-service readiness failure: the acceptance fixture reused an older
candidate's SQLite database and startup reported a missing message_id column.
Tracked authority remained unchanged throughout that run. Preserve the old fixture
and use a new disposable acceptance directory for each replacement generation.

| Requirement | Current evidence | Remaining work |
| --- | --- | --- |
| LitAI build/admission | Dependency and native stages reached packaged service acceptance | Fresh acceptance fixture, successful admission and current receipt |
| Repository overview/inspector | Registration, origin and description save pass | Final artifact repeat |
| Task attributes/SQLite | API restart durability and complete desktop/mobile edits pass | Final artifact repeat |
| Trello board | Dark rail/lists/cards/covers visually reviewed; dimensions and rightmost-list scrolling pass at1440/390 | Final artifact review |
| Workflow editing | Rename, add, reorder, reload and populated deletion migration pass | Final artifact repeat |
| Live task activity | Second-client create/edit and durable SSE replay pass | Final artifact repeat |
| Physical coding sessions | Actual child PID/host/CLI/branch stored; reporter survives backend outage and stops | Fleet row omits PID |
| Session expiry | Passive stale status/sidebar zero at95.11 seconds | Final artifact repeat |
| Checkout identity | Realpath/symlink identity passes | Final artifact repeat |
| Git graph/timeline | Real refs/parent edges, branch filter, selection, zoom, proportional time and mobile inspector pass | Timeline inspector prints Lane undefined |
| Empty/truncated Git | Both widths pass empty state and reachable outside-window parent marker | Final artifact repeat |
| MAC authority | Discovery, stable import, metadata preservation, absence/outage separation and503/no shadow tasks pass | Workflow omits unoccupied in_progress/completed states, preventing transitions |
| Official MCP | Official HTTP and stdio SDK client roundtrips pass | Final artifact repeat |
| A2A peers | Durable tasks/retries, authenticated forwarding and peer UI create/remove pass | Final artifact repeat |
| LLM settings | Gateway prefix/auth/context, UI persistence and secret redaction pass | Final artifact repeat |
| Public launch | Retained source executes in isolated test processes | Accepted-source build, actual public litai run and final health/browser checks |

Evidence: `_build/contained-backend-ready2.log`, `_build/contained-board-ready2`,
`_build/contained-peer-ready`, `_build/contained-expiry`, `_build/contained-git-states`,
`_build/contained-graph-ready3` and `_build/contained-graph-irregular2`.
Final source changed main.js to lazy imports, plus README/test manifest/BOM/spec map;
backend and UI implementations match the tested earlier snapshot. Recheck entrypoint
behavior before transferring execution claims to the final artifact.

Checker adaptations support stable symbolic task-state keys with separate workflow
IDs and display names, custom role dialogs and equivalent accessible controls.
They preserve failure for unavailable MAC transitions and missing Fleet PID.
The independent suite never creates a LitAI receipt. No production MAC writes,
external publication or fleet-wide installation is required for this task.
