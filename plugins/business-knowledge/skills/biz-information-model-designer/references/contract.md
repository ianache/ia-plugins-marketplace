# Contrato biz-information-model-designer

- Gate de cierre: G5 (gate de entrada: G4)
- Inputs: Glosario TRM (G3) y reglas BR (G4) aprobados, BCAP y fuentes funcionales autorizadas; el modelo existente del dominio, si lo hay (se actualiza, no se reemplaza).
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: IMD; `business/information-model/IMD-NNN-<slug>.md`, un archivo por modelo.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
