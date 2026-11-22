/project {{project}}
/subproject {{subproject}}
/cost {{cost}}
/time {{time}}
/client {{client}}
/group {{group}}
/cost_agent {{cost_agent}}
/time_agent {{time_agent}}
{{project_end_line}}

<!--
Plantilla de la descripción del Milestone de un Sprint. La renderiza `scripts/gitlab_milestone.py`; los comentarios HTML no se publican.
La descripción contiene solo estos comandos, uno por línea y en este orden; no lleva Sprint Goal, historias ni enlaces (eso vive en el SSP). Los valores salen del bloque de la sección «Descripción del Milestone» del SSP.
- /project: nombre del proyecto. /subproject: título del Milestone (no puede estar pendiente).
- /cost y /time: los informa una persona (costo y horas del equipo). /cost_agent y /time_agent: costo y horas del agente de IA.
- /client y /group: por defecto COMSATEL y Proyectos.
- /project_end: opcional, AAAA-MM-DD; la línea solo existe si hay valor.
- Un valor que nadie informó se escribe PENDIENTE y se reporta; nunca se inventa.
Los comandos son texto: GitLab no los ejecuta; otra plataforma los lee para extraer métricas.
Ejemplo vigente: Milestone «Sprint 1 - Catálogo de Skills (business y management)» de kb-demo (iid 2).
-->
