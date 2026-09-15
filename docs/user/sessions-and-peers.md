# Physical sessions and peers

[Documentation](../README.md)

## Report a coding CLI session

Run the reporter on the physical host where the coding CLI executes. It launches the
actual child with inherited terminal input/output and reports hostname, PID, checkout,
branch and CLI identity to the backend. It does not require database access on that host.

```sh
export TRACKER_URL=http://127.0.0.1:8765
./scripts/litai-service.sh run components/tracker '["service","session","--repo","/absolute/repo/path","--cli","codex","--","codex"]'
```

Configure `TRACKER_ACCESS_TOKEN` in the reporter's environment when the backend is
protected. Keep credentials out of command arguments. The executable after `--` must
already be installed on the reporting host. The CLI label identifies the frontend;
it does not independently prove which model a provider router selected.

Reporter labels include `codex`, `claude`, `cursor`, `opencode`, and `other`. The reporter
sends a heartbeat about every 20 seconds and reports stopped status when the child exits.
A backend outage does not terminate the coding child.

| Status | Evidence |
| --- | --- |
| Active | Running status and a heartbeat received within 90 seconds |
| Stale | Heartbeat freshness expired |
| Stopped | The reporter explicitly recorded child exit |

A MAC agent assignment or machine heartbeat alone is not proof of an active coding CLI
process. Fleet displays those facts separately. Reporter activity also appears in repository
counts and branch associations in Graph and Timeline.

The reporter is a foreground wrapper. No login agent, remote installation or fleet-wide
service registration is performed by these instructions.

## Connect another tracker

In **Agents & peers**, register the receiving instance's base URL and, if required,
its access token. Registration fetches and validates the peer's agent card. Credentials
are stored on the sending backend and omitted from browser responses and message history.

Use a repository ID belonging to the receiving tracker when sending a task request.
Repository IDs and task IDs are instance-local; do not substitute a MAC ID or a sender's
local repository ID. Peer failures display an error while retaining history.

The outgoing API accepts a complete A2A message under `message`. Reusing its `messageId`
retries the same operation and returns its durable A2A task rather than creating another
board task. Completed synchronous operations cannot be cancelled.

See [API examples](../reference/api.md#a2a-and-peers) for the wire format and the difference
between A2A protocol task IDs and board task IDs. The declared A2A version is 0.3.0.
