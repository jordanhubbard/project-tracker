# Security

[Documentation](../README.md)

## Service access

Loopback is the default. Non-loopback binding requires `TRACKER_ACCESS_TOKEN`; remote
operators also provide their secure endpoint and network controls. There is no automatic
TLS or reverse-proxy setup. Local unauthenticated requests enforce Host/Origin checks;
mutation and event requests do not allow arbitrary cross-origin access.

Browser sign-in creates an HttpOnly, SameSite cookie. API, HTTP MCP and A2A use bearer
authentication. Tokens must not appear in URLs, browser localStorage/sessionStorage or
rendered page content. When a session is missing, the browser returns to a usable sign-in
form instead of exposing project data.

## Credentials and data

MAC, LLM and peer credentials remain on the backend. Responses reveal only whether a
credential is configured. Blank input preserves it; explicit clear removes it without
silently falling back to an environment default. Authenticated upstream requests refuse
redirects and URLs containing embedded credentials.

The data directory is private, and secret settings use restricted file permissions.
Backups can contain credentials and project content: protect them accordingly and keep
them out of Git. Sanitized logs and public evidence must not expose actual tokens, private
fleet endpoints or raw production task data.

The LLM receives bounded project/task context for the requested question. Consider that
content when choosing a gateway. Assistant responses do not authorize shell execution or
silent task mutations.

## Authority and execution

All task interfaces share the MAC-aware service layer. An upstream outage does not create
local shadow tasks. Explicit operator actions govern MAC registration, local-to-MAC
migration and peer registration. A configured peer card fetch is not permission to
follow arbitrary URLs from later messages.

Generated source remains untrusted until the supported lifecycle admits and tests the
exact candidate. Specifications, selected Flavors and pinned skills define the change;
do not patch generated source, receipts or accepted-cache entries to bypass a failure.
Execution authorization and verified acceptance are separate from source generation.

See [development](development.md), [operations](operations.md), and
[verification](verification.md) for the lifecycle and its current limits.
