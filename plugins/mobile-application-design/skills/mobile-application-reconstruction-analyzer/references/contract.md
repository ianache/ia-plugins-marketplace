# Contrato de ejecución — mobile-application-reconstruction-analyzer

- **Versión:** 1.0.0
- **Productor:** `mobile-application-reconstruction-analyzer`
- **Gate:** `G1`
- **Inputs:** repositorio Flutter, versiones/commit, ADR, APIs y documentación vigente.
- **Outputs:** as-is/mobile-as-is-assessment.md; as-is/mobile-dependency-inventory.md; as-is/mobile-risk-register.md.
- **Precondición:** G0 aprobado; para tareas dependientes, gate anterior aprobado según `execution-plan.json`.
- **Postcondición:** archivos existentes, evidencia y traceability, sin suponer aprobación.
- **Error:** registrar `blocked`, causa, evidencia faltante y siguiente responsable en `comsatel/`.
- **Criterio:** inventario con evidencia por ruta, versión y confianza; riesgos sin inferir código inexistente.
