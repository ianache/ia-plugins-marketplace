# Contrato biz-context-objectives-analyst

- Gate de cierre: G1 (gate de entrada: G0)
- Inputs: Fuentes gobernadas de negocio (estrategia, planes, PRD, visión, actas, procesos, políticas, contratos) y alcance del run (G0 aprobado). No requiere salidas previas de este pack.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: BCP; BO. `business/context-packs/BCP-NNN-<slug>.md` y `business/objectives/BO-NNN-<slug>.md`.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
