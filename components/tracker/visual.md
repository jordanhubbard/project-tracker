---
name: Complete board and Git visual behavior
summary: Rendered graph layout, actual navigation views and CSP-compatible card covers
kind: visual
---
# Complete board and Git visual behavior

This document makes the visual outcomes precise. It does not reduce any requirement
in component.md or quality.md. A usable board alone is not the complete application.

## Git layout and controls

Build a single layout map keyed by commit hash. Each entry contains the commit,
its stable index, lane and finite x/y coordinates. Node drawing, edge drawing,
selection and labels must all consume that same map. Do not attach an index to
one copy of a commit and then read it from the original unannotated object.
No SVG attribute or transform may contain NaN, undefined or Infinity.

Graph mode uses topological order and ancestry lanes. Draw every actual parent
edge, including a visibly marked boundary when its parent is outside the bounded
window. Ref labels identify branch tips. Do not draw sequential edges merely
because two commits are adjacent in time or in a list. All rendered nodes need
distinct usable hit targets and readable labels.

Timeline mode uses committed_at to determine horizontal position and a visible
timestamp axis. It is not Graph mode with a decorative horizontal line. Equal
time intervals occupy equal horizontal distances. Commits sharing a timestamp
must have separate vertical positions or another explicit collision layout so
their nodes and labels remain independently selectable. The all-equal timestamp
case uses a finite time domain and keeps every node visible. Absent or malformed
dates show a bounded diagnostic state instead of invalid coordinates.

Both modes provide visible Zoom in, Zoom out, Reset and branch-filter controls.
Zoom changes the actual graph scale; Reset restores fit. Scroll/pan allows every
node to be reached. The branch filter uses real ref ancestry and retains required
boundary context. Show task and active-session branch associations as overlays
or linked annotations using actual backend data.

Clicking or keyboard-activating a node selects it and opens an in-page commit
inspector with hash, subject, author, timestamp, parents and related task links.
An alert box or a hover-only title is insufficient. Keep the selected node visibly
distinguished and allow Enter/Space activation without scrolling the page.

### Fork and merge scenario

A real repository contains base A, children B and C, and merge D with parents B
and C. Graph displays four distinct nodes and exactly the four parent edges
A-B, A-C, B-D and C-D. Selecting each node shows its own commit details. This
must remain usable when all four Git commits share a timestamp. A second scenario
uses times 0, 10 and 100 seconds: Timeline positions reflect elapsed time rather
than uniform list indices. Empty and unborn repositories show an empty state;
remote-only repositories explicitly request a local checkout.

## Visible covers under the shipped security policy

Assigned purple, blue, green and orange card covers must render in both desktop
and mobile screenshots. Apply colors through CSS classes or a style mechanism
authorized by the actual shipped Content Security Policy. Do not emit blocked
inline style attributes and leave blank grey cover space. Validate user color
values, preserve saved colors on edit, and check computed backgrounds in the
browser. Serve a local favicon or declare one that does not create a 404 request.
No console, CSP, failed-resource or uncaught page errors are acceptable.

## Readable board controls

Native form controls participate in the dark theme, including the compact task
move selects on every card. Set a dark color-scheme and explicit compatible
foreground/background colors where needed. A pale label on a default white native
select is unreadable even if its action works. Inspect the closed select and its
options at desktop and mobile widths; retain visible keyboard focus.

## Actual navigation destinations

Dispatch Activity and Agents & peers before the no-selected-repository overview
fallback. These buttons must change to their own visible views and URL state.
Activity shows persisted, human-readable task creation, state changes and attribute
edits in time order and incorporates incoming events. Agents & peers shows physical
host sessions, clearly separate MAC assignments, and registered peer agents.

The peer view includes registration, fetched card details, connection/error state,
an explicit message action with result/history, and removal. Secrets remain
backend-only and password inputs never refill stored tokens. An unconfigured peer
list shows a useful empty state and the registration control. A button that simply
returns to Project overview has not implemented this view.

Settings loads saved nonsecret URLs, model and timeout before editing. Blank
password inputs preserve existing credentials; clear actions are explicit.
The task editor provides labeled controls for title, description, state, integer
priority, labels, cover color, assignee, branch, due date, checklist text/completion,
and dependencies. Priority is editable on creation and update, with its current
value loaded and preserved through later edits; a backend field alone does not
fulfill task editing. At desktop and mobile, change priority to 2 together with
other attributes, save, reload, reopen and verify the persisted value.
Task editing preserves every unedited attribute, including checklist completion,
labels, due date and dependencies. Provide dependency selection by task title
instead of requiring the operator to type internal task IDs.

## Rendered verification

At desktop and 390px widths, open the board, create/edit/move a task, rename a
workflow state, inspect a repository, visit Activity and Agents & peers, and
exercise both Git modes including node selection, zoom/reset and filtering.
Verify backend persistence and a second-client event while observing the page.

Graph and Timeline retain visible navigation back to the board and between modes.
After applying or clearing a branch filter, commit selection must still update the
inspector; reuse the selection callback when rebuilding the SVG. Scope workspace
sidebar styles to that sidebar: a commit inspector must not inherit a fixed sidebar
position or the mobile off-screen transform. On mobile it appears within the page
and the selected full hash and subject remain reachable. Route focus must not scroll
the view heading underneath the sticky top bar. Verify zoom changes the visible
graph scale, Reset restores it, and both filtered and unfiltered nodes remain
keyboard-selectable under the actual CSP.

Activity entries use repository and task titles for creation, edits and state moves,
with IDs available in details. Task-created events and their renderer must agree on
the payload shape; do not fall back to task UUIDs when the event already contains
the title. The same second-client task title visible on the board is visible in its
creation entry in Activity.
Capture actual rendered views and inspect their coordinates and visible content;
the presence of an SVG element or a button alone does not prove functionality.
