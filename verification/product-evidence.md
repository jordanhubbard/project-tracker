# Product completion evidence

The latest tested candidate is retained at `_build/ui-final-diagnostic`. It is
**not an admitted artifact**: native validation rejected a missing resolved peer
edge in its source BOM. Earlier Fable observations remain historical evidence;
passing checks must be repeated on the artifact ultimately delivered.
The active regeneration is recorded in `_build/active-run.json`.

Current review: board creation/edit/move, workflow lifecycle, live task edits,
inspector saves and Settings pass at desktop/mobile. Board document widths are
1526/1440 and 1299/390, so layout still fails. Service checks pass except checkout
symlink identity, which creates a duplicate repository. Expiry remains active at
110 seconds. Peer registration succeeds but opening the message dialog throws
`Illegal invocation`. Graph selection/filter/zoom and timestamp-proportional placement pass after
waiting for asynchronous rendering. Mobile inspector overflow is confirmed.
Empty Git history and detached HEAD pass API checks. Visual comparison finds
poor contrast in the pale task-move controls; final visual acceptance remains open. These results supersede the older candidate
rows below where noted. Evidence: `_build/ui-final-browser.log`,
`_build/ui-service-alias.log`, `_build/ui-expiry-browser/result.json`,
`_build/ui-final-peer/page-errors.json`, `_build/ui-final-graph-ready.log`.

| Requirement | Current evidence | Remaining work |
| --- | --- | --- |
| LitAI project and native build | Authoritative Component, flavors and lock; native npm build and 33 generated tests passed | Current lifecycle acceptance, committed receipt and reusable admitted source |
| Repository overview and inspector | UI first-repository registration, origin display and description persistence pass | Repeat on final artifact |
| Task attributes and SQLite persistence | Independent API roundtrip/restart covers title, description, state, labels, checklist, assignee, branch, cover, due date and dependencies; cycle and stale revision rejected | Repeat on final artifact |
| Trello-style board | Rendered dark columns/cards, covers and horizontal board; create, search, desktop drag and settled mobile move pass | Rapid edit/save/move fails on stale revision; final reference comparison |
| Editable workflow | Browser rename/add/reorder/delete with task migration pass at desktop/mobile | Repeat on final artifact |
| Live task changes | Creation and title/description-update delivery plus durable SSE replay pass | Final invalidation/routing consistency |
| Actual coding sessions by host | Real reporter child PID, hostname, CLI, branch and stopped lifecycle pass in API; same real PID appears in Fleet | Live stopped/expired state and overview counts in browser |
| Git timeline and relationship graph | Real fork/merge parents; equal and unequal timestamp SVG layouts; selected hashes before/after filter; zoom and visible mobile inspector pass | Repeat on final artifact; review empty/error/truncated history states |
| MAC authority and local fallback | Discovery, canonical SSH equivalence, metadata import, stable polling, all-protocol fleet writes, lifecycle rejection, confirmed absence and outage containment pass | Final artifact and configured-fleet setup review |
| Official MCP | Official HTTP and stdio SDK clients create/read tasks; stdio waits boundedly for MAC readiness | Repeat on final artifact |
| A2A peering | Durable task IDs, retry idempotency, two-process authenticated forwarding and token redaction pass | Peer UI currently offers sender IDs instead of receiver IDs |
| Backend LLM configuration | Mock gateway prefix/auth/context and redaction pass; desktop settings save/reload passes | Mobile Settings control currently hidden |
| Public runnable application | Diagnostic source runs locally in isolated fixtures | `litai build --from-accepted-source`, actual `litai run`, health and browser verification |

Diagnostic logs and screenshots are indexed in `docs/roadmap/active-work.md`.
`check_all.py` runs the independent product suite and does not issue a LitAI receipt.
No production MAC fleet writes, external repository publication or release is required
for this local project task.
