# Contrato del orchestrator

G0: objetivo, producto, alcance, fuentes autorizadas y owner.
G1: `af-evidence-context-designer` -> RCP y evidencia.
G2: gate humano de línea base de negocio (sin skill): evidencia = handoff G6 de `business-knowledge` (BR, IMD, TRM) o decisión humana explícita.
G3: `af-user-story-designer` -> HU por archivo, EPC opcionales por RCP (agrupan HU del mismo RCP) y backlog delta. G3 no aprueba una épica que cite una HU inexistente, que incluya una HU ya agrupada en otra épica o cuyos criterios no se tracen a criterios de sus historias.
G4: `af-acceptance-quality-reviewer` -> revisión de criterios, DoR y cobertura.
G5: `af-functional-impact-mapper` -> mapa de impactos y análisis funcional.
G6: `af-requirements-pack-publisher` -> trazabilidad E2E y handoff.

Todo paso devuelve `inputs`, `outputs`, `readiness`, `gate`, `evidence`, `open_questions`, `owner` y `approved_by` (solo cuando exista aprobación externa).
