# Contrato biz-glossary-curator

- Gate de cierre: G3 (gate de entrada: G2)
- Inputs: BCP, STK y BCAP con sus gates aprobados; fuentes autorizadas del producto o dominio; glosario existente (se actualiza, no se reemplaza); acceso web solo para fuentes externas N1.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: TRM; `business/terms/TRM-NNN-<slug>.md` por término y `business/terms/CTLG-TRM.md` (CTLG, índice alfabético sin definiciones).
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
- Prohibido: documentos de glosario con otro `type` (p. ej. `Business Glossary`). Un glosario en `business/terms/` es solo `TRM-*.md` y `CTLG-TRM.md`.
