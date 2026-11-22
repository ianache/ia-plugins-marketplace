# Contrato de ejecución — mobile-design-orchestrator

- **Versión:** 1.0.0
- **Productor:** `mobile-design-orchestrator`
- **Gate:** `G0-G6`
- **Inputs:** solicitud, escenario, alcance, fuentes y actores de aprobación.
- **Outputs:** .comsatel/mobile-application-design/runs/<run-id>/state.json; .comsatel/mobile-application-design/runs/<run-id>/execution-plan.json; .comsatel/mobile-application-design/runs/<run-id>/gate-register.json.
- **Precondición:** G0 aprobado; para tareas dependientes, gate anterior aprobado según `execution-plan.json`.
- **Postcondición:** archivos existentes, evidencia y traceability, sin suponer aprobación.
- **Error:** registrar `blocked`, causa, evidencia faltante y siguiente responsable en `comsatel/`.
- **Criterio:** secuenciación condicionada, evidencia de outputs, gates humanos, bloqueo por dependencias y reporte final.
