# {{dsp_id}} — {{project_name}}

## Objetivo
{{objective}}

## Alcance
{{scope}}

## Exclusiones
{{exclusions}}

## Riesgos
{{risks_intro}}

| ID | Riesgo | Clasificación | Impacto (1-5) | Probabilidad (1-5) | Incidencia (I×P) | Afecta a | Respuesta | Responsable |
|---|---|---|---|---|---|---|---|---|
{{risk_rows}}

## Milestones
{{milestones_intro}}

| N.º | SSP | Milestone |
|---|---|---|
{{milestone_rows}}

## Estimación y Costeo
{{estimation_table}}

{{sprint_costing}}

## Trazabilidad
- DSP: {{dsp_ref}}
- Project ID: `{{project_id}}`
- Issue ID: `{{issue_id}}`
- Issue IID: `{{issue_iid}}`

<!--
Plantilla del issue de tipo «Proyecto» (un Project Issue por DSP). La renderiza `scripts/gitlab_issues.py`; los comentarios HTML no se publican.
- Labels: `Proyecto` (más los de `--label`, por ejemplo `Proyecto :: Ejecución`). Sin Milestone: abarca varios Sprints.
- Objetivo y exclusiones salen de las secciones «Objetivo» y «Trabajo excluido» del DSP; el alcance lista las historias del Sprint con su issue.
- Riesgos: una fila por riesgo con ID estable R-nn, entregada en `--project-data` (clave `risks`). Sin dato, la tabla queda sin filas y no se inventan riesgos.
  Clasificación: Técnico, Negocio, Persona, Seguridad, Operación, Datos, Proveedor u Otro. Impacto y probabilidad: 1 a 5. Incidencia: impacto por probabilidad
  (1-5 baja, 6-12 media, 15-25 alta). Afecta a: Objetivo, Alcance, Cronograma o Costo. Respuesta: Evitar, Mitigar, Transferir o Aceptar, con la acción.
- Estimación y Costeo (va antes de Trazabilidad): una fila por User Story del alcance con código, título, talla, # CA y las horas de persona, de agente de IA y total de QA y Dev, más una fila de totales; debajo, los totales del Sprint (`/time`, `/cost`, `/time_agent`, `/cost_agent`). Salen de `estimate.py` (`--estimates`); sin dato, «Por definir». Una persona los confirma en el Sprint Planning.
- Milestones: una fila por cada Milestone generado para el DSP, en orden de creación, con numeral consecutivo sin saltos. Mientras no haya, la introducción dice «Aún no hay Milestones».
- Un Project Issue ya existente que se gobierna aparte no se modifica (`--project-issue-iid`).
-->
