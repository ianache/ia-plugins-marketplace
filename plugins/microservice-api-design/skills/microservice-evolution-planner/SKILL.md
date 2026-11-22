---
name: microservice-evolution-planner
description: Evolución y compatibilidad para microservicios Greenfield, Brownfield o Evolution con trazabilidad a KB y ADR.
---
# Evolución y compatibilidad

## Responsabilidad
Comparar As-Is/To-Be, breaking changes, consumidores, datos, migraciones, rollout, rollback y riesgos; greenfield: justificar N/A.

## Entradas
`scope-manifest.yaml`, artefactos DDD `BC/CTX/AGG/VO/EVT`, ADR, DSP/SSP si aplica, KB `codebase/<MICROSERVICIO>`, y repositorios/commits cuando existan. No inventar fuentes ausentes.

## Salida
`design/microservices/<servicio>/evolution/impact-analysis.md`; si es Markdown conceptual, frontmatter y provenance STD-OKF-001 v1.11.0-stable; YAML operativo sin frontmatter OKF. Mantener `sources` y enlaces a evidencias, y declarar incertidumbre.

## Contrato y gate
La tarea del orchestrator especifica inputs, outputs, acceptance y gate de entrada. Entregar evidencia verificable y revisión antes de DONE. No hacer push ni Merge Request sin autorización explícita.


## Output Pathmap obligatorio
- Leer el contrato de ejecución recibido del orchestrator. No elegir el directorio por cuenta propia.
- Usar `assets/pathmap.md` y `assets/pathmap.json` (raíz del plugin); validar con `scripts/validate_pathmap.py`.
- Escribir entregables especializados en la ruta asignada por el pathmap (`design/` o `codebase/<servicio>/`); reportar `document_type`, `output_path`, `pathmap_version` y evidencia de validación.
- Una ruta diferente solo procede por instrucción explícita del usuario y debe quedar registrada en el ledger.
- El orchestrator mantiene planes, gates y ledger bajo `.comsatel/microservice-api-design/runs/<run-id>/`.
- Los Markdown generados requieren frontmatter conforme a `STD-OKF-001 v1.11.0-stable`, sin inventar tipos documentales aprobados.
