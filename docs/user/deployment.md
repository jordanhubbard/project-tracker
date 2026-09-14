# Managed macOS deployment

[Documentation](../README.md) · [Operations](operations.md)

The deployed v1.0.0 service uses the unchanged [published archive](https://github.com/jordanhubbard/project-tracker/releases/tag/v1.0.0).
The operating account owns the application and data. A system LaunchDaemon runs it
as that account and starts it at boot. This is separate from a development build.

## Access and files

Open `http://HOST:8765` on the intended network. Sign in with the token in
`~/.config/project-tracker/access-token` on the deployment host. Retrieve it over
SSH; do not put the token in a URL, issue, screenshot or Git commit.

| Path | Purpose |
| --- | --- |
| `~/.local/share/project-tracker/releases/v1.0.0/package` | Verified application and locked dependencies |
| `~/.local/share/project-tracker/downloads/v1.0.0` | Original archive, manifest and checksums |
| `~/.local/share/project-tracker/launch.py` | Loads private configuration and executes the service |
| `~/.config/project-tracker/service.json` | Private process configuration, including access and MAC credentials |
| `~/Library/Application Support/project-tracker` | Durable database and saved settings |
| `~/Library/Logs/project-tracker` | Standard output and error logs |
| `/Library/LaunchDaemons/com.project-tracker.service.plist` | Root-owned launchd registration; process runs as the operating account |

Private configuration and token files have mode 0600. Data, configuration and log
directories have mode 0700. The configured MAC connection performs background reads;
production task writes remain deliberate operator actions in the application.

## Service controls

Run these commands on the deployment host:

```sh
sudo launchctl print system/com.project-tracker.service
curl --fail http://127.0.0.1:8765/health
```

Graceful restart: the service handles SIGTERM, then launchd restarts it because
KeepAlive is enabled.

```sh
sudo launchctl kill SIGTERM system/com.project-tracker.service
```

Stop for a consistent backup:

```sh
sudo launchctl bootout system/com.project-tracker.service
```

After [backing up the complete data directory](operations.md#backup), start again:

```sh
sudo launchctl bootstrap system /Library/LaunchDaemons/com.project-tracker.service.plist
```

Check both HTTP readiness and `mac.last_sync_ok`. Confirm repository and task data
after startup. A loaded LaunchDaemon alone does not establish application readiness.
The initial deployment passed native diagnostics, authenticated desktop/mobile browser
checks, managed restart and exact upstream task-ID comparison. Startup after a full
machine reboot was not separately exercised.

The release's documented UI issues still apply. LLM gateway configuration is optional
and can be supplied through Settings; deployment verification does not claim an LLM
connection was tested.
