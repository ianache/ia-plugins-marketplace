# Contrato af-acceptance-quality-reviewer

- Gate: G4
- Inputs: HU (G3) y reglas BR de la línea base de negocio (G2, `business-knowledge`)
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado si existe dependencia.
- Outputs: acceptance-review; coverage; DoR
- Postcondición: hallazgos de criterios y readiness por HU.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha/versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado de gate.

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
