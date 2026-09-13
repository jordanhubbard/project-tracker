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
- In progress: LitAI source generation and build. Inspect `_build/tracker-rebuild.log` and the live process before deciding whether to resume or retry. No runnable app is claimed.
- Chrome headless automation was launched successfully from isolated `_build/browser-qa`; product browser checks remain pending.
- No Git remote is configured; LitAI tracker/peer survey reported unsupported forge and skipped remote reconciliation.
- After the build, verify all product requirements, protocol clients and Trello visual fidelity; the initial service probes alone do not prove the whole goal.
