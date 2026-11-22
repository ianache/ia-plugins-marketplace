# Contrato af-user-story-designer

- Gate: G3
- Inputs: RCP, reglas y catálogo HUC
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado si existe dependencia.
- Outputs: HU por archivo; EPC por archivo (opcional, agrupa HU del mismo RCP); backlog-delta; INVEST
- Postcondición: historias trazadas sin inventar reglas, con ID `RCP-NNN-US-NNN` globalmente único (`scripts/us_ids.py check` con 0 errores, incluidas las ramas abiertas y las otras KB). Cada EPC cita en `related` historias existentes, sin que una historia pertenezca a dos épicas, y cada criterio de la épica se traza a criterios de sus historias.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha/versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado de gate.

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
