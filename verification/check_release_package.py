#!/usr/bin/env python3
"""Verify npm release bytes and every archive member before extracting a new copy."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify(archive, manifest, destination):
    report = json.loads(manifest.read_text())
    if report['schema'] != 'project-tracker/npm-release-package@1':
        raise ValueError('Unsupported release manifest')
    if archive.name != report['artifact'] or archive.stat().st_size != report['bytes']:
        raise ValueError('Archive name or size mismatch')
    if sha256(archive.read_bytes()) != report['sha256']:
        raise ValueError('Archive checksum mismatch')
    expected = report['packaged_files']
    if not 1 <= len(expected) <= 4096:
        raise ValueError('Invalid archive file count')
    members = {}
    total = 0
    with tarfile.open(archive, 'r:gz') as bundle:
        for member in bundle:
            path = PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or '..' in path.parts
                    or not path.parts or path.parts[0] != 'package' or len(path.parts) < 2
                    or '\\' in member.name or member.size > 64 * 1024 * 1024):
                raise ValueError('Unsafe archive member')
            name = path.relative_to('package').as_posix()
            if name in members or name not in expected:
                raise ValueError('Duplicate or undeclared archive member')
            total += member.size
            if total > 256 * 1024 * 1024:
                raise ValueError('Archive expands beyond the release size budget')
            data = bundle.extractfile(member).read()
            if sha256(data) != expected[name]:
                raise ValueError('Archive member checksum mismatch')
            members[name] = data
    if set(members) != set(expected):
        raise ValueError('Required package files are missing')
    for name, checksum in report['source_files'].items():
        packaged_name = 'npm-shrinkwrap.json' if name == 'package-lock.json' else name
        if packaged_name not in members or sha256(members[packaged_name]) != checksum:
            raise ValueError('An accepted source file was changed or omitted')
    package = json.loads(members['package.json'])
    if package['name'] != 'project-tracker' or package['version'] != report['version']:
        raise ValueError('Package metadata mismatch')
    if destination.exists():
        raise ValueError('Extraction requires a new destination')
    destination.mkdir(parents=True)
    for name, data in members.items():
        target = destination / 'package' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return {'ok': True, 'sha256': report['sha256'], 'files': len(members),
            'component_revision': report['component_revision'],
            'source': str(destination / 'package')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--extract', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.manifest, args.extract)))


if __name__ == '__main__':
    main()
