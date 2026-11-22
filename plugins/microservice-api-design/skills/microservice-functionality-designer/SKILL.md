---
name: microservice-functionality-designer
description: Produce Fichas de Diseño Técnico de Funcionalidad (FDT) para capacidades y endpoints, trazando requisitos, reglas, datos, interacciones hexagonales, secuencias, pruebas y handoff.
---
# Microservice Functionality Designer

## Cuándo activar
Tras disponer de límites, arquitectura y contratos de API/eventos, para Greenfield, Brownfield y Evolution. Una funcionalidad puede corresponder a varios endpoints o ninguno (event-driven).

## Inputs contractuales
DSP/SSP/RCP, US y criterios de aceptación, BR, BC/AGG/VO/EVT, ADR, C4, contratos OpenAPI/AsyncAPI, LDM/PDM disponibles, inventario de tests, y evidencia As-Is para sistemas existentes. No inventar documentos faltantes.

## Procedimiento
1. Inventariar funcionalidades dentro del scope, IDs estables, operaciones y consumidores.
2. Para cada funcionalidad producir `functionalities/<FDT-ID>-<slug>.md` con STD-OKF-001 v1.11.0-stable, `type: FDT`, `service_id`, `bounded_context_id`, `pack`, `skill`, `sources` reales.
3. Especificar entradas, salidas, errores, reglas e invariantes, operaciones de datos requeridas, seguridad/tenant, transacciones/idempotencia, observabilidad, escenarios y casos de prueba.
4. Dibujar secuencia Mermaid entre consumidor, inbound adapter, application layer, domain, outbound ports y adapters/proveedores; documentar flujos alternos y fallos. Reutilizar SEQ con enlace si corresponde.
5. Para Brownfield distinguir comportamiento observado de comportamiento requerido; para Evolution registrar delta, compatibilidad y pruebas de regresión.
6. Ejecutar `python scripts/fdt_validate.py <ruta>`; registrar evidencia y hallazgos antes de pasar la tarea a DONE.

## Gate FUNCTIONALITY_DESIGN_READY
Cada funcionalidad de alcance tiene FDT; ninguna referencia obligatoria sin resolver; OpenAPI `operationId` alineado; fuentes y escenarios verificables; diagramas y puertos coherentes; aprobación humana para publicar. El validador automatizado verifica solo estructura, no la verdad semántica.

## Outputs
`design/microservices/<servicio>/functionalities/*.md`, índice `functionalities/fdt-manifest.yaml`, hallazgos y evidencia en el ledger. La publicación a `codebase/<MICROSERVICIO>/docs/functionalities/` es mediante MR, sin escritura directa automática.


## Output Pathmap obligatorio
- Leer el contrato de ejecución recibido del orchestrator. No elegir el directorio por cuenta propia.
- Usar `assets/pathmap.md` y `assets/pathmap.json` (raíz del plugin); validar con `scripts/validate_pathmap.py`.
- Escribir entregables especializados en la ruta asignada por el pathmap (`design/` o `codebase/<servicio>/`); reportar `document_type`, `output_path`, `pathmap_version` y evidencia de validación.
- Una ruta diferente solo procede por instrucción explícita del usuario y debe quedar registrada en el ledger.
- El orchestrator mantiene planes, gates y ledger bajo `.comsatel/microservice-api-design/runs/<run-id>/`.
- Los Markdown generados requieren frontmatter conforme a `STD-OKF-001 v1.11.0-stable`, sin inventar tipos documentales aprobados.
