# Contrato de ejecución — mobile-evolution-release-planner

- **Versión:** 1.0.0
- **Productor:** `mobile-evolution-release-planner`
- **Gate:** `G5`
- **Inputs:** As-Is, arquitectura To-Be, contratos, matriz de dispositivos y restricciones de stores.
- **Outputs:** evolution/change-impact-analysis.md; evolution/mobile-migration-plan.md; evolution/release-rollout-rollback.md; evolution/mobile-test-strategy.md.
- **Precondición:** G0 aprobado; para tareas dependientes, gate anterior aprobado según `execution-plan.json`.
- **Postcondición:** archivos existentes, evidencia y traceability, sin suponer aprobación.
- **Error:** registrar `blocked`, causa, evidencia faltante y siguiente responsable en `comsatel/`.
- **Criterio:** migración incremental, versionado API/app, feature flags, observabilidad, pruebas y plan de reversión realista.
