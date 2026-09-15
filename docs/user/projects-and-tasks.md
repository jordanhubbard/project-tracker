# Projects and tasks

[Documentation](../README.md)

## Repository overview and registration

The overview lists repository task counts, authority and physical session activity.
Open a repository to reach its board. Its inspector shows origin URL, local checkout,
default branch, description, synchronization information and sessions.

Register a local Git path, remote URL, or both. SSH and HTTPS URLs for the same host
and repository normalize to one identity; unrelated repositories with the same basename
do not. A remote-only registration supports tasks but needs a local checkout for Git
visualization. The backend never clones a repository merely because a URL was entered.

MAC discovery brings registered fleet repositories into the overview. Explicit MAC
registration is a separate upstream write. See [authority rules](mac-integration.md).

## Board and task details

Each list is a workflow state. Create a task with a nonempty title, open its card, and
edit the fields you need: description, state, priority, labels, cover color, assignee,
branch, due date, checklist and dependencies. Save commits the edit; Cancel leaves the
stored task unchanged. Search and board filters narrow the visible cards.

Use **Move to** for keyboard-accessible state changes, or drag a card between lists.
If the server rejects a move, the card returns to its persisted state and an error
explains the rejection. MAC enforces its own lifecycle; moving a card does not bypass it.

Task edits use a revision number. If another client changed the task, reload its current
state and reconcile your draft before saving again. Do not blindly retry a stale update.
Connected clients receive committed changes through server-sent events without reloading;
unsaved edits must not be silently overwritten.

## Dependencies and upstream references

Choose prerequisite tasks from the labelled **Dependencies** control. Local mutations
reject cycles and cross-repository edges. For MAC tasks, selected tracker task IDs are
translated to MAC IDs before the upstream request.

An imported dependency can refer to a task absent from the snapshot or belonging to
another MAC project. These references remain visible as unresolved details rather than
being silently deleted. Editing unrelated fields preserves them. Use the explicit remove
control to discard a particular unresolved reference; clearing the ordinary dependency
selection does not imply permission to delete every unknown upstream reference.

Imported upstream cycles are retained as read data. This does not remove validation on
new local mutations. A newly available prerequisite can resolve on a later successful
sync. Genuine relationship changes advance the task revision and emit a committed event;
an identical poll should do neither.

## Workflow lists

Local defaults are `open`, `in_progress`, `blocked`, `review`, and `completed`. Use
**Add list** and list actions to add, rename or reorder local states. Deleting a nonempty
list requires a destination for its tasks; migration and deletion commit together.
State IDs remain stable when display labels change.

MAC projects retain upstream states and transition rules. Their standard states are
`open`, `waiting`, `blocked`, `claimed`, `running`, `needs_review`, `needs_input`,
`stopped`, `reviewing`, `completed`, `failed`, and `cancelled`. Additional observed states
are preserved. Empty MAC columns remain available; local `in_progress` is not a synonym
for upstream `running`.

## Branches, activity and deep links

A task's branch field associates it with Git views and reported coding sessions; it does
not create or check out a Git branch. Select a commit in Graph or Timeline to follow its
related task links back to the editor. Activity records committed task changes. Repository
selection is reflected in the URL hash so the board can be reopened directly.
