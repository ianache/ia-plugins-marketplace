# Contrato local de uow-orchestrator

Inputs: US (id, versión, ruta con digest), modo, línea base si aplica y decisiones humanas. Outputs: `plan.yaml`, `plan-status.yaml`, `events.jsonl`, evidencia de gates y `uow-package.yaml` por UOW. Decide gates con `gate_governance.decide()`. Los gates los decide exclusivamente el orquestador.
