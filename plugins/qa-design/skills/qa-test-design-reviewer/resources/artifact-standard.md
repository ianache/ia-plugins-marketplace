# Metadatos Markdown (STD-OKF-001)

Todo documento `.md` entregable lleva frontmatter YAML con: `type` (sigla del catálogo de `pack.yaml`), `id`, `title`,
`description`, `version` (SemVer entre comillas), `status` (`draft`, `stable`, `deprecated`), `owner`, `classification`,
`tags`, `generated` (`by`, `at`), `sources`, y los campos condicionales `pack`, `skill`, `product`, `related`.
No usar `artifact_type`, `source_refs`, `okf`, `kind` ni estados operativos en `status`.
El readiness de un TC (`READY`, `BLOCKED_CLARIFICATION`, `DEFERRED`) vive en `coverage-matrix.yaml`, no en el frontmatter.
Los YAML de apoyo (matrices, trazabilidad, gate-report) se referencian desde el Markdown OKF como artefactos adjuntos.
Los diagramas Mermaid se incrustan en bloques ```mermaid; el render no se presume sin motor verificado.
