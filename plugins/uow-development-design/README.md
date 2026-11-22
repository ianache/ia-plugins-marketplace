# UOW Development Design

Plugin de Claude Code que convierte una **User Story**, el **diseño de API** y el **diseño de BD** en **Unidades de Trabajo (UOW)**: paquetes asignables a un developer que desarrolla asistido por un agente IA (Claude Code, con perfil para Superpowers).

- **Versión:** 1.0.0 · **Autor:** COMSATEL
- **Skills:** 1 orquestador y 6 especialistas.
- **Modalidades:** `GREENFIELD`, `BROWNFIELD`, `EVOLUTION`.
- **Salida:** `./management/uows/` (documentos OKF) y `.comsatel/uow-development-design/runs/` (estado operativo).

## Qué es una UOW
Un slice vertical de una US (API, datos y lógica de un comportamiento completo) que un solo developer con su agente puede completar. Una US puede dar una o varias UOW. La UOW **referencia** por ID y versión lo que producen los demás plugins (`US`, `DSP`, `SSP`, `FDT`, `API`, `LDM`, `PDM`, `DBM`, `HOF`, `WEB`, `MOB`, `HCB`, `ADR`); no lo copia ni lo redefine.

## Skills

| Skill | Tarea | Produce |
| :--- | :-: | :--- |
| `uow-orchestrator` | G0, `expand`, T07 | estado operativo, `uow-package.yaml` |
| `uow-context-assembler` | T01 | `UCX` — insumos versionados; hechos, inferencias, supuestos, desconocidos |
| `uow-slice-designer` | T02 | `UOW` — alcance, límites, dependencias, criterios cubiertos |
| `uow-contract-binder` | T03 | `UCB` — operaciones API y objetos de datos exactos, coherencia API↔BD |
| `uow-codebase-mapper` | T04 | `UCM` — repositorio, rama y commit base, rutas permitidas y prohibidas |
| `uow-agent-execution-planner` | T05 | `UAP` — pasos con prueba primero, verificación, parada, desviaciones |
| `uow-readiness-reviewer` | T06 | `UWR` — revisión independiente |

## Flujo
`G0 → T01 contexto → T02 slice → expand → { T03 contratos ‖ T04 código } → T05 plan del agente → T06 revisión → T07 aprobación humana`

`UOW_READY_GATE` exige aprobación humana ligada al digest exacto del paquete. Hasta entonces la UOW no se asigna a nadie; la asignación es de Gestión.

## Uso
```
python skills/uow-orchestrator/scripts/uow_orchestrator.py init --plan-id P1 --us-id US-001 --us-version 1.0.0 --us-path <ruta> --objective "..." --mode GREENFIELD
python skills/uow-orchestrator/scripts/uow_orchestrator.py g0
python skills/uow-orchestrator/scripts/uow_orchestrator.py authorize --task T01   # y start, complete, gate
python skills/uow-orchestrator/scripts/uow_orchestrator.py expand --uows UOW-001,UOW-002 --depends UOW-002=UOW-001
python skills/uow-orchestrator/scripts/uow_package.py build --root ./management/uows --uow UOW-001
```
### Línea base verificable

`init --mode BROWNFIELD|EVOLUTION` exige `--baseline-ref` y `--baseline-commit`. Con `--baseline-repo <ruta-repo-git>` G0 además comprueba con `git cat-file -e <commit>^{commit}` que el commit existe (check `baseline-commit-exists`); sin `--baseline-repo` solo se verifica que estén declarados.

### Aprobación humana y reevaluación de `UOW_READY_GATE`

- `gate --pack <raíz de management/uows>` ejecuta `check_uow_package.py` por su cuenta y su resultado manda sobre el JSON de checks; sin `--pack`, los checks `script` exigen `attested_by: human:<id>` y los `independent-review` un `reviewer` distinto del autor.
- `--human-approval` (en `authorize` y `gate`), `--checks`, `--waiver` y `--scope-json` reciben la **ruta de un archivo JSON**, no el JSON en línea. La aprobación lleva `{"approved": true, "actor": "human:<id>", "evidence_ref": "<MR/ticket>", "artifact_revision": "<digest>"}`; el `artifact_revision` es el digest que el gate calculó para las salidas de la tarea (queda en `evidence/UOW_READY_GATE/<tarea>-attempt<N>.yaml` tras la primera evaluación).
- La primera evaluación de `UOW_READY_GATE` sin aprobación válida deja la tarea en `BLOCKED` y abre una intervención humana (`human_intervention`). Para reevaluar: (1) `human --id <HI-id> --decision REVALIDATE --evidence <ref>` registrado por una persona; (2) `gate --task <T07-…> --checks <checks.json> --human-approval <aprobacion.json>`. Una decisión humana no equivale a PASS: el gate se vuelve a evaluar.

Los checks deterministas de cada gate: `python skills/<skill>/scripts/check_uow_package.py --root <dir> --profile <context|slice|binding|codebase|agent-plan|readiness|ready> [--uow UOW-001]`.

Más detalle en [DOCUMENTACION.md](DOCUMENTACION.md). Estándar: `standards/STD-OKF-001-v1.11.0-stable.md` (los tipos `UOW`, `UCX`, `UCB`, `UCM`, `UAP` y `UWR` están aprobados en v1.11.0-stable).
