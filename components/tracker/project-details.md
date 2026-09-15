---
name: MAC project detail
summary: Safe cached MAC project metadata in repository API and Inspector views
kind: integration
---
# MAC project detail

## Acquisition and persistence

Fetch `GET /projects/{project}` for discovered MAC repositories and retain a last-good,
display-safe project-detail snapshot separately from the summary used for identity
matching. Do not issue one detail request per five-second task poll: refresh missing
details promptly, refresh existing details no more than once per minute, and let an
explicit operator synchronization request refresh details immediately. Bound detail
fetch concurrency to four.

A detail failure must not discard an otherwise valid project, task or registry snapshot.
Retain the prior detail with its fetched timestamp and record a per-project detail error.
A detail response may add information but cannot change the logical routing name
established by discovery. Persist the safe snapshot and its status in SQLite so it is
available after restart before the next successful refresh.

## Privacy and resource bounds

Never expose the MAC bearer credential or metadata values whose case-insensitive key
contains token, secret, password, credential, authorization, cookie, private_key or
api_key. Replace those values with the literal `[redacted]` at every nesting level before
persistence. Bound the retained and displayed detail to 64 KiB, nesting depth eight,
100 array entries per array and 4,000 Unicode code points per string. Record visible
truncation markers instead of failing the fleet synchronization.

## API and Inspector

Expose the safe snapshot only on authenticated `GET /api/repos/{id}` as
`mac_project_detail`; keep repository collection responses compact. The value contains
project name and ID, repository URL, fetched time, freshness/error state and bounded
metadata. Local and unresolved repositories return null.

For a MAC-owned repository, Inspector shows a **MAC project details** section with the
same fields and an accessible nested key/value view. Render strings as text, never HTML;
distinguish empty objects, empty arrays, null, false and zero. Nested values are
keyboard-operable and the section remains usable at 390px without page-level horizontal
overflow. If no safe snapshot exists, explain whether detail is loading or failed. When
last-good data is retained after an error, show both its fetched time and stale/error
state rather than presenting it as fresh.
