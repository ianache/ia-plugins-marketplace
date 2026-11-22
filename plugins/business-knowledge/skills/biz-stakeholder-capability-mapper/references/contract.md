# Contrato biz-stakeholder-capability-mapper

- Gate de cierre: G2 (gate de entrada: G1)
- Inputs: BCP y BO con gate G1 aprobado, más fuentes de organización, procesos, políticas y roles.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: STK; BCAP; mapa de capacidades y procesos como secciones de los BCAP. `business/stakeholders/` y `business/capabilities/`.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
