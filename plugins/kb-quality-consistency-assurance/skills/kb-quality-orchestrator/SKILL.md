---
name: kb-quality-orchestrator
description: Orquestar auditorías, revisión de cambios y remediación gobernada en KB OKF. Usar cuando se requiera esta función en un workflow de aseguramiento de KB.
metadata:
  version: "0.1.0"
---
# kb-quality-orchestrator

## Propósito
Orquestar auditorías, revisión de cambios y remediación gobernada en KB OKF.

## Entradas contractuales
`source_manifest.yaml, policy_profile.yaml, run_request.yaml`. Las entradas deben estar ancladas a repositorio, rama y commit SHA; registrar ausencias como BLOCKED, sin inventar evidencia.

## Procedimiento
Planificar tareas, verificar DAG, invocar especialistas, consolidar gates y exigir autorización de publicación.

## Salidas contractuales
`run-plan.yaml, gate-report.yaml, run-summary.md`. Producir los artefactos dentro de `.comsatel/kb-quality-consistency-assurance/runs/<run_id>/`; documentos Markdown conceptuales con frontmatter OKF v0.2 y perfil corporativo cuando aplique; YAML operativo no es un documento OKF.

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

## Workflow
1. Resolver `audit`, `change-review` o `remediation` y construir manifest de fuentes.
2. Generar `run-plan.yaml` y validar DAG con `../../scripts/validate_workflow.py` (relativo a esta carpeta; recibe el plan en JSON) ANTES de ejecutar.
3. Ejecutar validadores independientes en paralelo cuando las entradas estén listas; preservar snapshots.
4. Ejecutar G1–G5 después de las tareas productoras; G6 solo tras consolidación de evidencias y revisión humana.
5. Si un gate falla, abrir tareas de remediación; no aprobar gates artificialmente.
6. Registrar decisión humana para publicar; sin ella `publication-readiness` permanece `pending_approval`.

El plan por defecto es `T01` estructura → G1, `T02` referencias → G2, `T03` semántica → G3, `T04` cross-artifact → G4, `T05` impacto → G5, `T06` reporte → G6. Las tareas T01–T05 pueden ejecutarse en paralelo cuando sus datos estén disponibles; T06 depende de sus salidas. Nunca T02 → G1 si G1 requiere T02.
