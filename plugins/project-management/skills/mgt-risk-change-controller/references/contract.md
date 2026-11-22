# Contrato mgt-risk-change-controller

- Gate de cierre: G4 (gate de entrada: G3)
- Inputs: Plan e iteraciones aprobados (G1 a G3), riesgos de negocio (`BRISK` en el `BCP`), ASR/ADR de arquitectura, análisis de impacto (`IMP`), decisión de calidad (`QDC`) cuando exista, y el estado real del trabajo.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: RSK; CHG. `management/risks/RSK-NNN-<slug>.md` (un registro por iniciativa) y `management/changes/CHG-NNN-<slug>.md` (uno por solicitud).
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, decisión humana pendiente (compromiso, cambio, cierre) o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
