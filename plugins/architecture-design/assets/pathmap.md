# Architecture Design — Workspace Output Pathmap

**Scope:** all six specialized architecture skills and the architecture orchestrator.  
**Workspace root:** repository/workspace where the user invoked the plugin; never the plugin installation directory.

## Mandatory rules

1. Resolve every specialized skill output by `document type` **before** writing. The orchestrator reads this file at G0 and passes the resolved absolute/relative destination to each skill in its task contract.
2. The default root is the one `pathmap.json` defines. Never use `design/architecture/`, `architecture/<run-id>/`, or the orchestrator control folder for specialized outputs.
3. The only exception is a **user-explicit output path**; record the original instruction, resolved path, actor, and rationale in the execution plan. A skill cannot self-authorize an override.
4. Unknown/unmapped `document type` is **BLOCKED** until the orchestrator requests a mapping decision; do not silently place it at the architecture root.
5. `type` is the OKF frontmatter `type`, not a guess from the filename. Validate both type and resolved path; do not infer provenance or approval.
6. Existing files: do not overwrite without an explicit evolution/versioning decision; preserve stable references and links.
7. The orchestrator alone writes execution plans, state, gate registers, routing decisions and operational evidence in `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`). A JSON output manifest produced by a specialized skill is a delivery artifact and must be associated with its resolved deliverables, not stored as an orchestrator gate record.

## Document type → destination directory

El mapeo de cada tipo documental a su directorio (y los metadatos de cada artefacto) vive solo en [`pathmap.json`](pathmap.json), bajo `document_types` y `artifacts`; su versión está en `pathmap_version`. Este archivo no repite ese contenido. Las convenciones propuestas y las confirmadas por el usuario se distinguen en `artifacts.<tipo>.basis`.

Do **not** generate `RCP` or requirements-owned artifacts from Architecture Design merely to fill a directory. Requirements documents remain owned by Requirements Engineering. Other approved types may be added to this table only through reviewed change control. Paths are not a substitute for the corporate type registry in STD-OKF-001 v0.1.0-stable.

## Per-task handoff contract (orchestrator → specialized skill)

```json
{
  "run_id": "RUN-001",
  "workspace_root": ".",
  "skill": "architecture-decision-governor",
  "document_type": "ADR",
  "output_dir": "<directory of the type in pathmap.json>",
  "pathmap_version": "<pathmap_version>",
  "override": null,
  "gate": "G3",
  "inputs": ["approved-evidence-ref"],
  "required_standard": "STD-OKF-001-v0.1.0-stable"
}
```

A specialized skill MUST verify the contract's `document_type` and `output_dir` against this map, create the directory when permitted, validate its OKF frontmatter, and return a manifest with each actual file path. It must refuse a missing mapping or mismatched path.

## Gate checks

- **G0:** orchestrator loads pathmap, records its version and creates per-task routing contracts.
- **G1–G5:** each producing skill reports `type`, destination, validation result and source provenance; gate blocks on unresolved route.
- **G6:** orchestrator verifies all specialized outputs with `scripts/validate_pathmap.py`, then verifies OKF metadata and human approvals before handoff.
- **Override:** only user-explicit paths, documented and validated to remain within the workspace unless the user explicitly directs otherwise.
