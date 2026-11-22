# Contrato local de qa-feature-analyzer

**Rol:** specialist

**Entradas:** DSP validado (id, versión, estado, ruta) y User Stories en scope; evidencia upstream condicional (arquitectura, API, seguridad, UX, defectos).

**Salidas:** QFA: QA Feature Analysis Pack con RISK-*, ambigüedades, surfaces, readiness por criterio y checks de gate_proposal.

**Gates:** FEATURE_ANALYSIS_GATE. El especialista entrega `gate_proposal`; solo el orquestador decide.

Vocabulario y reglas comunes: `resources/contracts/common-contract.yaml`.
