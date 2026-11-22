# Contrato local de qa-sdlc-orchestrator

**Rol:** orchestrator

**Entradas:** objective, DSP id/versión/ruta, gitlab_id, available_artifacts, decisiones upstream; para publicar: GITLAB_PAT en runtime, kb_local_path y kb_gitlab_url por TC.

**Salidas:** plan.yaml, plan-status.yaml, tasks/<id>/task-status.yaml, events.jsonl, evidence/ y QDC (decisión de calidad humana registrada).

**Gates:** TESTCASE_PUBLICATION_GATE, HUMAN_GATE. Evaluados por el orquestador.

Vocabulario y reglas comunes: `resources/contracts/common-contract.yaml`.
