# Contrato local de qa-test-design

**Rol:** specialist

**Entradas:** QFA aprobado (gate FEATURE_ANALYSIS_GATE en PASS verificado por el orquestador) y referencia al DSP.

**Salidas:** QTD (índice del pack), QTS (estrategia), QTP (plan y priorización), TSN-*, TC-*, coverage-matrix.yaml, requirements-test-traceability.yaml y gate-report-T02.yaml (en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_DESIGN_GATE/`) como gate_proposal.

**Gates:** TEST_DESIGN_GATE. El especialista entrega `gate_proposal`; solo el orquestador decide.

Vocabulario y reglas comunes: `resources/contracts/common-contract.yaml`.
