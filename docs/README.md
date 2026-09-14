# Project Tracker documentation

Project Tracker combines repository boards, live tasks, Git history and physical coding
sessions. MAC owns tasks for matched projects; Project Tracker maintains local tasks
for repositories confirmed absent from the configured fleet.

Start with [getting started](user/getting-started.md). For current acceptance status,
read [verification](user/verification.md); repository publication and runtime acceptance
are separate milestones.

## User manual

| Guide | Covers |
| --- | --- |
| [Getting started](user/getting-started.md) | Requirements, build, first launch and first project |
| [Configuration](user/configuration.md) | Data directory, authentication, MAC and LLM settings |
| [Projects and tasks](user/projects-and-tasks.md) | Registration, boards, editing, workflow and dependencies |
| [MAC integration](user/mac-integration.md) | Authority, discovery, synchronization, upstream writes and outages |
| [Git views](user/git-views.md) | Graph, Timeline, branch filters, task links and checkout requirements |
| [Sessions and peers](user/sessions-and-peers.md) | Reporter deployment, host activity and A2A peers |
| [Operations](user/operations.md) | Startup, shutdown, backup, restore and upgrades |
| [Managed deployment](user/deployment.md) | macOS service files, sign-in and launchd controls |
| [Troubleshooting](user/troubleshooting.md) | Common symptoms and diagnostic steps |
| [Security](user/security.md) | Credentials, browser access and execution boundaries |

## Integrators and contributors

- [API and protocol reference](reference/api.md): REST, live events, MCP and A2A examples.
- [Application architecture](architecture/application.md): data flow, persistence and authority.
- [Development](user/development.md): specifications, lifecycle and tests.
- [Contributing](user/contributing.md): work records, review and landing.
- [Project layout](user/project-layout.md): ownership and generated output.
- [Framework flow](user/framework-flow.md), [specifications](user/specifications.md),
  [models and generation](user/models-and-generation.md), and [test matrix](user/test-matrix.md).
- [Verification](user/verification.md), [active work](roadmap/active-work.md), and
  root `CHANGELOG.md`.

The product objective in `PROJECT.md` and Component in `components/tracker/component.md`
are authoritative. Documentation explains those requirements and identifies what has
actually been verified. Framework design references cover [skill boundaries](architecture/skills.md),
[authority learning](architecture/authority-learning-loop.md),
[mission composition](architecture/mission-specification-composition.md), and
[design traceability](architecture/design-traceability.md).

- [Releases](user/releases.md): verified npm archives, installation and release evidence.
