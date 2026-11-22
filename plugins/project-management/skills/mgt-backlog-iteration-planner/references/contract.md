# Contrato mgt-backlog-iteration-planner

- Gate de cierre: G2 (gate de entrada: G1)
- Inputs: `PCH` y `RMP` con gate G1 aprobado; User Stories y `DSP` aprobado de `requirements-engineering`; capacidad y compromisos entregados por una persona.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: SSP. `management/sprints/SSP-NNN-<slug>.md`, un archivo por Sprint, con `dsp_id`.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, decisión humana pendiente (compromiso, cambio, cierre) o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
