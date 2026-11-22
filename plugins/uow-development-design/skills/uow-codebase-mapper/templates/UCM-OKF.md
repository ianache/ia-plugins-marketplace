---
type: UCM
title: "UOW Codebase Map"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-UCM-001
version: "1.0.0"
status: draft
owner: team:engineering
classification: internal
tags: [uow, ucm]
product: <PRODUCTO>
pack: uow-development-design
skill: uow-codebase-mapper
generated:
  by: uow-codebase-mapper/1.1.0
  at: "<ISO-8601 con zona>"
sources:
  - id: us
    resource: "<ruta o URI de la US>"
    version: "<versión>"
    title: "<US-ID>@<versión>"
uow_ref: UOW-001
service_id: <servicio>
authored_by: [<persona o agente>]
repository: {project: <proyecto>, target_branch: <rama>, source_ref: <ref>, source_commit: <sha>}
allowed_paths: []
forbidden_paths: []
adr_refs: []
existing_code_analysis: {performed: false, summary_ref: null}
backward_compatibility: {assessed: false, summary: null}   # obligatorio con summary cuando el modo es EVOLUTION
rollback: {defined: false, summary: null}                  # obligatorio con summary cuando el modo es EVOLUTION
---
# UCM-XXX — <título>
## Repositorio y referencia base
## Rutas permitidas
## Zonas prohibidas
## Convenciones y ADR
## Análisis del código existente
## Compatibilidad hacia atrás
<!-- Solo EVOLUTION: contratos, datos y consumidores afectados; qué sigue funcionando sin cambios. -->
## Rollback
<!-- Solo EVOLUTION: cómo revertir (orden, datos, banderas) y criterio para decidirlo. -->
## Migraciones y orden
## Provenance
