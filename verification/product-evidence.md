# Product completion evidence

The latest tested candidate is the retained final Fable source in
`_build/fable-final-diagnostic`. It is **not an admitted artifact**. The active
replacement is tracked in `_build/active-run.json`. Passing observations below must
be repeated on the artifact that is ultimately delivered.

| Requirement | Current evidence | Remaining work |
| --- | --- | --- |
| LitAI project and native build | Authoritative Component, flavors and lock; native npm build and 33 generated tests passed | Current lifecycle acceptance, committed receipt and reusable admitted source |
| Repository overview and inspector | Browser origin display and description persistence pass at desktop/mobile | Final artifact review; UI repository registration |
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
