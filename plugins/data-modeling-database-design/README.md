# Data Modeling & Database Design Pack v1.3.0 (DTC-102)

Plugin Claude compatible en estructura; ejecución real en Claude Code pendiente.

**6 skills + 1 orchestrator.** Escenarios Greenfield/Brownfield/Evolution. Entradas: modelo conceptual AF, RCP/DSP/SSP, DDD BC/CTX/AGG/VO/EVT, FDT, ADR, codebase/DDL/Flyway. Salidas OKF: DBR/LDM/PDM/DBM/DDR. T01 agrega ownership al LDM; T05 produce el DDR tipado. No se crean nuevos `type` fuera de STD-OKF-001 v1.11.0-stable.

Los skills producen resultados bajo `design/database/<run-id>` y el orchestrator mantiene controles bajo `.comsatel/data-modeling-database-design/runs/<run-id>` (`execution-plan.json`, `gate-register.json`, `scope-manifest.json`). Cada tarea pasa por `PENDING`, `IN_PROGRESS`, `NEEDS_REVIEW` y `DONE` (más `BLOCKED` y `FAILED`), con historial de transiciones. Documentación completa en [DOCUMENTACION.md](DOCUMENTACION.md).

## Escenarios y gates
G0 alcance y fuentes. Cada gate posterior tiene un significado fijo y cada escenario usa solo los que aplican:

| Gate | Cierra | Greenfield | Brownfield | Evolution |
| :-: | :--- | :-: | :-: | :-: |
| G1 | Reconstrucción As-Is (`DBR`) | — | sí | sí |
| G2 | Ownership de datos | sí | sí | sí |
| G3 | Modelo lógico (`LDM`) | sí | — | sí |
| G4 | Modelo físico (`PDM`) | sí | — | sí |
| G5 | Migración y compatibilidad (`DBM`) | sí (migración inicial) | — | sí |
| G6 | Validación y handoff | sí | sí | sí |

El CLI registra declaraciones de aprobación (el actor debe empezar por `human:`), pero **no autentica aprobadores**.

## Handoff
Publicar documentos gobernados en KB y migraciones Flyway en repositorio de microservicio únicamente mediante MR, usando rutas determinadas por ADR y convenciones reales. Ninguna publicación automática.

## Limitaciones
Validación del workflow es estructural; no ejecuta skills automáticamente, no analiza bases reales ni valida SQL, Mermaid o semántica OKF. La conformidad documental final requiere validadores adicionales y revisión humana. Las corridas creadas con una versión anterior del CLI (sin `schema_version` igual a la actual) se rechazan: hay que crear una nueva.
