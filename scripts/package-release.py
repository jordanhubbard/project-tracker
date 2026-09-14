#!/usr/bin/env python3
"""Pack an accepted tracker export without changing its generated source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files(root):
    result = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if 'node_modules' in relative.parts:
            continue
        if path.is_symlink():
            raise ValueError(f'Symlink outside dependencies: {relative}')
        if path.is_file():
            result[relative.as_posix()] = digest(path.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--build-result', type=Path, required=True)
    parser.add_argument('--cache-entry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--node', default=shutil.which('node') or '/opt/homebrew/opt/node@22/bin/node')
    args = parser.parse_args()
    root = args.project.resolve(strict=True)
    lock = json.loads((root / 'components/tracker/component.lock.json').read_text())
    revision = lock['root_revision']['digest']
    source = root / 'generated/artifacts/tracker' / ('artifact-' + revision[:20]) / 'source'
    build = json.loads(args.build_result.read_text())
    if not build.get('ok') or not build.get('result', {}).get('passed'):
        raise ValueError('A successful supported application build is required')
    result = build['result']
    if Path(result['artifact']).resolve() != source.parent.resolve():
        raise ValueError('Build result does not identify the current component export')
    tests = result['test_summary']
    if tests['failed'] or tests['skipped'] or tests['passed'] < 1:
        raise ValueError('Native acceptance is incomplete')
    receipt = json.loads((root / 'verification/current.json').read_text())
    lock_identity = 'sha256:' + digest(json.dumps(lock, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
    if lock_identity not in receipt['component_lock_identities']:
        raise ValueError('Acceptance receipt does not bind the current component lock')
    original = files(source)
    entry_path = args.cache_entry.resolve(strict=True)
    entry = json.loads(entry_path.read_text())
    if digest(entry_path.read_bytes()) != entry_path.stem:
        raise ValueError('Accepted-cache entry digest mismatch')
    if 'sha256:' + entry['derivation']['component_lock_identity']['digest'] != lock_identity:
        raise ValueError('Accepted source belongs to a different component lock')
    expected_source = {}
    for item in entry['source_files']:
        if not item['path'].startswith('source/'):
            raise ValueError('Unexpected accepted source layout')
        expected_source[item['path'][7:]] = item['blob']['digest']
    if original != expected_source:
        raise ValueError('Public export differs from the exact accepted source cache entry')
    resolved_digest = entry['resolved_sbom']['digest']
    resolved_sbom = entry_path.parents[2] / 'cas/blobs/sha256' / resolved_digest[:2] / resolved_digest
    if digest(resolved_sbom.read_bytes()) != resolved_digest:
        raise ValueError('Resolved SBOM digest mismatch')
    source_sbom_digest = entry['source_sbom']['digest']
    source_sbom = entry_path.parents[2] / 'cas/blobs/sha256' / source_sbom_digest[:2] / source_sbom_digest
    if digest(source_sbom.read_bytes()) != source_sbom_digest or json.loads(source_sbom.read_text()).get('bomFormat') != 'CycloneDX':
        raise ValueError('Source CycloneDX SBOM mismatch')
    version = json.loads((source / 'package.json').read_text())['version']
    if version != json.loads((root / 'literate.project.json').read_text())['version']:
        raise ValueError('Project and package versions differ')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, PATH=str(Path(args.node).resolve().parent) + os.pathsep + os.environ.get('PATH', ''))
    npm = shutil.which('npm', path=environment['PATH'])
    if not npm:
        raise ValueError('npm is unavailable')
    sbom = json.loads(resolved_sbom.read_text())
    if sbom.get('bomFormat') != 'CycloneDX':
        raise ValueError('Expected the lifecycle resolved CycloneDX SBOM')
    with tempfile.TemporaryDirectory(prefix='tracker-pack-') as temporary:
        staging = Path(temporary) / 'package'
        shutil.copytree(source, staging, ignore=shutil.ignore_patterns('node_modules'))
        # npm intentionally excludes package-lock.json; shrinkwrap preserves its exact bytes.
        shutil.copyfile(staging / 'package-lock.json', staging / 'npm-shrinkwrap.json')
        for name in ('LICENSE',):
            shutil.copyfile(root / name, staging / name)
        collateral = staging / 'release'
        collateral.mkdir()
        shutil.copyfile(resolved_sbom, collateral / 'resolved-sbom.cdx.json')
        shutil.copyfile(source_sbom, collateral / 'source-sbom.cdx.json')
        shutil.copyfile(root / 'verification/current.json', collateral / 'acceptance.json')
        specs = collateral / 'specification'
        specs.mkdir()
        for path in (root / 'components/tracker').iterdir():
            if path.suffix in ('.md', '.json'):
                shutil.copyfile(path, specs / path.name)
        install = f'''# Project Tracker {version}\n\nRequires macOS, Node.js 22.23.2 or newer, npm, and Git 2.30 or newer.\n\nExtract the GitHub release archive into a new directory, then run:\n\n```sh\ncd package\nnpm ci --ignore-scripts\nnode main.js '["service", "--host", "127.0.0.1", "--port", "8765"]'\n```\n\nOpen http://127.0.0.1:8765. Configure MAC and LLM connections through Settings.\nThe default data directory is ~/Library/Application Support/project-tracker.\nSet TRACKER_DATA_DIR to select another private persistent directory. Keep that\ndirectory outside this package so upgrades retain data. Stop the old process\nbefore starting an upgrade. Back up the data directory while the service is stopped.\n\nThe package stays private to prevent accidental npm registry publication; it is\ndistributed as a GitHub archive. npm-shrinkwrap.json is the exact accepted lockfile.\n\n[Complete manual](https://github.com/jordanhubbard/project-tracker/blob/v{version}/docs/README.md)\n'''
        (staging / 'INSTALL.md').write_text(install)
        expected = files(staging)
        expected.pop('package-lock.json')
        packed = subprocess.run([npm, 'pack', '--ignore-scripts', '--json', '--pack-destination', str(output)], cwd=staging, env=environment, text=True, capture_output=True, check=True)
        info = json.loads(packed.stdout)
        if len(info) != 1:
            raise ValueError('Expected exactly one npm package')
        archive = output / info[0]['filename']
        actual = {}
        with tarfile.open(archive, 'r:gz') as bundle:
            for member in bundle:
                if not member.isfile() or not member.name.startswith('package/'):
                    raise ValueError('Unexpected npm archive entry')
                name = member.name.removeprefix('package/')
                if name in actual or '..' in Path(name).parts or Path(name).is_absolute():
                    raise ValueError('Unsafe or duplicate npm archive entry')
                actual[name] = digest(bundle.extractfile(member).read())
        if actual != expected:
            raise ValueError(f'Archive differs from declared files: missing={sorted(expected.keys()-actual.keys())}, extra={sorted(actual.keys()-expected.keys())}')
        if files(source) != original:
            raise ValueError('Generated source changed during packaging')
        report = {
            'schema': 'project-tracker/npm-release-package@1', 'version': version,
            'artifact': archive.name, 'sha256': digest(archive.read_bytes()),
            'bytes': archive.stat().st_size, 'component_revision': revision,
            'component_lock_identity': lock_identity, 'acceptance_receipt_identity': receipt['receipt_identity'],
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
            'build_result_sha256': digest(args.build_result.read_bytes()),
            'accepted_cache_entry_identity': 'sha256:' + entry_path.stem,
            'source_files': original, 'packaged_files': actual,
            'npm_version': subprocess.check_output([npm, '--version'], env=environment, text=True).strip(),
            'node_version': subprocess.check_output([args.node, '--version'], text=True).strip(),
            'native_tests': tests,
        }
        manifest = output / 'package-manifest.json'
        manifest.write_text(json.dumps(report, indent=2) + '\n')
        (output / 'SHA256SUMS').write_text(f"{report['sha256']}  {archive.name}\n{digest(manifest.read_bytes())}  {manifest.name}\n")
        print(json.dumps({'ok': True, 'archive': str(archive), 'manifest': str(manifest), 'files': len(actual)}))


if __name__ == '__main__':
    main()
