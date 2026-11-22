# qa-sdlc-orchestrator

Rol: **orchestrator** del pack `qa-sdlc-pack` v1.3.0.

**Entradas:** objective, DSP id/versión/ruta, gitlab_id, available_artifacts, decisiones upstream; para publicar: GITLAB_PAT en runtime, kb_local_path y kb_gitlab_url por TC.

**Salidas:** plan.yaml, plan-status.yaml, tasks/<id>/task-status.yaml, events.jsonl, evidence/ y QDC (decisión de calidad humana registrada).

Autónomo: todo recurso necesario está en esta carpeta. Ver `SKILL.md` y `resources/contract.md`.
