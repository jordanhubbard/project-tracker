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
| Default deadline | Real exported service, stalled HTTP 200 body, rejection and socket cleanup before 65 seconds, process survival and recovery |
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

Later candidates exposed additional defects. Each result applies only to the source
and checks identified in its evidence file; none establishes current final acceptance.

| Candidate evidence | Main finding |
| --- | --- |
| [3](../../verification/track004-candidate3.json) | 46 native tests passed; independent checks found dependency-edit and Git branch/filename-collision failures. |
| [4](../../verification/track004-candidate4.json) | MAC lifecycle states were not preserved completely. |
| [5](../../verification/track004-candidate5.json) | Timeout cleanup and write/poll projection stability failed. |
| [6](../../verification/track004-candidate6.json) | Dependency-only changes did not advance the revision or publish task events. |
| [7](../../verification/track004-candidate7.json) | Focused event checks passed; response cleanup crashed and the native run exceeded its process budget. |
| [8](../../verification/track004-candidate8.json) | The timeout rejected the caller but left the response socket open. |
| [9](../../verification/track004-candidate9.json) | Deadline cleanup passed; a 48 MiB response limit rejected the real 77 MiB task collection. |
| [10](../../verification/track004-candidate10.json) | Full HTTP import and several service/browser checks passed; first-poll foreign references, response-volume fixture sizing, and populated-state rename failed. |
| [11](../../verification/track004-candidate11.json) | Foreign references, state rename, HTTP writes, and documentation examples passed focused checks; removed-project tasks remained cached and the native rollback assertion used an incorrect event baseline. |

Candidate [12](../../verification/track004-candidate12.json) passes focused removal,
rollback, full-response import, dependency/event and workflow checks. Its actual service
also passes lifecycle, default-timeout, HTTP-write, protocol and documentation-example
checks. The native MAC diagnostic still fails because it requires an unchanged
`dependencies` field in an outgoing update, although the upstream and cached edges
remain intact. The next generation clarifies that preservation is verified from the
resulting task state while checking every dependency ID that is actually transmitted.
Final exported-artifact acceptance remains pending.

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

Candidate thirteen passed eight of nine native MAC groups. Its serialized-read
assertion considered only newly accepted sockets and missed keep-alive reuse. A
separate actual-client probe confirmed the exact reused socket closed at the short
deadline before fixture cleanup and a healthy follow-up succeeded. The lifecycle
rejected this candidate; final acceptance remains pending. See
[candidate-thirteen evidence](../../verification/track004-candidate13.json).

Candidate [15](../../verification/track004-candidate15.json) passed the supported
native build after reviewing and rebinding the service acceptance contract. Its
native npm archive passed exact file verification, installation, native/service
checks and byte-for-byte download verification from an unpublished GitHub draft.
Two browser defects remain: a stale render reopens the registration dialog and a
status toast intercepts mobile Settings clicks. Stable release acceptance is pending.
