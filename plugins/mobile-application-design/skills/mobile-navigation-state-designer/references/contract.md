# Contrato de ejecución — mobile-navigation-state-designer

- **Versión:** 1.0.0
- **Productor:** `mobile-navigation-state-designer`
- **Gate:** `G3`
- **Inputs:** UXR/FLW/SCR/CMP/TKN aprobados, arquitectura mobile, políticas de sesión.
- **Outputs:** composition/navigation-routing-spec.md; composition/state-management-spec.md; composition/ui-technical-mapping.md; composition/accessibility-implementation.md.
- **Precondición:** G0 aprobado; para tareas dependientes, gate anterior aprobado según `execution-plan.json`.
- **Postcondición:** archivos existentes, evidencia y traceability, sin suponer aprobación.
- **Error:** registrar `blocked`, causa, evidencia faltante y siguiente responsable en `comsatel/`.
- **Criterio:** rutas profundas, auth guards, lifecycle, loading/error/empty/offline states, ownership de estado y testing.
