---
name: ddd-domain-contract-validator
description: Validar consistencia DDD y contratos a partir de DSP/SSP, contexto gobernado y outputs DDD previos, con trazabilidad y revisión humana.
metadata:
  version: "0.1.0"
---
# ddd-domain-contract-validator

## Objetivo
Validar consistencia DDD y contratos. Hallazgos, matriz de trazabilidad, cobertura, conflictos y recomendaciones de gate sin autoaprobar.

## Contrato de entrada
Recibir `task-id`, `run-id`, `scope-manifest.yaml`, `execution-plan.yaml`, referencias versionadas y los outputs aprobados de predecesores según DAG. Si faltan insumos críticos: BLOCKED.

## Procedimiento
1. Verificar entradas y fuentes con provenance.
2. Identificar hechos, inferencias, contradicciones y decisiones pendientes.
3. Elaborar diseño con alternativas y trade-offs, sin exceder alcance.
4. Revisar coherencia con bounded contexts, ubiquitous language, invariantes y contratos.
5. Guardar salida tipada `CFR-domain-validation.md` (type `CFR`) en la ruta resuelta por `assets/pathmap.json` y reporte en `.comsatel/ddd-domain-design/runs/<run-id>/task-results/<task-id>.yaml`.

## Contrato de salida
Documento OKF `CFR-domain-validation.md` con `type: CFR`, `id` estable, evidencias y trazabilidad; `task-results` con `task_id`, `skill`, `status`, `inputs`, `outputs`, `evidence`, `findings`, `questions`, `started_at`, `finished_at`. Estados: DONE, BLOCKED, FAILED. DONE no significa aprobado.

## Gate
Requiere revisión humana cuando haya cambio de límite, contrato o regla; no autoaprobar.

## Reglas obligatorias
- Leer únicamente fuentes disponibles y declarar archivos ausentes; no inventar contenido de DSP, SSP, RCP, ADR, User Stories ni KB.
- El DSP gobierna alcance; SSP organiza trabajo y no lo amplía. Distinguir hipótesis de decisiones aprobadas.
- Preservar IDs y trazabilidad fuente→afirmación→decisión→artefacto; indicar procedencia, versión y skill productor en frontmatter compatible con OKF v0.2 según perfil corporativo disponible. No declarar conformidad si no se cuenta con dicho perfil.
- No editar artefactos de otros skills ni aprobar gates; emitir hallazgos y solicitud de revisión humana.
- No asumir que bounded context = microservicio, aggregate = tabla, domain event = evento de integración.
- Registrar ejecución con estado y evidencias en el plan gestionado por orchestrator.


## Norma corporativa objetivo — STD-OKF-001 v0.1.0-stable
- Antes de producir Markdown conceptual, leer `standards/STD-OKF-001-v0.1.0-stable.md` (ruta relativa a la raíz del plugin). Si no está disponible, bloquear publicación.
- Distinguir tres niveles: OKF mínimo, perfil COMSATEL y publicación. Ejecutar `python scripts/okf_validate.py <archivo> --level profile` antes de revisión y `--level publish --run <directorio-run>` antes de publicación.
- Los documentos conceptuales deben usar exclusivamente los campos corporativos `type`, `id`, `title`, `description`, `version`, `status`, `owner`, `classification`, `tags`, `generated.by`, `generated.at`, `sources`, y condicionalmente `product`, `bounded_context_id`, `pack`, `skill`, `related`. No crear aliases `artifact_type`, `source_refs`, `reviewed_by`, `lifecycle_status`.
- Usar `type: BC` para Bounded Context, `type: CTX` para Context Map y los tipos aprobados `AGG`, `VO`, `EVT` para especificaciones separadas. No crear otros tipos nuevos (incluido SSP) sin control de cambios. Documentos operativos YAML del orchestrator no son OKF.
- `status: stable` no significa gate aprobado; nunca fabricar `verified`, `sources`, aprobaciones ni fechas históricas. `index.md` y `log.md` tienen tratamiento reservado.
- `related` requiere enlaces Markdown correspondientes en el cuerpo; preservar metadatos desconocidos al consumir documentos de terceros.

## Artefactos DDD v1.1.0
Generar especificaciones AGG/VO/EVT independientes cuando corresponda, con `bounded_context_id`, `pack`, `skill`, fuentes y relaciones BC/CTX. Validar cada artefacto con `scripts/okf_validate.py` antes de marcar la tarea como completada.

## Destino obligatorio v0.4.2
- Publicar todos los resultados propios del skill en `<workspace>/architecture/<ruta-por-tipo>/`, organizados por `run-id` para evitar colisiones: `architecture/<ruta-por-tipo>/`. El reporte operativo de tarea se conserva en `.comsatel/ddd-domain-design/runs/<run-id>/task-results/`.
- No escribir resultados conceptuales en `.comsatel/ddd-domain-design/runs/<run-id>/artifacts/`; registrar en el ledger las rutas efectivas.

## Contrato obligatorio de rutas (pathmap v1.0.0)
- Leer `assets/pathmap.md` y utilizar `assets/pathmap.json` como mapa ejecutable. La raíz de las rutas es el **workspace**.
- Los seis skills especializados deben escribir cada documento en la subcarpeta `./architecture/` correspondiente a su `type` OKF. No usar `design/ddd/` ni carpetas por run para documentos de KB.
- El orchestrator es el único responsable de los archivos operativos en `.comsatel/ddd-domain-design/runs/<run-id>/`.
- El orchestrator resuelve y entrega a cada skill `workspace_root`, `run_id`, `document_type`, `output_path`, `pathmap_version`, `gate`; el skill devuelve `actual_output_path` y evidencia.
- Validar con `scripts/validate_pathmap.py verify --workspace <workspace> --kind <type-o-archivo> --file <ruta>` antes de declarar un output completo. Bloquear tipos no mapeados, rutas incorrectas y archivos inexistentes.
- Solo aceptar rutas alternativas por instrucción explícita del usuario, registrando excepción y evidencia en el plan.
- Los Markdown conceptuales deben cumplir `STD-OKF-001-v0.1.0-stable.md` antes de gate y publicación.

## Plantilla de salida (v2.2.0)
- Las plantillas de este skill están en su propia carpeta: `skills/ddd-domain-contract-validator/templates/` (en las rutas de abajo, `templates/` es esa carpeta).
- Usar `templates/cfr-okf.md` para `CFR-domain-validation.md`: OKF `type: CFR` (tipo asignado por `assets/pathmap.json`, `typed_outputs`).
- Generar `domain-design-contract.yaml` a partir de `templates/domain-design-contract.yaml` y verificarlo con `scripts/workflow.py validate-contract`.
- Validar `CFR-domain-validation.md` con `scripts/validate_pathmap.py verify --kind CFR-domain-validation.md` y `scripts/okf_validate.py --level profile`, antes de pasar la tarea a NEEDS_REVIEW.
