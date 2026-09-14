# Operations

[Documentation](../README.md)

## Startup and shutdown

Run the service in the foreground using the [getting-started command](getting-started.md#start-the-application).
Use a stable absolute `TRACKER_DATA_DIR`, a deliberate port, and loopback unless remote
access is configured. Stop with Ctrl-C and let the process close its server and database.
Do not assume a previously started development process is a managed background service.

`GET /health` checks service readiness. MAC readiness additionally requires a successful
complete synchronization, no repository sync errors, and the expected task data. A
healthy listener can coexist with a failed upstream connection.

## Backup

Stop every process using the workspace before making a filesystem backup. Copy the
**complete data directory**, including SQLite sidecars and private settings. Do not copy
a changing database file and its WAL independently and call that a consistent backup.

For example, with the service stopped and `TRACKER_DATA_DIR` set to its absolute path:

```sh
tracker_backup_dir="$HOME/project-tracker-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -m 700 "$tracker_backup_dir"
cp -pR "$TRACKER_DATA_DIR/." "$tracker_backup_dir/"
```

Treat the backup as confidential because it can contain stored credentials and project
data. Keep it outside the Git checkout and use your normal encrypted backup controls.
Record the application artifact or repository revision alongside it.

## Restore

Restore into a new private directory while the service is stopped. Point an isolated
instance at that directory and a different port. Clear inherited MAC/LLM environment
values if you intend an offline inspection, and remember that saved settings may still
contain upstream connections. Review those settings before starting connected work.

Verify repository and task counts, representative task details, workflow states,
dependencies, activity and saved settings. Retain the previous data directory until
this validation is complete. Do not overwrite your only copy with an unverified restore.

## Upgrade

1. Stop the service and make a consistent backup.
2. Preserve local specification changes, then fetch and review the target Git revision.
3. Run the supported build and acceptance lifecycle on that revision.
4. Start the accepted export against the intended data directory.
5. Verify readiness, task data and upstream recovery before reconnecting other clients.

Generated output and source-cache entries are replaceable. User data is not. Keep
`TRACKER_DATA_DIR` outside generated source and disposable build storage.
A failed build can leave an older public export in place; verify its artifact identity
against the current result before using it.

## Logs and incident evidence

Foreground stdout/stderr contains startup and diagnostic output. Preserve the relevant
error, artifact identity and sanitized sync status when investigating a failure. Exclude
bearer values, private URLs, raw fleet snapshots and private settings from public issues.
Runtime checks write local reports under `_build/`; these are ignored by Git.

There is no configured packaged installer, release pipeline or fleet deployment in this
workspace. GitHub persistence is source publication, not installation or a release.
