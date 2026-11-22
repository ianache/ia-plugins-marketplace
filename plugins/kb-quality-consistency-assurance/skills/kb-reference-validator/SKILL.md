---
name: kb-reference-validator
description: Validar enlaces, relaciones, provenance y referencias de artefactos. Usar cuando se requiera esta función en un workflow de aseguramiento de KB.
metadata:
  version: "0.1.0"
---
# kb-reference-validator

## Propósito
Validar enlaces, relaciones, provenance y referencias de artefactos.

## Entradas contractuales
`source_manifest.yaml, documents, artifact_index.yaml`. Las entradas deben estar ancladas a repositorio, rama y commit SHA; registrar ausencias como BLOCKED, sin inventar evidencia.

## Procedimiento
Resolver referencias contra snapshot y registrar faltantes, rotas, ambiguas, obsoletas o externas no verificables.

## Salidas contractuales
`reference-findings.yaml, referential-gate.yaml`. Producir los artefactos dentro de `.comsatel/kb-quality-consistency-assurance/runs/<run_id>/`; documentos Markdown conceptuales con frontmatter OKF v0.2 y perfil corporativo cuando aplique; YAML operativo no es un documento OKF.

## Reglas obligatorias
- Respetar la fuente de verdad Git; MCP y WebDAV son vistas de lectura, no fuentes autoritativas.
- No alterar archivos gobernados ni hacer commit/merge sin autorización humana explícita.
- Adjuntar evidencia verificable (ruta, revisión SHA, sección/línea o excerpt y hash cuando esté disponible).
- Separar `confirmed`, `suspected` y `unverified`; el análisis LLM por sí solo no convierte una sospecha en bloqueo definitivo.
- Ejecutar el gate de salida solo tras producir sus entradas. Los gates no son prerrequisitos de las tareas que evalúan.
- Tratar `STD-OKF-001` como perfil corporativo versionado: la copia vigente es `standards/STD-OKF-001-v0.1.0-stable.md` (estable, aprobada).

## Recursos
- `../../references/contracts.md`
- `../../references/gates.md`
- `../../references/policy.md`
