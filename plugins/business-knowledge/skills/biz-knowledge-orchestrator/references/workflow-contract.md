# Contrato del orchestrator

G0: objetivo, producto, alcance, fuentes autorizadas y owner.
G1: `biz-context-objectives-analyst` -> BCP y BO.
G2: `biz-stakeholder-capability-mapper` -> STK y BCAP.
G3: `biz-glossary-curator` -> TRM e índice del glosario.
G4: `biz-rules-modeler` -> BR e índice de reglas.
G5: `biz-information-model-designer` -> IMD; `biz-scenario-modeler` -> BSN (T07, depende de G4 y no de T05).
G6: `biz-pack-validator-publisher` -> trazabilidad, `check_pack.py` y handoff.

Todo paso devuelve `inputs`, `outputs`, `readiness`, `gate`, `evidence`, `open_questions`, `owner` y `approved_by` (solo cuando exista aprobación externa).

## Contrato orchestrator -> skill

```json
{
  "run_id": "RUN-001",
  "workspace_root": ".",
  "skill": "biz-glossary-curator",
  "document_type": "TRM",
  "output_dir": "./business/terms/",
  "pathmap_version": "2.0.0",
  "override": null,
  "gate": "G3",
  "inputs": ["BCP-001", "BCAP-001"],
  "required_standard": "STD-OKF-001-v0.1.0-stable"
}
```

El skill devuelve un manifiesto con `document_type`, `actual_path`, `okf_validation`, `sources` y `gate_evidence`. El orchestrator lo valida y bloquea el gate si hay divergencias.
