# ValidaciÃ³n â€” ssp-closure

## Comandos

Desde la raÃ­z del plugin:

```powershell
python scripts/check_closure.py status-report <STR.md>
python scripts/check_closure.py closure-report <CLS.md>
python scripts/validate_pathmap.py
python scripts/workflow.py init <run-id> --root <workspace> --project-id <id> --ssp-id <ssp> --period <periodo>
python scripts/workflow.py status <run-id> --root <workspace>
python scripts/workflow.py propose-gate <run-id> --gate <GATE> --result READY --check <check> --evidence <ref> --root <workspace>
python scripts/workflow.py approve-gate <run-id> --gate <GATE> --actor human:<nombre> --evidence <ref> --root <workspace>
```

## Cobertura declarada

- `check_closure.py`: validaciones estructurales de metadatos OKF para `STR` y `CLS`, prevenciÃ³n de horas/estimados en informe, referencias a issues y reglas identificables de agenda/cierre/experimentos.
- `workflow.py`: forma segura de run-id, inicializaciÃ³n sin sobrescritura, creación de estructura operativa, gates conocidos, dependencias, propuesta READY con evidencia y registro declarativo de actor/evidencia.
- `check_document_path`: verifies the canonical type directory and ID as filename prefix.
- `validate_pathmap.py`: checks routing map consistency and approved type catalog.

## LÃ­mites

Los scripts no validan el significado real de la evidencia, identidad/autenticaciÃ³n del actor, permiso de GitLab, decisiÃ³n del Product Owner, calidad semÃ¡ntica ni autorizaciÃ³n de despliegue. El plugin no consulta GitLab de forma automÃ¡tica. Una propuesta tÃ©cnica o un estado `APPROVED` local no reemplaza una decisiÃ³n humana autenticada.
