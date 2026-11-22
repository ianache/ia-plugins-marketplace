# Gate Governance v1.0 — COMSATEL

Separar **evaluación del gate**, **política de decisión** y **transición del workflow**.

- `AUTO`: criterios determinísticos PASS -> AUTO_ADVANCE; falla -> reintento limitado o HIL.
- `CONDITIONAL_HIL`: PASS verificable -> AUTO_ADVANCE; incertidumbre, cambio riesgoso o agotamiento -> REQUEST_HIL.
- `MANDATORY_HIL`: todos los checks PASS y aprobación humana explícita ligada a la revisión exacta del artefacto.
- Los resultados de agentes no constituyen por sí solos evidencia suficiente para autorizar automáticamente cambios críticos.
- Nunca convertir FAIL en PASS por simple aprobación verbal. Las excepciones requieren registro independiente y autorización conforme a política.
- `AUTO_ADVANCE` significa **elegible para despacho**, no ejecución del agente: el orquestador debe verificar todas las dependencias y registrar autorización.
- `AUTO_RETRY` requiere presupuesto de intentos; `REQUEST_HIL` suspende tareas dependientes.
- `PASS`, `FAIL`, `BLOCKED` describen gates; `PENDING`, `IN_PROGRESS`, `COMPLETED` describen tareas; `draft`, `stable`, `deprecated` describen documentos.
- El orquestador es el único escritor autorizado de estados operativos. Las revisiones posteriores invalidan aprobaciones obsoletas.
