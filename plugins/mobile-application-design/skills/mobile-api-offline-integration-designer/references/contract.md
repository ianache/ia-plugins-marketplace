# Contrato de ejecución — mobile-api-offline-integration-designer

- **Versión:** 1.0.0
- **Productor:** `mobile-api-offline-integration-designer`
- **Gate:** `G4`
- **Inputs:** OpenAPI/AsyncAPI, FDT, ADR, políticas de seguridad, modelo de datos y tenancy.
- **Outputs:** integration/mobile-api-contracts.md; integration/offline-sync-design.md; integration/local-storage-design.md; integration/security-and-observability.md.
- **Precondición:** G0 aprobado; para tareas dependientes, gate anterior aprobado según `execution-plan.json`.
- **Postcondición:** archivos existentes, evidencia y traceability, sin suponer aprobación.
- **Error:** registrar `blocked`, causa, evidencia faltante y siguiente responsable en `comsatel/`.
- **Criterio:** políticas de cache/TTL, conflicto y reintentos; secretos no embebidos; PKCE y tokens; telemetría sin PII.
