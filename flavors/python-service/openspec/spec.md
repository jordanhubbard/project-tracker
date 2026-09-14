# Python service runtime

### Requirement: Python ASGI service

The implementation SHALL generate Python 3.11+ service code in `source/`, with `source/main.py` as dispatcher.
Use the ASGI framework and official MCP SDK required by the Component. Third-party
runtime dependencies are required, not optional; declare exact pinned versions in
pyproject.toml and requirements.txt and a complete source CycloneDX BOM. The operator
provides an isolated interpreter with these dependencies installed before the authorized
build. Do not install dependencies or use the network during model generation.

This is a service-specific language flavor, not the portable standard-library flavor.
Do not substitute handwritten HTTP or MCP lookalikes. Keep backend modules separate
from static HTML/CSS/JavaScript assets, and include all assets in the runnable artifact.
Default `service` CLI and Standard --litai-serve must start the same real ASGI app.
Support --litai-test and --litai-smoke through the same product implementation; use
isolated temporary databases and synthetic upstream fixtures for tests. Generated
native tests should use unittest (available in the interpreter), not undeclared test
libraries. Avoid bytecode mutation of admitted source with PYTHONDONTWRITEBYTECODE=1.

The standard tree builder preserves the Python source tree; runtime dependencies live
in the selected interpreter's isolated environment. Generated package metadata must
allow installing the same dependencies into a new environment for distribution. Do not
claim the application is self-contained or runs on a bare interpreter.

#### Scenario: Full service starts

- **WHEN** the artifact starts with the configured isolated interpreter
- **THEN** it serves the complete ASGI application with its declared SDK dependencies

### Requirement: Exact runtime closure

The generated manifests and source BOM SHALL describe the installed runtime closure:

```text
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
attrs==26.1.0
certifi==2026.7.22
cffi==2.1.1
click==8.5.0
cryptography==50.0.1
fastapi==0.141.1
h11==0.16.0
httpcore==1.0.9
httpcore2==2.12.0
httpx==0.28.1
httpx2==2.12.0
idna==3.19
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
mcp==2.2.0
mcp-types==2.2.0
opentelemetry-api==1.44.0
pycparser==3.0
pydantic==2.13.5
pydantic-core==2.46.5
pyjwt==2.14.0
python-multipart==0.0.32
referencing==0.37.0
rpds-py==2026.6.3
sse-starlette==3.4.11
starlette==1.6.0
truststore==0.10.4
typing-extensions==4.16.0
typing-inspection==0.4.4
uvicorn==0.52.4
```

MCP 2.2 uses `from mcp.server.mcpserver import MCPServer`. Create the server with
its name, decorate typed tools/resources, and use `streamable_http_app` with
`streamable_http_path`, `json_response` and `stateless_http` keyword parameters.
Mount and run its SDK session manager lifecycle with the ASGI lifespan. `run` accepts
transport `stdio` or `streamable-http`. Do not import the removed FastMCP v1 location.

#### Scenario: Required frameworks import

- **WHEN** the selected interpreter imports fastapi, uvicorn, httpx and mcp
- **THEN** their versions match the exact declared runtime closure
