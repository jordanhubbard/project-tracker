---
name: "rust-ecosystem"
description: "Conventional Rust package layout and dependency authority."
metadata:
  author: "Literate AI maintainers <literate-ai-maintainers@users.noreply.github.com>"
schema: "urn:literate-ai:schema:v1:specification-to-source-skill"
skill_id: "rust-ecosystem"
version: "1.0.0"
title: "Rust ecosystem layout"
stages:
  - "plan"
  - "generate"
dependencies:
  - schema: "urn:literate-ai:schema:v1:skill-reference"
    skill_id: "repository-layout"
    version: "1.1.0"
    identity:
      schema: "urn:literate-ai:schema:v1:content-identity"
      algorithm: "sha256"
      digest: "39f0145075f349d8dac3bf0f00484c73a8588a3e9f3dd983240bac5dc4854a33"
limitations:
  - "Keep Cargo target output and package caches outside generated source under framework-owned object storage."
  - "Do not generate Cargo.lock; the authorized lifecycle derives it from registry requirements in a disposable build projection. Do not substitute mutable path or Git dependencies for registry packages."
trust: "repository-reviewed"
---
# Rust ecosystem layout

Use Cargo's conventional package layout with `Cargo.toml` at the package root,
implementation beneath `src/`, optional library code in `src/lib.rs`, binaries in
`src/main.rs` or declared `src/bin/` targets, and generated runtime-test modules reachable
from the exported binary. Keep registry requirements in the manifest; the authorized
lifecycle derives the exact registry closure and `Cargo.lock` outside admitted source.

Treat Cargo's target directory, registry cache, and compiler intermediates as derived
state. Honor the lifecycle-provided `CARGO_TARGET_DIR` beneath `OBJ_DIR`; never create a
`target/` directory in admitted source. Do not generate or commit `Cargo.lock`; the
post-authorization lifecycle derives and freezes it externally, then uses `--locked` for
metadata and builds so resolution cannot silently alter source authority.
