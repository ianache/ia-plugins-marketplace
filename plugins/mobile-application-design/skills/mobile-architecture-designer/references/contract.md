# Contrato de ejecución — mobile-architecture-designer

- **Versión:** 1.0.0
- **Productor:** `mobile-architecture-designer`
- **Gate:** `G2`
- **Inputs:** DDD BC/CTX, ASR, ADR, handoff UX/UI, contratos API/BFF, As-Is si aplica.
- **Outputs:** architecture/mobile-architecture.md; architecture/feature-module-boundaries.md; architecture/platform-capabilities.md; architecture/mobile-adr-register.md.
- **Precondición:** G0 aprobado; para tareas dependientes, gate anterior aprobado según `execution-plan.json`.
- **Postcondición:** archivos existentes, evidencia y traceability, sin suponer aprobación.
- **Error:** registrar `blocked`, causa, evidencia faltante y siguiente responsable en `comsatel/`.
- **Criterio:** decidir modular monolith vs módulos/packages; separar domain/data/presentation; no imponer 1:1 con API/BC/MicroUI.
