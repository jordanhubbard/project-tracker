# Project layout

[Documentation](../README.md)

| Path | Purpose |
| --- | --- |
| `PROJECT.md` | Durable product objective |
| `AGENTS.md`, `SKILL.md` | Agent entry point and specification-led workflow |
| `components/tracker/` | Product, integration, quality, visual and exact runtime specifications |
| `flavors/` | Selected and inherited target policies |
| `skills/`, `workflows/`, `routing/` | Pinned conversion and lifecycle guidance |
| `literate.project.json` | Declared roots, lifecycle binding, cache and repository policies |
| `.literate/` | Framework-managed ancestry and import records |
| `scripts/litai-service.sh` | Toolchain-aware local lifecycle wrapper |
| `verification/acceptance/` | Authored persistent-service acceptance contracts |
| `verification/check_*.py` | Independent product and browser harnesses |
| `verification/current.json` | Framework-owned test receipt |
| `verification/final-result.json` | Consolidated delivery evidence; inspect its artifact scope |
| `docs/` | User, integrator, architecture and development documentation |
| `docs/roadmap/active-work.md` | Current work and completion gates |
| `generated/artifacts/` | Disposable exported application trees |
| `generated/accepted-source-cache/` | Local runtime source cache |
| `generated/committed-source-cache/` | Deliberately published exact-key cache, when present |
| `_build/` | Ignored diagnostics, browser reports, fixtures and temporary drafts |

User data belongs in `TRACKER_DATA_DIR`, outside generated source and transient build
storage. It is not part of the repository or source cache.

`literate.project.json` declares documentation and source roots. Repository inheritance is
separate from the Git remote: `.literate/repository-parent.json` selects the parent,
`.literate/repository-lineage.json` records its exact ancestor graph, and imports track
inherited authority. The GitHub `origin` persists this project's history.

`component.lock.json` is generated resolution, not hand-maintained product prose. Only
files named by a Component's specification roots contribute to that Component's authored
specification set. The source-intelligence policy is currently `none`, with stages off;
this project has no CodeGraph index and does not create one automatically.
