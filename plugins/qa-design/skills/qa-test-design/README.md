# qa-test-design

Rol: **specialist** del pack `qa-sdlc-pack` v1.3.0.

**Entradas:** QFA aprobado (gate FEATURE_ANALYSIS_GATE en PASS verificado por el orquestador) y referencia al DSP.

**Salidas:** QTD (índice del pack), QTS (estrategia), QTP (plan y priorización), TSN-*, TC-*, coverage-matrix.yaml, requirements-test-traceability.yaml y gate-report-T02.yaml (en `.comsatel/qa-design/runs/<run-id>/evidence/TEST_DESIGN_GATE/`) como gate_proposal.

Autónomo: todo recurso necesario está en esta carpeta. Ver `SKILL.md` y `resources/contract.md`.
