# Readable specifications

[Documentation](../README.md)

The application is authored as behavioral requirements rather than maintained generated
source. Begin with `components/tracker/component.md`, then its named
runtime, MAC integration, quality and visual documents. These specify externally observable
behavior and the scenarios needed to establish it.

A useful requirement names a trigger and result: for example, an unchanged upstream poll
must leave task revisions and event counts unchanged, while a dependency-only change
advances exactly once. Distinguish confirmed upstream absence from an unavailable fleet;
those cases authorize different behavior.

Keep product behavior in the Component, target policy in selected Flavors, and conversion
technique in exact skills. Keep real credentials, private snapshots and temporary diagnostic
paths out of specification authority. `component.lock.json` records framework resolution;
it is not a second handwritten dependency specification.

When a generated candidate fails, preserve the evidence, identify the owning requirement,
and refine that authority where needed. Regenerate and verify the exact new export. A
passing helper or provisional module does not prove the final service and browser.

The [design traceability rule](../architecture/design-traceability.md) links explanation
to authority. [Development](development.md) covers the complete workflow.
