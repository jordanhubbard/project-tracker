# Troubleshooting

[Documentation](../README.md)

| Symptom | Check and action |
| --- | --- |
| Lifecycle wrapper rejects Node or Git | Compare the installed versions with `components/tracker/runtime.md`; use the declared toolchain or deliberately update runtime authority and regenerate |
| `litai` or the coding CLI is unavailable | Install/configure the selected operator tooling; use `litai doctor` and the provider's own authentication flow |
| Generation is taking a long time | Inspect the lifecycle process and log; generation is not an ordinary compile, and empty buffered output alone is not evidence of a hang |
| Failed build but an application still launches | An earlier export may remain; compare the artifact and receipt with the current verification record |
| Browser asks for a token | Enter the configured backend access token in Sign in; never put it in the URL |
| API returns 401 | Supply the backend bearer token, not the MAC or LLM credential |
| Browser works but MAC tasks are missing | Inspect sync status, authority, API URL and both project/registry discovery; compare complete paginated collections |
| New repository is unresolved | A configured fleet has not completed discovery; restore it before treating the repository as absent |
| Cached MAC tasks remain during an outage | Expected behavior; restore upstream access rather than recreating them locally |
| Save returns 409 | Fetch the latest task and reconcile the draft with its current revision |
| Move is rejected | MAC lifecycle rules still apply; inspect the rejection instead of retrying a local-only state name |
| A dependency is unresolved | The target is missing from the snapshot or belongs to another project; retain it unless you intend explicit removal |
| Graph requests a checkout | Set a path on the backend host; a path on the browser's computer is insufficient |
| Graph is empty | Distinguish an unborn repository from a missing path, bad branch or Git error |
| Fleet shows no active coding session | Start the reporter around the actual CLI on its physical host; agent assignment alone does not create a session |
| Session is stale | Check reporter connectivity and heartbeat age; active status expires after 90 seconds |
| Assistant is unavailable | Check the saved gateway prefix/model/key and its connection result; core task work remains available |
| Peer task goes to the wrong project or fails | Use a repository ID from the receiving instance and its valid peer token |

## Useful diagnostics

From the repository root:

```sh
litai doctor
./scripts/litai-service.sh project validate
./scripts/litai-service.sh verify
curl --fail http://127.0.0.1:8765/health
```

`project validate` checks authored authority and documentation. `verify` evaluates the
declared gates and receipt. Neither a stale historical result nor HTTP readiness alone
proves current MAC integration. Read [verification](verification.md) for exact scope.

For a bug report, include the Git revision, artifact identity, command, expected and
observed behavior, and a small synthetic reproduction. Strip credentials, private
hostnames and production task content. Keep original failed reports when a corrected
probe or candidate is tested; a later pass does not erase the earlier failure.
