# API and protocol reference

[Documentation](../README.md)

The running service publishes REST schemas at `/openapi.json`, MCP tools through the
official SDK, and its A2A card at `/.well-known/agent-card.json`. Use those runtime
schemas for exact optional fields and collection pagination. All task interfaces call
the same authority-aware service.

## Authentication and IDs

Protected HTTP clients send `Authorization: Bearer TOKEN`, using the backend access
token. The browser uses its same-origin session cookie. MAC, LLM and peer credentials
are different secrets and are never substitutes for the backend token.

Repository and task IDs come from Tracker responses. `mac_id` identifies an upstream
task where present. An A2A task ID identifies a protocol operation, not a board task.
When sending to a peer, use repository IDs belonging to that receiving instance.

## REST routes

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Service readiness, separate from complete MAC acceptance |
| `GET /openapi.json` | REST contract |
| `GET /api/repos` | Paginated repositories |
| `POST /api/repos` | Register a repository |
| `GET /api/repos/{id}` | Repository detail |
| `PATCH /api/repos/{id}` | Edit repository metadata |
| `GET /api/repos/{id}/tasks` | Paginated tasks for a repository |
| `POST /api/repos/{id}/tasks` | Create a task through its authority |
| `GET /api/tasks/{id}` | Complete task detail |
| `PATCH /api/tasks/{id}` | Edit fields/state using the current revision |
| `DELETE /api/tasks/{id}` | Request deletion subject to the task authority's rules |
| `GET /api/repos/{id}/states` | Workflow states |
| `PUT /api/repos/{id}/states` | Update workflow with explicit migration for deleted nonempty states |
| `GET /api/repos/{id}/graph` | Bounded real Git history, refs and associations |
| `POST /api/sessions/heartbeat` | Report a physical coding session |
| `GET /api/sessions` | Sessions and derived freshness |
| `GET /api/events` | Durable server-sent event stream |
| `GET /api/settings` | Public settings and credential-configured booleans |
| `POST /api/assistant` | Ask the configured backend gateway with repository context |
| `GET /api/peers` | Registered peers |
| `POST /api/peers` | Register and validate a peer |
| `DELETE /api/peers/{id}` | Remove a peer |
| `POST /api/peers/{id}/messages` | Send a complete A2A message through stored peer credentials |

Use the served OpenAPI document for the current settings-write method and full workflow
payload. A collection response may omit upstream detail; fetch task detail when auditing
MAC IDs and unresolved references. Do not assume the first collection page is complete.

## Example: create and edit a task

The following Python example reads the token from the environment. `TRACKER_REPO_ID`
must name a repository on this instance. **Running this example creates and edits a real
task**, including upstream writes when the repository is MAC-owned. Use an isolated local
workspace for experimentation.

```python
import json
import os
import urllib.request

base = os.environ.get("TRACKER_URL", "http://127.0.0.1:8765").rstrip("/")
repo_id = os.environ["TRACKER_REPO_ID"]
token = os.environ.get("TRACKER_ACCESS_TOKEN")

def request(method, path, body=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=75) as response:
        return json.load(response)

created = request("POST", f"/api/repos/{repo_id}/tasks", {
    "title": "Review documentation",
    "description": "Check the local setup instructions.",
    "priority": 1,
})
task = created.get("task", created)
updated = request("PATCH", f"/api/tasks/{task['id']}", {
    "title": "Review documentation and API examples",
    "revision": task["revision"],
    "expected_revision": task["revision"],
})
print(json.dumps(updated, indent=2))
```

The revision fields above carry the same observed value for compatible generated REST
representations. Follow the active schema when building a strict client. On 409, fetch
current detail and reconcile instead of retrying the old revision. On upstream timeout,
inspect actual task state before retrying a write.

`dependencies` contains same-project Tracker IDs. The backend translates those for MAC.
`upstream_dependencies` retains raw upstream references; `unresolved_dependencies`
explains missing or outside-project links. An explicit `remove_upstream_dependencies`
array removes selected unresolved MAC references. Ordinary edits preserve foreign
metadata and unresolved references.

## Errors and live events

Validation errors reject invalid input; 401 requires authentication, 404 identifies a
missing resource, 409 indicates a revision/workflow conflict, and 503 indicates an
unavailable authority. Check the structured error code/message for the specific cause.
Do not convert an upstream HTML or empty 503 body into success.

SSE events have ordered durable IDs and named event types. Subscribe to named task and
repository events rather than relying only on `onmessage`. Reconnect with `Last-Event-ID`
for replay. Keepalives maintain the stream; they are not the mechanism for publishing
committed changes. Browsers use the same-origin authenticated cookie for EventSource.

## MCP

The service uses `@modelcontextprotocol/sdk` over Streamable HTTP at `/mcp` and stdio:

```sh
./scripts/litai-service.sh run components/tracker '["service","mcp"]'
```

Use an official SDK client and negotiate its supported protocol version. Do not parse
stdout as ordinary application logs in stdio mode. The tool catalog includes
`list_repositories`, `list_tasks`, `get_task`, `create_task`, `update_task`,
`list_sessions`, and `get_branch_graph`; resource `tracker://repositories` exposes the
repository collection. Inspect `listTools()` for exact argument schemas.

Example using the SDK available in the built application's dependency environment:

```javascript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

const headers = process.env.TRACKER_ACCESS_TOKEN
  ? { Authorization: `Bearer ${process.env.TRACKER_ACCESS_TOKEN}` }
  : {};
const transport = new StreamableHTTPClientTransport(
  new URL('/mcp', process.env.TRACKER_URL || 'http://127.0.0.1:8765'),
  { requestInit: { headers } },
);
const client = new Client({ name: 'tracker-example', version: '1.0.0' });
try {
  await client.connect(transport);
  console.log(await client.listTools());
  console.log(await client.callTool({ name: 'list_repositories', arguments: {} }));
} finally {
  await client.close();
}
```

## A2A and peers

The declared protocol version is **A2A 0.3.0**. Send JSON-RPC to `/a2a`. This example
requests task creation; substitute a repository ID belonging to the receiver:

```json
{
  "jsonrpc": "2.0",
  "id": "request-1",
  "method": "message/send",
  "params": {
    "message": {
      "kind": "message",
      "role": "user",
      "messageId": "documentation-example-1",
      "parts": [{
        "kind": "data",
        "data": {
          "operation": "create_task",
          "repo_id": "RECEIVER_REPOSITORY_ID",
          "task": {"title": "Review documentation", "priority": 1}
        }
      }]
    }
  }
}
```

For outbound `POST /api/peers/{id}/messages`, send `{"message": MESSAGE}` using the
same complete Message object, not the outer JSON-RPC envelope. Preserve `messageId`
on retries. The peer service owns JSON-RPC forwarding and backend authentication.

Supported operations include list/get/create/update repository tasks. `tasks/get`
retrieves the durable A2A Task; `tasks/cancel` rejects completed synchronous work with
TaskNotCancelable. Unknown methods use -32601, malformed parameters -32602, and unknown
A2A tasks -32001. The receiving card declares implemented capabilities and authentication.
