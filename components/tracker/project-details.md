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

The synchronizer must actually schedule these detail reads after each successful
discovery snapshot. For every discovered project, percent-encode the discovery routing
name as one URL path segment and request `/projects/{encoded-project}`. A successful
detail response must be sanitized and committed to that project's repository row before
the synchronization reports success. Automatic synchronization may reuse a last-good
snapshot whose `fetched_at` is less than 60 seconds old; a manual `POST /api/sync` must
bypass that age check. Never let more than four project-detail requests be in flight,
including when many details are missing on first discovery.

A detail failure must not discard an otherwise valid project, task or registry snapshot.
Retain the prior detail with its fetched timestamp and record a per-project detail error.
A detail response may add information but cannot change the logical routing name
established by discovery. Persist the safe snapshot and its status in SQLite so it is
available after restart before the next successful refresh.

Schema migration from every previously released Project Tracker database must add any
project-detail storage columns without dropping or recreating repositories, tasks,
events, settings or credentials. A repository-detail write and its status update are one
SQLite transaction. A failed detail read with no last-good value persists an error status
without manufacturing a successful `fetched_at`; a later success clears that detail error.

## Privacy and resource bounds

Never expose the MAC bearer credential or metadata values whose case-insensitive key
contains token, secret, password, credential, authorization, cookie, private_key or
api_key. Replace those values with the literal `[redacted]` at every nesting level before
persistence. Bound the retained and displayed detail to 64 KiB, nesting depth eight,
100 array entries per array and 4,000 Unicode code points per string. Record visible
truncation markers instead of failing the fleet synchronization.

The 64 KiB limit applies to the UTF-8 encoded serialized safe snapshot after redaction,
not merely to an individual string or upstream HTTP response. Apply deterministic
truncation until the serialized value is at most 65,536 bytes. Secret-shaped keys at or
beyond a truncation boundary remain redacted; neither SQLite, repository API responses,
browser DOM nor browser storage may contain an original secret value.
Reduce oversized strings, arrays and over-depth descendants before removing ordinary
object members. An unrelated bulk sibling must not cause bounded output to discard
finite numbers (including zero), booleans (including false), null, or empty object/array
members that already fit their individual limits. Preserve those JSON types exactly;
never replace them with truthy fallbacks or omit them merely to halve an object's keys.

Measure serialized size as the UTF-8 byte length of compact `JSON.stringify` output. For
example, sanitizing `{"api_key":"secret","name":"alpha"}` produces
`{"api_key":"[redacted]","name":"alpha"}`, whose compact serialization is 39
UTF-8 bytes.

## API and Inspector

Expose the safe snapshot only on authenticated `GET /api/repos/{id}` as
`mac_project_detail`; keep repository collection responses compact. The value contains
project name and ID, repository URL, fetched time, freshness/error state and bounded
metadata. Local and unresolved repositories return null.
Map the upstream detail's `project`, `project_id` and `repository_url` to those top-level
fields and sanitize its `metadata` object into `mac_project_detail.metadata`. Do not place
the entire upstream detail response inside that metadata field (which would incorrectly
produce paths such as `mac_project_detail.metadata.metadata.api_key`).

`mac_project_detail.fetched_at`, `.fresh` and `.error` describe the current cache status
in every repository-detail response. After a failed refresh with last-good metadata,
overlay `fresh: false` and the current bounded error on that returned value while keeping
the last successful `fetched_at`; do not return stale embedded `fresh: true` or
`error: null` values from the stored success. Persistence may normalize status into
separate SQLite columns, but those columns are an implementation detail and do not alter
the public nested shape.

For a MAC-owned repository, Inspector shows a **MAC project details** section with the
same fields and an accessible nested key/value view. Render strings as text, never HTML;
distinguish empty objects, empty arrays, null, false and zero. Nested values are
keyboard-operable and the section remains usable at 390px without page-level horizontal
overflow. If no safe snapshot exists, explain whether detail is loading or failed. When
last-good data is retained after an error, show both its fetched time and stale/error
state rather than presenting it as fresh.

## Required generated acceptance scenarios

Generated native tests must use a synthetic authenticated MAC server and exercise the
real `MacSync`, SQLite store and repository HTTP handlers. Acceptance requires all of the
following observations; a helper-only unit test does not satisfy them:

1. Initial discovery of five projects produces five encoded `/projects/{project}` reads,
   never exceeds four concurrent reads, persists sanitized details, omits detail from
   `GET /api/repos`, and returns it from each `GET /api/repos/{id}`.
2. A second automatic sync within 60 seconds makes no additional detail reads, while a
   manual sync immediately makes one additional detail read per discovered project.
3. One detail endpoint fails after an earlier success: the global project/task snapshot
   still commits, the old detail and original `fetched_at` survive with `fresh: false`
   and a bounded error, then a later success replaces it and clears the error.
4. Closing and reopening the store exposes the same last-good detail before another MAC
   request. Opening a fixture database created with the previous released schema retains
   its rows and accepts project-detail writes.
5. A nested fixture containing every secret-shaped key, an HTML-like string, overlong
   Unicode strings, arrays over 100 entries, depth over eight and total data over 64 KiB
   proves recursive redaction, deterministic visible truncation, a serialized maximum of
   65,536 bytes and text-only browser rendering at desktop and 390px widths.
