# {{hu_id}} — {{title}}

Fuente única de la historia:
- Repositorio: {{hu_repo}}
- Local: `{{hu_local}}`

Este Issue es una proyección operativa para el Board «Sprint Backlog»: sirve para ver y mover el estado. La historia, sus criterios de aceptación y la Definition of Done se leen y se cambian solo en el archivo de la historia indicado. No copiar ese contenido aquí. La estimación de esfuerzo es de gestión: se calcula con el estimador del skill userstory-traceability y vive solo en este Issue.

## Estimación de esfuerzo (referencia)

- **Estimación de esfuerzo:** {{effort_estimate}}
- **Base de la estimación:** {{effort_basis}}

## Costeo

{{costing_table}}

## Tareas

{{tasks_table}}

## Trazabilidad
- DSP: `{{dsp_id}}` ({{dsp_ref}})
{{ssp_line}}
- US: `{{hu_local}}`
- Project ID: `{{project_id}}`
- Issue ID: `{{issue_id}}`
- Issue IID: `{{issue_iid}}`
- Project Issue: {{project_issue}}
- Milestone: {{milestone_title}}

<!--
Plantilla del issue de tipo «User Story». La renderiza `scripts/gitlab_issues.py`; los comentarios HTML no se publican.
- Título del issue: `US<iid>: <título>`. El iid lo asigna GitLab al crear: se crea el issue y luego se completa título y trazabilidad.
- Labels: `User Story` (más los de `--label`, por ejemplo `AI Cowork` o `Status :: PENDING`). Milestone: el del SSP.
- hu_repo: enlace al archivo de la historia en el repositorio, o la ruta en código si no hay URL base.
- effort_estimate y effort_basis: los entrega una persona o el estimador (`--estimates`); sin dato, «Por definir». El total es horas de persona más horas del agente de IA y se fija también en el estimate nativo de GitLab.
- costing_table: tabla Desarrollo / QA / Total con horas de persona, horas del agente de IA, total de horas y costo de la persona (horas por la tarifa del estimador). El costo del agente se calcula por Sprint (`/cost_agent` del Milestone), no por historia. Sin dato, «Por definir».
- tasks_table: los dos issues `Task` de la historia (Dev y QA) con su enlace y su estimate; además quedan enlazados a la historia en GitLab (`relates_to`) y con su mismo Milestone.
- ssp_line: la línea «- SSP: ...» solo existe si se indica `--ssp`. project_issue: «#<iid>» del Project Issue.
- No copiar aquí la historia, sus criterios ni la Definition of Done.
-->
