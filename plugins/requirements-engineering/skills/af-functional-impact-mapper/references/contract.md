# Contrato af-functional-impact-mapper

- Gate: G5
- Inputs: RCP, HU, reglas, capacidades
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado si existe dependencia.
- Outputs: impact-analysis; impact-surface-map
- Postcondición: impactos confirmados/inferidos/hipotéticos.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha/versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado de gate.

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
