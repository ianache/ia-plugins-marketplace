# ssp-closure — Plugin de cierre de Sprint

**Versión:** 1.0.0
**Estándar:** STD-OKF-001 v0.1.0-stable

Prepara Sprint Review, Sprint Retrospective y resumen de readiness para un SSP existente. El pack contiene **un orchestrator y cinco skills especializados**, dentro del máximo recomendado de seis: cada especialista tiene una función separada y sus contratos se documentan en su `SKILL.md`.

## Skills y flujo

| Tarea | Skill | Resultado | Gate |
|---|---|---|---|
| T1 | `review-agenda` | Payload de agenda/acta para alimentar el cierre | `REVIEW_AGENDA_GATE` |
| T2 | `review-status-report` | Payload factual de estado de historias/TC | `REVIEW_REPORT_GATE` |
| T3 | `retro-agenda` | Documento `CLS` de cierre de Sprint, incorporando resultados Review y Retro | `RETRO_AGENDA_GATE` |
| T4 | `retro-experiment-tracker` | Payload de seguimiento y referencias a issues de experimento; no crea un documento OKF independiente | `RETRO_TRACKER_GATE` |
| T5 | `release-readiness` | Datos de readiness para consolidar en el `STR` del periodo | `RELEASE_READINESS_GATE` |

El orchestrator coordina las cinco tareas, conserva su estado y referencias, consolida las salidas factuales en el `STR` de periodo y controla los gates. No toma decisiones de aceptación, calidad ni despliegue. El Product Owner registra la aceptación de historias; una persona autorizada decide los gates.

## Modos y alcance

El plugin soporta los **ámbitos de ceremonia** Review, Retrospective y Release Readiness, definidos como flujo estándar del plugin. Greenfield/Brownfield/Evolution no son modos de este plugin: trabaja sobre un SSP, milestone, issues y evidencia de producto ya existentes. Si el producto se encuentra en uno de esos escenarios, se conserva como contexto del SSP, pero no cambia las tareas del plugin. No se infiere un escenario de producto ni se reconstruye su baseline aquí.

## Rutas y tipos documentales

- Estado y archivos de gestión del orchestrator: `.comsatel/ssp-closure/runs/<run-id>/`.
- Documento de estado del periodo: `STR`, en `management/status-reports/`.
- Documento de cierre del Sprint (resultado, desviaciones y lecciones): `CLS`, en `management/closure/`.
- Agendas, propuestas de gate, resultados de tarea y payloads de integración se guardan como información operativa del run; no se etiquetan con tipos OKF inventados.
- Los tipos provienen del catálogo aprobado de STD-OKF-001 v0.1.0-stable. El plugin no crea alias para reuniones, experimentos o readiness.

Consultar `assets/pathmap.json` y `assets/pathmap.md` para rutas. Las plantillas `skills/ssp-closure-orchestrator/templates/status-report.md` (STR) y `skills/retro-agenda/templates/closure-report.md` (CLS) contienen los metadatos OKF requeridos.

## Uso

Desde la raíz del plugin:

```powershell
python scripts/workflow.py init SSP-2026-04 --root <workspace> --project-id <gitlab-project-id> --ssp-id SSP-2026-04 --period 2026-W46
python scripts/workflow.py status SSP-2026-04 --root <workspace>
python scripts/workflow.py propose-gate SSP-2026-04 --gate REVIEW_AGENDA_GATE --result READY --check "agenda completa" --evidence task-results/T1/review-agenda.md --root <workspace>
python scripts/workflow.py approve-gate SSP-2026-04 --gate REVIEW_AGENDA_GATE --actor human:<nombre> --evidence <ruta-o-referencia> --root <workspace>
python scripts/check_closure.py status-report management/status-reports/<STR-ID>.md
python scripts/check_closure.py closure-report management/closure/<CLS-ID>.md
python scripts/validate_pathmap.py
```

`workflow.py` guarda manifiesto, plan, registro de gates, evidencia y resultados operativos en `.comsatel/ssp-closure/runs/<run-id>/`. El actor local es una declaración y no se autentica con el script. La integración GitLab requiere acceso externo y no está implementada por este plugin.

## Gobierno

- Los especialistas no aprueban gates ni deciden aceptar historias o desplegar.
- El informe de estado no incluye horas, estimados ni gasto mientras las fuentes de tiempo no sean completas; toda cifra refiere su issue de origen.
- Un experimento solo se registra si tiene persona dueña, métrica y fecha de cierre. Crear issues en GitLab requiere autorización explícita y acceso; sin ello se devuelve el payload sin publicar.
- Evidencia ausente implica bloqueo o `UNCERTAIN`, nunca PASS inferido.
