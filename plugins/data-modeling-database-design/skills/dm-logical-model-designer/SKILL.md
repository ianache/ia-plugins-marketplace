---
name: dm-logical-model-designer
description: Transformar modelo conceptual, BC, AGG, VO, EVT y FDT en modelo lógico; cardinalidad, claves, invariantes y trazabilidad.
---
# dm-logical-model-designer

## Objetivo
Transformar modelo conceptual, BC, AGG, VO, EVT y FDT en modelo lógico; cardinalidad, claves, invariantes y trazabilidad.

## Entradas y precondiciones
- `scope-manifest.json`, ADR aplicables, fuentes reales con ruta/commit y permisos.
- Context Pack de requerimientos, modelo conceptual AF y artefactos DDD (`BC`, `CTX`, `AGG`, `VO`, `EVT`) cuando correspondan.
- FDT, contratos OpenAPI, inventario de servicios y esquemas, si existen.
- Si falta una fuente crítica, registrar bloqueo; nunca inventar esquemas, reglas o evidencia.

## Proceso
1. Leer `execution-plan.json` y `gate-register.json`; verificar dependencias y gate de entrada.
2. Inspeccionar fuentes, distinguir hechos observados de hipótesis y decisiones To-Be.
3. Producir el resultado con referencias a IDs y fuentes, siguiendo ADR y estándares.
4. Ejecutar `python scripts/validate.py <documento>.md` (delegado en `scripts/validate_okf.py`) y `scripts/validate_pathmap.py --run-id <run-id> --file <ruta> --type LDM`; registrar evidencia de salida para que el orchestrator cierre la tarea.

## Salida
- `design/database/<run-id>/to-be/logical-data-model.md` (actualización del `LDM` creado por T01; preservar `id`, incorporar entidades, claves y relaciones, incrementar `version` y actualizar `skill`/`generated`).
- Referencias trazables, riesgos, incertidumbres, preguntas y propuesta de gate.

## Reglas
- Documentos OKF (`STD-OKF-001 v1.11.0-stable`): metadatos obligatorios, SemVer, `generated.by`, `generated.at`, `sources`, `pack`, `skill`, `bounded_context_id` y `schema_id` cuando apliquen.
- No publicar ni modificar repositorios sin aprobación humana; no asumir BC=esquema ni AGG=tabla.
- La ubicación final de migraciones depende de ADR y convenciones verificadas de la codebase.
