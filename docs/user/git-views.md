# Git Graph and Timeline

[Documentation](../README.md)

Git views read a checkout on the backend host. A remote URL alone does not provide
history, and Project Tracker does not clone, fetch, commit, merge or check out branches
when you browse a graph.

**Graph** draws the actual commit parent relationships, including forks and merges.
**Timeline** positions commits by time and shows a timestamp axis. Chronological adjacency
does not imply a parent relationship. Branch tips, related tasks and active reported
sessions provide context around the same history.

## Explore a repository

1. Open its board and select Graph or Timeline.
2. Choose a branch filter to restrict the reachable history, or clear it for all refs.
3. Select a commit to inspect its hash, parents, author and subject.
4. Use zoom and reset, and scroll the chart to explore a larger history.
5. Follow a related task link to open that task's editor.

Task branch names and reporter branch values establish associations. A session association
shows the reporter's physical hostname, not an assumption that the backend is running
the coding CLI. See [sessions](sessions-and-peers.md).

The loaded history is bounded. Boundary nodes represent real parents outside that window;
they are not fabricated commits or missing merge edges. Equal timestamps remain selectable,
while irregular timestamps preserve their relative spacing in Timeline.

## Empty and unavailable states

| View state | Meaning and next step |
| --- | --- |
| Checkout needed | Add a local path accessible to the backend |
| Missing or inaccessible path | Correct the path or filesystem access in the repository inspector |
| No commits / unborn | The repository has not yet acquired the relevant history; create history using Git outside Tracker |
| Detached HEAD | Git is at a commit without a checked-out branch; inspect the available refs normally |
| Unknown branch or Git error | Refresh the branch selection and inspect the error; this is not successful empty history |

Branches and files may share names. Filtering must still resolve the actual Git ref,
including for names such as `main` and `feature`. Mobile charts scroll within their own
region; the inspector remains reachable through normal vertical scrolling.
