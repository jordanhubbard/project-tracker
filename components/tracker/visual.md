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
dates on actual loaded commits show a bounded diagnostic state instead of invalid
coordinates. Marked outside-window parent placeholders are not loaded commits:
exclude their absent dates from the timeline's validity check and preserve the
valid dated commits. Do not invent a timestamp for a boundary marker. Explain
that the history window is bounded while Graph keeps the genuine parent edge.

Collision handling covers nearby unequal timestamps as well as identical ones.
Preserve proportional timestamp x coordinates and choose vertical bands using the
rendered node, subject and ref-label extents. A label must never overlap another
node's pointer hit target. At default and Reset scale, real circle clicks on each
commit in the 0, 10, 100, 110 second fixture select that commit's own inspector;
keyboard activation also works. Keep trailing labels reachable in the scroller.
A bounded 1005-commit history still displays its loaded real commits in Timeline,
including when the Graph response has null-dated outside-window placeholders.

A fixed minimum gap between circle centers is not sufficient collision handling.
For example, at times 0, 10, 100 and 110 seconds, the labels "Base" and "Main"
with eight-character hashes overlap the next circles when all nodes share a row.
Reserve the full hash, subject and ref-label rectangle in each vertical band,
including padding around other node targets. Measure rendered text or use a
conservative bounded label width with truncation and accessible full text.
Verify bounding rectangles of each label against every other commit hit target;
none may intersect. Drawing a later circle on top of an earlier label still fails
readability even if that circle receives clicks.

The label budget applies to the complete visible string after composing the
abbreviated hash, subject and every ref suffix, including separators and padding.
Truncating only the subject before appending refs does not establish a bound.
Either measure that complete rendered label and allocate disjoint rectangles,
or constrain the complete label to the reserved width with accessible full text.
For equal-timestamp commits, the hash-prefixed `Merge feature [main]` label must
not touch or cross the neighboring `Main` commit target. Verify complete labels
at initial scale, after zoom and after Reset in desktop and mobile layouts.
Preserve proportional timestamp positioning and related-task editing.

Both modes provide visible Zoom in, Zoom out, Reset and branch-filter controls.
Zoom changes the actual graph scale; Reset restores fit. Scroll/pan allows every
node to be reached. The very first Zoom in on the four-commit fork/merge fixture
must visibly enlarge commit geometry. Apply the scale to the complete fitted
canvas size, including label padding and any minimum viewport size. Applying a
minimum width after multiplying only the narrow lane width can swallow the first
several zoom increments. Compare an actual commit circle's rendered diameter
before and after one click, then verify Reset restores its original geometry.
The branch filter uses real ref ancestry and retains required
boundary context. Show task and active-session branch associations as overlays
or linked annotations using actual backend data. A selected branch's task list
must use the branch association, not label every repository task "on this branch".
For distinct main and feature tasks, filtering to feature and selecting its tip
shows feature-related tasks without mislabelling main-only tasks. Include active
coding-session branch associations from the backend alongside task associations;
MAC assignments alone are not active coding sessions.

Clicking or keyboard-activating a node selects it and opens an in-page commit
inspector with hash, subject, author, timestamp, parents and related task links.
An alert box or a hover-only title is insufficient. Keep the selected node visibly
distinguished and allow Enter/Space activation without scrolling the page.

### Chart and inspector sizing on mobile

At 390px width, opening a selected commit inspector must not collapse the Graph
or Timeline canvas. Keep a usable chart viewport with at least 180px of client
height in the 390x844 acceptance viewport, including after switching modes with
the Feature commit already selected. A tall inspector may extend the vertically
scrollable view; it must not consume the chart's grid or flex allocation. Give
the chart row a non-collapsing minimum or equivalent intrinsic sizing, and let the
containing view scroll to reach the inspector. A zero-height scroller surrounding
a nonzero SVG is not a visible chart. Do not cover node targets with the inspector
or clip document overflow to conceal a broken layout.

Verify the four-commit equal-time and irregular-time fixtures with the selected
Feature inspector, branch filter applied and cleared, then Graph to Timeline and
back. Real pointer clicks on reachable commit circles must update the inspector
without force clicks or injected CSS. Retain Zoom/Reset, proportional timestamps,
label collision avoidance and related-task editing at both desktop and mobile.

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

## Hidden dialog lifecycle

A hidden modal container must not render, cover the workspace, intercept pointer
input, or retain keyboard focus. Preserve the HTML hidden attribute's behavior even
when component rules set display:flex or display:grid. The initially empty dialog
root must be hidden on first load; opening a dialog makes it visible, and Cancel,
Escape and successful Save hide it again. Use an explicit hidden-state CSS rule
with sufficient precedence over the component display rule. Verify real Chrome
clicks after cold load and after each dismissal path, at desktop and 390px widths.
Do not force clicks, remove the overlay, inject CSS, or bypass browser policies in
acceptance tests.

