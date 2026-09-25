# Changelog

## Unreleased

- Project Tracker: specify named MAC fleets with isolated repository, task, session and
  event identities; add an accessible global fleet selector with URL-backed navigation,
  Settings-based fleet management, independent health, and aggregate or scoped views.

- Verification: add independent multi-fleet service and browser acceptance covering
  secure configuration, immediate first-fleet discovery, token-safe CRUD, write routing,
  one-sided outages, cached-data retention, stable deep links, and desktop/mobile use.
  Tighten MAC repository registration and local dependency validation regressions.

## 1.1.1 - 2026-09-20

[README.md](https://github.com/jordanhubbard/project-tracker/blob/v1.1.1/README.md)

- Packaging: align the tracker component, generated `package.json`, lockfile and project
  release at 1.1.1, then publish the documented archive, manifest and checksum assets.

- Verification: strengthen the fleet snapshot rollback fixture so a phase-selective
  injected failure is consumed only at its named phase. The regenerated Claude candidate
  passes the complete native suite and independent service readiness with `--host` and
  `--port`.

- Documentation: identify v1.1.0 as a source-only release and direct archive installs to
  v1.1.1 or newer.

## 1.1.0 - 2026-09-20

[README.md](https://github.com/jordanhubbard/project-tracker/blob/v1.1.0/README.md)

- Repository: add a documented root Makefile facade for project validation, planning,
  build, test, verification, and foreground or demo runs while preserving the selected
  JavaScript/npm lifecycle as application build authority. Accept Git 2.30.0 and newer
  instead of rejecting compatible versions newer than the observed build toolchain.

- Packaging: exercise the native npm packaging and independent service-readiness paths.
  This tag remained source-only because its generated package version did not match the
  release version, so no install assets were published; v1.1.1 supersedes it for archive
  installation.

- Documentation: provide complete setup, configuration, project/task, MAC, Git,
  session/peer, API, operations, security, troubleshooting and contributor guides.
  Replace stale blanket completion claims with artifact-specific acceptance status.

- Repository: persist the Project Tracker workspace on GitHub main through PR #1,
  preserving the starter history and BSD license. Remaining MAC runtime repairs
  are tracked separately from the completed workspace import.

- Project Tracker: deliver the verified local frontend/backend workspace with live
  Trello-style task boards, editable workflows, repository inspection, physical
  coding-session reporting, Git graph/timeline exploration, MAC authority routing,
  official MCP, durable A2A peering, backend LLM settings and protected browser login.
  Validated with 28 native tests, nine independent phases, desktop/mobile Chrome
  interactions and the public LitAI launcher.

- Initialized the project with Literate AI's specification-led lifecycle and durable
  user-directed work queue.
