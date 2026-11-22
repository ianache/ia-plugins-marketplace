# Contrato biz-rules-modeler

- Gate de cierre: G4 (gate de entrada: G3)
- Inputs: Glosario TRM con gate G3 aprobado, BCP/BO/BCAP con sus gates aprobados y fuentes funcionales autorizadas (visión, procesos, políticas, User Stories, decisiones registradas).
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: BR; `business/rules/BR-NNN.md` (uno por regla, generado por `scripts/rules.py from-json`) más `business/rules/CTLG-BR.md` (CTLG, generado por `scripts/rules.py build`); matriz de trazabilidad de reglas como sección de cada BR.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Reutilización: antes de crear una `BR`, buscar en el workspace una regla con el mismo enunciado; si existe, se reutiliza su ID.
- Catálogo narrativo: `type: CTLG`, `indexes: BR`, filas enlazadas a los `BR-NNN.md`; sin tipos no registrados.
- Fuentes: cada fuente declara `id` y `resource`; una fuente eliminada se cita como referencia de git (`git:<commit>^:<ruta>`).
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
