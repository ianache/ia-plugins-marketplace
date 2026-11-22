# Validación de ux-design

## Comandos

Desde la raíz del plugin:

```powershell
python scripts/workflow.py init <run-id> --root <workspace> --initiative <id> --mode greenfield --scenario A
python scripts/workflow.py status <run-id> --root <workspace>
python scripts/workflow.py propose-gate <run-id> --gate G0 --result READY --check <check> --evidence <ref> --root <workspace>
python scripts/workflow.py approve-gate <run-id> --gate G0 --actor human:<id> --evidence <ref> --root <workspace>
python scripts/validate_pathmap.py
python skills/ux-ui-orchestrator/scripts/audit_ux.py <knowledge-base> --json
python skills/ux-development-handoff/validators/cli.py preflight --profile production --kb <knowledge-base> --initiative <id> --screens <SCR-id>
python skills/ux-development-handoff/validators/cli.py gate --profile production --kb <knowledge-base> --hof <HOF-id>
```

Para Brownfield/Evolution, `workflow.py init` exige `--baseline <referencia>`.

## Cobertura

- `workflow.py`: crea run sin sobrescritura, valida ID y modo, registra baseline/escenario, genera plan y gates; bloquea gates dependientes y requiere propuesta READY con evidencia antes de aprobación humana declarada.
- `audit_ux.py`: comprueba trazabilidad UXR/FLW/SCR/DTM, campos de SCR, enlaces relativos y vacíos detectables; no certifica accesibilidad semántica.
- `ux-development-handoff/validators`: lee OKF YAML, tipos permitidos, metadatos mínimos, lineage, readiness y gate técnico.
- `validate_pathmap.py`: compara tipos y rutas del plugin con la copia declarada del estándar.

## Límites

Los validadores no certifican que una persona esté autenticada, que una evidencia externa sea auténtica, que Stitch/Figma estén accesibles ni que WCAG se satisfaga sin inspección real. El resultado `READY` es técnico; una aprobación humana permanece independiente.
