# Contrato mgt-work-publisher-synchronizer

- Gate de cierre: G3 (gate de entrada: G2)
- Inputs: `SSP` con gate G2 aprobado, User Stories OKF aprobadas, configuración de producto-proyecto de GitLab y `GITLAB_PAT` en el entorno (solo se verifica que exista; nunca se imprime ni se guarda).
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: resultado estructurado de publicación devuelto al orchestrator en `.comsatel/project-management/runs/<run-id>/`.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, decisión humana pendiente (compromiso, cambio, cierre) o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
