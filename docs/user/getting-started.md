# Getting started

[Documentation](../README.md)

Project Tracker runs a local web application backed by SQLite. A browser is sufficient
for everyday use after the backend starts. Git views require a checkout accessible to
that backend. MAC, an LLM gateway and peer instances are optional connections.

## Requirements

The currently selected build targets macOS. It requires Node.js **22.23.2**, Git
**2.30.0 or newer**, and the installed Literate AI **1.0.1** CLI. Git 2.50.1 is the
version recorded by the accepted build evidence; newer compatible Git releases are
allowed. The application uses Node's built-in SQLite and the locked official MCP
JavaScript SDK dependency tree.

Install the required toolchain and your configured Literate AI distribution before
building. Confirm `litai --version`, `git --version`, and the Node version selected by
`scripts/litai-service.sh`. The wrapper prefers Homebrew's `/opt/homebrew/opt/node@22/bin`
when present. This repository is a development workspace; it does not provide a signed
macOS installer or claim validation on Windows or Linux. See [verification](verification.md).

## Clone and build

```sh
git clone git@github.com:jordanhubbard/project-tracker.git
cd project-tracker
make plan
make build
```

Building may invoke the configured coding provider and requires its authenticated
installation. The wrapper selects Claude Code by default. An exact source-cache hit
can avoid generation, but must still pass current acceptance. Generation can take
considerably longer than an ordinary source build. See [development](development.md).

Only launch an export produced by a successful build. A previous export can remain
on disk after a newer build fails; its presence does not establish current acceptance.

## Start the application

Choose an absolute directory for your data, then launch the foreground service:

```sh
export TRACKER_DATA_DIR="$HOME/Library/Application Support/project-tracker"
make run
```

Use `make demo` for an isolated sample workspace or `make help` to list the available
shortcuts and overrides. The underlying supported run command remains:

```sh
./scripts/litai-service.sh run components/tracker '["service","--host","127.0.0.1","--port","8765"]'
```

Open `http://127.0.0.1:8765`. Check readiness with:

```sh
curl --fail http://127.0.0.1:8765/health
```

Readiness establishes that the application is serving requests. Check the repository's
synchronization status separately to establish MAC health. Press Ctrl-C to stop.

For sample data, add `"--demo"` inside the JSON argument array. Demo storage is isolated
from the ordinary database. Keep real MAC credentials out of a demonstration environment.

When `TRACKER_ACCESS_TOKEN` is configured, use the browser's **Sign in** form. API clients
supply a bearer header. Read [configuration](configuration.md) before remote binding.

## Add your first repository

Open the repository registration control. Supply a local checkout path or a remote
repository URL and a useful name. A remote URL identifies a project; it does not clone
it. Add a backend-accessible local path when you want Graph and Timeline.

If MAC is configured, discovery matches existing projects automatically. Inspect the
authority badge before editing: local, MAC, or unresolved. Registering a project with
MAC is a separate deliberate action.

Open the repository board, create a task, then reopen its card to edit its description,
priority, labels, checklist or dependencies. Move it with the accessible state control
or drag it between lists. Other connected clients receive committed changes live.

Continue with [projects and tasks](projects-and-tasks.md), [MAC integration](mac-integration.md),
and [Git views](git-views.md).
