# Contrato mgt-release-closure-auditor

- Gate de cierre: G6 (gate de entrada: G5)
- Inputs: Todos los entregables de G1 a G5, la decisión de calidad (`QDC`) del pack de QA cuando exista, y el estado real de issues, cambios y riesgos.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: CLS. `management/closure/CLS-NNN-<slug>.md`.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, decisión humana pendiente (compromiso, cambio, cierre) o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
