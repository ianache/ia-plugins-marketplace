# Reglas locales

- Ejecutar solo con una autorización verificada por el runtime (`qa_orchestrator.py verify-authorization`).
- Producir artefactos y evidencias propuestas. **No** editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills
  y no emitir `decision`/`PASS`: entregar `gate_proposal` con checks `{id, result, evidence_ref}`.
- Los checks `script` salen de scripts deterministas que el orquestador ejecuta en `gate` (sin verificador: `attested_by: human:<id>`); los `independent-review` los aporta un revisor (`reviewer`) distinto del autor.
- Si falta evidencia, marcar `UNCERTAIN` o `FAIL`. Nunca inferir `PASS`.
- Cambios de versión de entradas invalidan la autorización: detenerse y avisar al orquestador.
