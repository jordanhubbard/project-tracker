# Verification and delivery status

[Documentation](../README.md)

The workspace is persisted on GitHub `main` through
[PR #1](https://github.com/jordanhubbard/project-tracker/pull/1), merge
`f455508a85b487d9290375993fec16420a93763f`. The MAC repair is tracked in
[PR #2](https://github.com/jordanhubbard/project-tracker/pull/2) and
[TRACK-004](../roadmap/active-work.md). Documentation completion is TRACK-006.

**Current MAC repair acceptance is pending.** Source publication does not establish
that every integration and failure-recovery gate has passed. Do not infer acceptance
from the presence of an older export or a healthy HTTP listener.

## Evidence layers

| Layer | Required proof |
| --- | --- |
| Authored project | Valid specifications, lock/plan and reviewed documentation |
| Native lifecycle | Exact dependencies, generated native tests, service acceptance and framework receipt |
| Independent backend | REST, persistence, revision conflicts, official MCP clients, A2A, peers, LLM redaction and real reporters |
| Browser | Desktop 1440px and mobile 390px, task/workflow interactions, login, live status, Git and no overflow |
| Fleet reconciliation | Complete saved snapshot IDs, fields, states and dependencies; atomic rollback and unchanged polls |
| Mutations | Synthetic authenticated MAC create/edit/transition, unresolved references, long text and outage handling |
| Default deadline | Real exported service, stalled HTTP200 body, rejection and socket cleanup before65 seconds, process survival and recovery |
| Live MAC | Isolated GET-only synchronization, stable upstream/task comparison and rendered tasks |
| Portable delivery | Supported committed-source publication and fresh GitHub checkout cache reuse/current acceptance |

The native suite uses a short deadline for its incomplete-body regression because the
installed packaged runner has a fixed 60-second total process budget. The separate default
60-second service test remains mandatory. A timer firing, a shortened test, or a fixture
watchdog closing the socket does not satisfy the full default-budget gate.

## Retained candidate history

The earlier `artifact-6119bda93ad771d2ed03` passed 28 native tests and nine independent
phases against isolated fixtures. A later live audit exposed incomplete fleet import.
Those historical passes establish their original scope, not current complete MAC readiness.

Candidate `7a1f3cd0aa4d08717013` passed 46 native tests and substantial fleet checks, but
independent checks found dependency-edit and branch/filename-collision failures. Later
candidates exposed state preservation, timeout cleanup, projection stability and event
revision regressions. Their sanitized results are retained in
[candidate three](../../verification/track004-candidate3.json),
[candidate four](../../verification/track004-candidate4.json),
[candidate five](../../verification/track004-candidate5.json),
[candidate six](../../verification/track004-candidate6.json), and
[candidate seven](../../verification/track004-candidate7.json), and
[candidate eight](../../verification/track004-candidate8.json), and
[candidate nine](../../verification/track004-candidate9.json).

Candidate seven's focused dependency-only and combined-change probes pass, but its
response-body cleanup produces an unhandled rejection. Its native run also exceeded the
framework's 60-second limit. Neither a provisional pass nor an interrupted generation
constitutes final artifact acceptance. Candidate eight prevents the cleanup crash
but leaves the original response socket open beyond the allowed deadline; it was
stopped before acceptance. The next repair explicitly owns and destroys transport
request/response handles. Candidate nine fixes the deadline and connection cleanup,
and passes the focused event and adapter snapshot checks, but its48MiB response cap
rejects the real77MiB task collection. Full response-volume coverage is now required.

`verification/current.json` is framework-owned and must match current authority.
[final-result.json](../../verification/final-result.json) records the artifact it was
written for; inspect that identity before relying on it. Temporary logs and raw fixture
captures stay in ignored `_build/`, while public evidence contains sanitized aggregates.

## Scope limits

Synthetic fixtures perform all automated writes. The live MAC checks use an isolated
tracker and read-only upstream access. No production task mutation, fleet installation,
background-service registration, packaged release or non-macOS validation is claimed.

No GitHub Actions application-build workflow is configured in this workspace. Inspect
actual PR checks separately; a secret scan is not a runtime test matrix.

Run instructions and independent checks are in [development](development.md) and
[test matrix](test-matrix.md). Work closes only after its required final-artifact evidence
is recorded and the corresponding change is actually merged.
