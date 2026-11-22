# Sección: Resultado de publicación GitLab

Fragmento para incorporar en un `STR` o `CLS` OKF existente. El resultado de ejecución completo se devuelve estructurado al orchestrator. No incluir el PAT ni cabeceras.


## Milestone del Sprint
| Alcance | Acción | Id / iid | URL | Autorizado por | Resultado |
|---|---|---|---|---|---|
| proyecto <id> / grupo <id> | dry-run / create / update / sync (`gitlab_milestone.py`) | <id> / <iid> | <url> | <human:nombre — fecha> | creado / actualizado / sin cambios / ya existía / error |

## Issues del alcance (`gitlab_issues.py`)
Un issue por User Story del Sprint con el label `User Story` y un issue del DSP con el label `Proyecto`.

| Concepto OKF | Issue (iid) | URL | Resultado | Labels |
|---|---|---|---|---|
| <US-ID> | <iid> | <url> | creado / actualizado / sin cambios / ya existía / error | User Story |
| <DSP-ID> | <iid> | <url> | creado / actualizado / sin cambios / ya existía / error | Proyecto |

## Deriva detectada
| Tipo | Elemento | Acción propuesta |
|---|---|---|
| issue sin plan / plan sin issue | <ref> | <acción> |

## Verificación
<Resultado de `report-userstory-testcase`: historias y casos coherentes con el plan.>

## Preparación
- **Estado:** READY / CONDITIONAL / NOT_READY
