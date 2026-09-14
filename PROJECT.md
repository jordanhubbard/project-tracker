# Project Tracker

Create with LitAI a frontend/backend workspace for every repository and task the user
works on. Show which physical hosts have active coding CLI sessions on each project.
Provide a graphical branch timeline and relationship graph derived from Git. Take
interaction cues from jordanhubbard/precis-mcp (zoom, selection, contextual inspection).

Task tracking must closely follow the supplied Trello concept: dark horizontal lists,
dark cards, colored covers and labels, left sidebar, board toolbar; repository overview
and inspector lead into editable task detail and movable, editable task states. Tasks
appearing or changing state or attributes update live without reloading.

The backend owns durable database, MCP, A2A peer interoperability, LLM gateway URL and
key. Browser code owns visualization and talks only to this backend. MAC normally owns
project registration and tasks. For repositories absent from the configured MAC fleet,
Project Tracker owns equivalent internal tasks. Absence and upstream failure differ.

Execution of the application and its tests is part of this requested implementation.
Live fleet writes must be deliberate operator actions in the UI. Fleet-wide
installation is outside this project implementation.

## Publication and documentation

Persist this workspace at `git@github.com:jordanhubbard/project-tracker.git`. Maintain
a complete user, operator, integrator and contributor manual under `docs/`, linked
from the root README. Document actual accepted behavior and outstanding integration
gates separately; GitHub persistence is not proof of runtime acceptance.

Publish the first stable release, v1.0.0, to the existing GitHub repository after
tracker acceptance, documented runtime verification and package verification pass.
Ship downloadable artifacts and verify the remote tag and release against the
accepted source revision.
