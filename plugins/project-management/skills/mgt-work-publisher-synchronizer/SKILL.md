---
name: mgt-work-publisher-synchronizer
description: Publicar y sincronizar en GitLab el trabajo planificado (milestone, issues `User Story` y `Proyecto`, labels, tablero) y registrar el linaje plan-issue. Usar para publicación GitLab; sync; publication-manifest.
metadata:
  version: "0.1.0"
---

# Work Publisher & Synchronizer

## Activación
Usar cuando se requiera ejecutar publicación GitLab y devolver su resultado estructurado al orchestrator. Puede ejecutarse individualmente con sus precondiciones o por `mgt-delivery-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
`SSP` con gate G2 aprobado, User Stories OKF aprobadas, configuración de producto-proyecto de GitLab y `GITLAB_PAT` en el entorno (solo se verifica que exista; nunca se imprime ni se guarda). Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Verificar la configuración de producto-proyecto y que `GITLAB_PAT` exista, sin mostrar su valor.
2. **Milestone del Sprint** (primero, porque los issues se asignan a él; plantilla `templates/milestone-description.md`): `python scripts/gitlab_milestone.py <SSP.md> --project-id <id> --mode dry-run` (o `--group-id`). Lee los valores del bloque de la sección «Descripción del Milestone» del SSP y renderiza la plantilla: la descripción contiene solo `/project`, `/subproject`, `/cost`, `/time`, `/client`, `/group`, `/cost_agent` y `/time_agent` (y `/project_end` opcional), sin Sprint Goal, historias ni enlaces. El título es el valor de `/subproject`. Las fechas solo se envían con `--start-date` y `--due-date`. Presentar la vista previa a una persona y, con su autorización, repetir con `--mode create|update|sync --approved-by human:<nombre>`.
3. **Issues del alcance** (plantillas `templates/user-story-issue.md` para el label `User Story` y `templates/project-issue.md` para el label `Proyecto`; el script las rellena y no publica sus comentarios guía): `python scripts/gitlab_issues.py --project-id <id> --dsp <DSP.md> --story <US.md> [--story ...] --ssp <SSP.md> --milestone-title "<título del Milestone>" --kb-base-url <URL-base-de-archivos> --kb-root <raíz-local> [--estimates <estimaciones.json>] [--project-data <json>] [--project-issue-iid <N>] [--label <extra>] --mode dry-run`. Crea o actualiza **un issue por User Story del Sprint**: label `User Story`, Milestone del Sprint, título `US{iid}: <título>` y estimate nativo de GitLab en horas cuando hay estimación. La descripción lleva la fuente única de la historia (repositorio y ruta local), la estimación de esfuerzo de referencia, una tabla de costeo (Desarrollo, QA y Total: horas de persona, horas del agente de IA, total de horas y costo de la persona con la tarifa del estimador; el costo del agente se calcula por Sprint), la tabla de las dos tareas `Task` (Dev y QA) con su enlace y estimate, y la trazabilidad (DSP, SSP, US, Project ID, Issue ID e IID, Project Issue, Milestone); no copia la historia, sus criterios ni la Definition of Done. La estimación (`--estimates`) la entrega una persona o el estimador (`estimate.py`) y es horas de persona más horas del agente de IA, sin costo: el issue de la historia lleva el total (`human_h + agent_h`) en su estimate nativo y en la descripción, la tarea Dev `dev_human_h + dev_agent_h` y la tarea QA `qa.human_h + qa.agent_h` (solo en su estimate nativo; sin casos de prueba, la QA no se estima). Sin dato queda «Por definir» y no se fija nada. El **Project Issue** (label `Proyecto`) sigue `templates/project-issue.md` (Objetivo, Alcance, Exclusiones, Riesgos, Milestones, Estimación y Costeo, Trazabilidad); «Estimación y Costeo» lleva una fila por User Story del alcance (código, título, talla, # CA, horas de persona y de agente de IA de QA y de Dev, totales de QA, Dev y general) y los totales del Sprint (`/time`, `/cost`, `/time_agent`, `/cost_agent`), tomados de `estimate.py`; el objetivo y las exclusiones salen del DSP y los riesgos, solo de `--project-data` (nunca se inventan). Se crea con el DSP salvo que ya exista gobernado aparte: en ese caso se pasa `--project-issue-iid`, se enlaza desde cada historia y no se modifica. Labels de equipo como `AI Cowork` o `Status :: PENDING` se añaden con `--label`. Presentar la vista previa y, con autorización humana, repetir con `--mode create|update|sync --approved-by human:<nombre>`.
3b. **Tareas de cada User Story** (las crea o completa `gitlab_issues.py` junto con la historia): dos issues con el label `Task`, uno para Desarrollo (label `Dev`, título `US{iid}: Coordinación del desarrollo con Superpowers`, trabajo en modo Cowork con un agente de IA y el harness Claude Code usando Superpowers; `templates/task-issue-dev.md`) y otro para Calidad (label `QA`, título `US{iid}: Coordinación del Aseguramiento de Calidad`; `templates/task-issue-qa.md`). La descripción de ambos es un markdown con tabla de contenido y tres secciones: Scope (la tarea según el rol), Acceptance Criteria y Condition of Done. Cada tarea queda asociada al mismo Milestone de la historia y enlazada a ella (`relates_to`). Si ya existe, se reutiliza y se corrigen sus labels, Milestone y enlace; no se duplica.
4. Las operaciones son idempotentes: cada issue se encuentra por el marcador `concept_id: <ID>` de su descripción (no se duplica aunque cambie el título), `update` y `sync` agregan labels sin quitar los del equipo y ningún script cierra, reabre ni elimina nada. Una historia que no está en el DSP o en el SSP no se publica: es un cambio (`CHG`). Los documentos OKF siguen siendo la fuente de verdad; el issue es una proyección.
5. Detectar deriva: issues `User Story` o `Proyecto` en GitLab que no están en el plan y elementos del plan sin issue; revisar labels y tablero con el plan (`SSP`).
6. Registrar en el manifiesto de publicación (`templates/publication-manifest.md`) el Milestone y el linaje `concepto <-> proyecto + issue_iid` (las filas `lineage` y `control_pack_row` que devuelven los scripts) y la deriva; copiar los ids al «Sprint GitLab Control Pack» y a la Trazabilidad del SSP.
7. Verificar con `report-userstory-testcase` que los issues `User Story` y `Test Case` quedaron coherentes con el plan.
8. Emitir readiness y solicitar aprobación humana del gate G3.

## Salidas
El skill devuelve el resultado estructurado al orchestrator; solo este persiste el manifiesto, las evidencias y el gate-report bajo `.comsatel/project-management/runs/<run-id>/`. Los entregables tipados van en `management/`.

## Por qué no se usa `gitlab-work-publisher` para los issues
Ese skill exige el formato antiguo de OKF (`okf: google-okf-v0.2`, `artifact: user-story`, gate `REQUIREMENTS_READY`) y etiqueta con `Producto::<X>` y `AI::Cowork`; los documentos actuales usan STD-OKF-001 (`type: US`) y el contrato de este pack pide los labels `User Story` y `Proyecto`. Si se necesitan labels de producto, usar `--label Producto::<X>`.

## Seguridad
- El PAT solo viaja en la cabecera `PRIVATE-TOKEN` desde `GITLAB_PAT`; nunca en archivos, logs, plantillas ni manifiestos.
- Los modos `create`, `update` y `sync` modifican un sistema externo: requieren confirmación humana en el momento; una aprobación de gate previa no los autoriza.
- Solo GitLab. Otro gestor de trabajo requiere ampliar el contrato del pack.
- Los modos que escriben (`create`, `update`, `sync`) de ambos scripts exigen `--approved-by human:<nombre>`; una aprobación de gate previa no los autoriza.

## Gate G3
READY, CONDITIONAL y NOT_READY **no equivalen a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no se habilitan tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar fechas, costos, capacidad, estimaciones, probabilidades, impactos, umbrales ni decisiones; lo que no tenga fuente es una pregunta abierta con responsable.
- Diferenciar hechos, inferencias, supuestos y decisiones humanas; las decisiones (compromiso, cambio, cierre) son siempre humanas.
- Markdown OKF v0.2 con STD-OKF-001 vigente; `status: draft`; no asignar `verified` ni `stable` sin autorización.
- Operaciones sobre sistemas externos (GitLab, repositorios) y commits, merges o cierres de milestone solo con autorización explícita en el momento.
- Si falta un input requerido, registrar el bloqueo y una pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate.py <archivo.md>` (usa `scripts/validate_okf.py` de la raíz del plugin).
- La validación no equivale a aprobación humana ni a publicación. Con STD-OKF-001 v0.1.0-stable, `PCH RMP SSP STR RSK CHG CLS` son tipos aprobados; en `--publication` se rechazan los tipos no registrados en el catálogo.
- Para JSON/YAML operativos en `.comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas
Leer `assets/pathmap.md` de la raíz del plugin. Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` e `id` del frontmatter contra el contrato y guardar en el destino resuelto con `scripts/validate_pathmap.py`. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato.
