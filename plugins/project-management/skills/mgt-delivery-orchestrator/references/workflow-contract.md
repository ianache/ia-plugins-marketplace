# Contrato del orchestrator

G0: iniciativa, producto, alcance, periodo, fuentes autorizadas y owner.
G1: `mgt-charter-roadmap-planner` -> PCH y RMP.
G2: `mgt-backlog-iteration-planner` -> SSP.
G3: `mgt-work-publisher-synchronizer` -> manifiesto de publicación GitLab (evidencia operativa).
G4: `mgt-risk-change-controller` -> RSK y CHG.
G5: `mgt-progress-reporting-analyst` -> STR.
G6: `mgt-release-closure-auditor` -> CLS y `check_management.py`.

Todo paso devuelve `inputs`, `outputs`, `readiness`, `gate`, `evidence`, `open_questions`, `owner` y `approved_by` (solo cuando exista aprobación externa).

## Contrato orchestrator -> skill

```json
{
  "run_id": "RUN-001",
  "workspace_root": ".",
  "skill": "mgt-risk-change-controller",
  "document_type": "RSK",
  "output_dir": "./management/risks/",
  "pathmap_version": "1.0.0",
  "override": null,
  "gate": "G4",
  "inputs": ["PCH-001", "SSP-001"],
  "required_standard": "STD-OKF-001-v1.9.0-stable"
}
```
