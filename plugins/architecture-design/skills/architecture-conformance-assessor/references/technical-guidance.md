# Guía técnica — architecture-conformance-assessor

Mantener las disciplinas originales como subprocedimientos dentro de este skill, no como skills adicionales publicados. Preservar las perspectivas Applications, Integration, Data, Infrastructure; ASR quality scenarios; ADR lifecycle; conformance, drift, fitness, governance y knowledge curation según aplique. Separar baseline As-Is de To-Be. No asumir herramientas ni repositorios disponibles.

## Política de rutas
Consultar `assets/pathmap.md` de la raíz del plugin: entregables especializados en `./architecture/` (ADR `adrs/`, ASR `asrs/`); solo el orchestrator escribe control en `.comsatel/architecture-design/runs/<run-id>/`. Overrides únicamente por instrucción explícita.

## Enrutamiento obligatorio
Usar el contrato `document_type`/`output_dir` emitido por el orchestrator y el `assets/pathmap.md` de la raíz del plugin; bloquear rutas no mapeadas.
