# Configuration

[Documentation](../README.md)

Configuration belongs to the backend. The browser Settings view edits saved MAC and
LLM connection settings; it never receives stored credential values.

| Variable | Meaning |
| --- | --- |
| `TRACKER_DATA_DIR` | SQLite and private settings directory; use an absolute path |
| `TRACKER_ACCESS_TOKEN` | Backend access token for browser sign-in and bearer-authenticated clients |
| `TRACKER_MAC_URL` | MAC HTTP(S) API base URL |
| `TRACKER_MAC_TOKEN` | MAC bearer credential, used only by the backend |
| `TRACKER_LLM_URL` | Chat-completions gateway prefix, for example `http://127.0.0.1:9000/v1` |
| `TRACKER_LLM_MODEL` | Model identifier sent to that gateway |
| `TRACKER_LLM_KEY` | Backend-only gateway bearer credential |
| `TRACKER_URL` | Reporter destination; this configures the host-side reporter, not the backend bind address |

Without `TRACKER_DATA_DIR`, macOS uses `~/Library/Application Support/project-tracker`.
`--host` and `--port` select the listening address; the default is `127.0.0.1:8765`.
Changing the data directory starts a different workspace rather than moving existing data.

## Saved settings and credentials

Environment values supply defaults. Explicitly saved settings take precedence. Leaving
a credential field blank preserves the existing value; use the labelled clear control
to remove it. An explicit clear must remain cleared even if an environment default
exists. GET responses expose configured booleans instead of secrets.

After changing a connection, inspect its connection feedback and repository sync status.
A working browser connection does not establish upstream access. Stop and restart the
backend after changing process environment variables.

Use HTTP(S) base URLs without embedded usernames or passwords. Authenticated upstream
requests do not follow redirects. Supply the actual API prefix, not a web dashboard URL.

## Browser and client access

Set `TRACKER_ACCESS_TOKEN` before starting a protected instance. Non-loopback binding
requires a token. Keep the token in your process environment or secret manager; do not
include it in URLs. Browser sign-in exchanges it for an HttpOnly, SameSite session
cookie. API, HTTP MCP and A2A clients use `Authorization: Bearer TOKEN`.

An operator exposing the service remotely must provide the secure endpoint and network
controls. The application does not install a reverse proxy, TLS certificate or background
service. See [security](security.md) and [operations](operations.md).

## Assistant gateway

The backend appends `/chat/completions` while retaining the configured path prefix:
`http://127.0.0.1:9000/v1` becomes `http://127.0.0.1:9000/v1/chat/completions`.
The assistant receives a question and bounded repository/task context. It summarizes
or suggests; it does not execute shell commands or silently edit tasks. Core task
tracking works without an LLM configuration.

## Independent instances

Use distinct absolute data directories and ports for development, production and tests.
Do not start two backend processes against the same workspace as an availability strategy.
Test harnesses clear upstream environment settings and use authenticated loopback fixtures.
