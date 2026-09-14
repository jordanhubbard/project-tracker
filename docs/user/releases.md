# Releases

[Project guide](../README.md) → releases

Release archives are published on the
[GitHub releases page](https://github.com/jordanhubbard/project-tracker/releases).
A release is ready when its tag, package checksums and acceptance evidence agree.
The first release is being prepared as v1.0.0; consult that page for publication status.

## Install an archive

Use macOS with Node.js 22.23.2 or newer, npm, and Git 2.30 or newer. Download the
`.tgz`, `SHA256SUMS` and `package-manifest.json` assets from the same release.
In the download directory, verify the files before extraction:

```sh
shasum -a 256 -c SHA256SUMS
mkdir project-tracker-1.0.0
cd project-tracker-1.0.0
tar -xzf ../project-tracker-1.0.0.tgz
cd package
npm ci --ignore-scripts
node main.js '["service", "--host", "127.0.0.1", "--port", "8765"]'
```

Open `http://127.0.0.1:8765`. Configure MAC and LLM connections in Settings;
credentials stay on the backend. See [configuration](configuration.md) for access
tokens and [operations](operations.md) for durable storage and backups.

The package contains `npm-shrinkwrap.json`, copied byte for byte from the accepted
lockfile. `npm ci` installs that locked dependency tree. The package's private flag
prevents accidental npm registry publication and does not prevent archive use.

## Upgrade and back up

Stop the running process and back up its data directory. By default that directory
is `~/Library/Application Support/project-tracker`; `TRACKER_DATA_DIR` can select
another private location. Extract each new release into a separate directory,
install its locked dependencies, and start it with the same data-directory setting.
Keep persistent data outside the extracted package.

A filesystem backup should capture the stopped service's complete data directory,
including SQLite WAL files when present. Retain the old package and backup until
you have checked the new service's health, repositories and tasks. Do not run two
versions against the same writable database concurrently.

## Release evidence

`package-manifest.json` records the archive checksum, every packaged file checksum,
the original generated-source checksums, component revision, accepted-cache entry,
acceptance receipt identity and packaging tool versions. The archive also includes
installation instructions, the license, component specifications, source SBOM and
resolved CycloneDX SBOM. Checksums identify bytes; download them through the same
trusted GitHub release page.

Packaging verifies the complete file table before a new extraction. Acceptance
then runs against that extracted package with replayed dependencies, including
native diagnostics, synthetic authenticated MAC fixtures and browser/service
checks. These fixtures do not mutate the production MAC fleet. See
[verification](verification.md) for the scope and recorded results.

## Maintainer procedure

Follow the repository release skill for contribution disposition, accepted source,
clean release preparation, exact-commit checks, publication and remote verification.
For the first release, the user authorized the project's independent npm packaging
flow because installed LitAI 1.0.1 cannot construct `package-npm` packages. Upstream
[issue #411](https://github.com/NVIDIA-dev/literate-ai/issues/411) tracks native support
for LitAI 1.1. This exception applies to packaging; application acceptance still
uses the supported LitAI lifecycle.

Run `scripts/package-release.py --help` against the final accepted public export.
It requires the successful build result and exact accepted-cache entry, checks the
source against that entry, and writes a package plus manifest and checksums under
the selected output directory. `verification/check_release_package.py` independently
verifies the archive and extracts it into a new directory. Neither command publishes.

Hosted acceptance is being prepared to exercise the exact packaged revision.
Until its evidence is recorded, local packaging-tool checks do not establish
application CI or release publication.