## Responsive workspace header

At 390px, account for the combined widths of the menu, workspace title, connection
status, Create, Settings, search, padding and gaps. Every visible header control
must remain within the viewport, and document.scrollWidth must equal the viewport
width. Use wrapping rows or move an accessible Settings control into the sidebar
when necessary. A grid with inflexible button tracks that total more than the
available width is not responsive. Check Connecting, Connected and Offline text;
search may occupy its own row. Do not hide or clip the overflow at the body/root
level or leave the Settings control beyond the right edge.

## Workflow deletion from the board

Every list menu exposes both Rename and Delete. Deleting a populated list offers
a labelled destination chosen by list name, migrates every task to that remaining
list in the same backend operation, and removes the deleted list. Preserve task
attributes and revisions correctly. Cancel leaves the list and tasks unchanged;
reject deleting the last list. Verify through the visible UI: add a list, move it
left, reload, create a task in it, delete with a destination and confirm both the
remaining ordered states and migrated task through the API. A rename-only menu
or a backend-only delete capability does not satisfy editable workflow states.

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
Render these controls before any empty, unborn, checkout-needed or error return.
A remote-only repository explains the checkout requirement and still offers Back
to board plus Inspector so the operator can supply a path. Test clicking Graph
from a remote-only board and returning through its visible control; browser Back
or rediscovering the repository in the sidebar is not the view's navigation.
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


## Operable navigation and complete zoom

Every visible workspace sidebar button has an actual route activation handler.
A data-route attribute alone performs no navigation. From a repository board,
click Activity and inspect titled task events; click Agents & peers and register
an isolated peer; click sidebar Settings and edit configuration. Verify these
actual controls at desktop/mobile widths, independently of header Settings and
without substituting direct URL navigation for a dead sidebar button.

Zoom must scale the rendered circle radius, edge widths and labels together with
positions and the complete canvas. Multiplying node x/y and SVG width while leaving
circle radius and text size fixed is only spacing, not the required graph zoom.
A real circle's screen diameter must increase on the first Zoom in and return on
Reset in both Graph and Timeline. Test rendered geometry, not only SVG width.

Retain the supplied Trello reference's compact visual hierarchy: list names remain
fully legible, with counts and compact actions; do not truncate short names such as
blocked or in_progress because permanent controls consume the header width. Put
secondary actions in an accessible list menu or a separate compact row. Task cards
prioritize title, colored label strips, cover color and concise metadata. Keep
secondary edit/move controls accessible without allowing repeated control rows to
dominate the card. Review actual desktop/mobile screenshots against the reference.


## Physical host identity in branch associations

Graph and Timeline visibly show the actual physical hostname for active coding
sessions associated with the selected commit's branch. Carry that hostname from
the reporter through the graph API projection into the visible session annotation.
Showing only CLI and status loses the physical-host association; showing the host
only in Fleet is insufficient for these branch views.

On an unfiltered repository graph, selecting the main branch tip shows the exact
hostname of an active reporter on main. An always-visible branch-association panel
may also provide this information. Do not require an undisclosed branch-filter
choice before any active host becomes visible. Filtering feature excludes hosts
associated only with main. Keep task annotations scoped to the actual branch.


## Short list names at normal board widths

At desktop 1440px and mobile 390px, ordinary columns display the full short names
open, in_progress, blocked, review, completed and Ready desktop. Do not ellipsize,
clip or cover these names with list controls. Reserve the name/count row for those
labels and place secondary actions in the accessible menu or a separate compact
row. Keep ordinary column widths and horizontal board scrolling. Measure the
rendered list-name element and require scrollWidth <= clientWidth for these names;
review screenshots as well as successful rename/reorder/delete behavior.

Related tasks in the selected commit inspector are actionable links or buttons,
not a sentence listing task titles. Preserve each association's task ID and route
activation to the same loaded task editor used by the board. In Graph and Timeline,
select a feature-branch commit, activate its related task by title and verify that
the editor shows that exact task's title and current attributes. Cancel closes it
without mutation; save uses the normal revision-aware task update. Keep task-link
activation independent of commit-node selection and branch filtering.

The task dependency multiple-select has an accessible name such as Dependencies.
Associate its visible label using label/for or aria-labelledby, or provide an
aria-label. aria-describedby supplies supplemental help and does not name the
control. Screen readers and role/name selectors must identify the dependency
listbox by its label; choosing dependencies by task title remains supported.
