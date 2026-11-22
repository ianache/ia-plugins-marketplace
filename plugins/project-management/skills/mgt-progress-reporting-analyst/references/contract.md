# Contrato mgt-progress-reporting-analyst

- Gate de cierre: G5 (gate de entrada: G4)
- Inputs: Plan e iteraciones (`SSP`), riesgos y cambios (`RSK`, `CHG`) con G4 aprobado, y datos reales de GitLab (issues, milestones, timelogs) del periodo.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: STR. `management/status-reports/STR-NNN-<periodo>.md`, uno por periodo.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, decisión humana pendiente (compromiso, cambio, cierre) o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
