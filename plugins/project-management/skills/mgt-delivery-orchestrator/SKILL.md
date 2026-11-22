---
name: mgt-delivery-orchestrator
description: Planifica, coordina y controla los seis skills de gestión de entrega (acta y roadmap, backlog e iteraciones, publicación en GitLab, riesgos y cambios, avance e informes, cierre), sus contratos, dependencias, gates y rutas bajo ./management.
---

# Delivery Management Orchestrator

## Activación
Usar para planificar y gobernar la entrega de una iniciativa (de acta a cierre), para planificar una nueva iteración sobre una iniciativa ya iniciada o para ejecutar el ciclo periódico de riesgos e informe de estado. No reemplaza a los skills especializados ni al flujo `gsd-*` de ejecución en repositorio.

## Responsabilidad
1. Identificar escenario, iniciativa, producto, periodo y resultados requeridos.
2. Crear `.comsatel/project-management/runs/<run-id>/` con plan, ledger de tareas y registro de gates.
3. Seleccionar pasos según el escenario, sin omitir precondiciones.
4. Encargar el trabajo al skill correspondiente con un contrato de rutas; validar sus salidas contra `references/workflow-contract.md`.
5. Detener dependientes cuando un gate previo esté pendiente o bloqueado. No aprobar gates ni tomar decisiones de compromiso, cambio o cierre.

## Flujo base
G0 alcance -> G1 acta y roadmap (`mgt-charter-roadmap-planner`: PCH, RMP) -> G2 Sprint Scope Pack (`mgt-backlog-iteration-planner`: SSP) -> G3 publicación en GitLab (`mgt-work-publisher-synchronizer`) -> G4 riesgos y cambios (`mgt-risk-change-controller`: RSK, CHG) -> G5 avance e informe (`mgt-progress-reporting-analyst`: STR) -> G6 cierre (`mgt-release-closure-auditor`: CLS).

Riesgos y cambios van antes del informe porque este último los cita. G4 y G5 son cíclicos: se repiten en cada periodo.

## Escenarios
- `initiative`: G0 a G6 completo.
- `iteration`: planifica una iteración nueva sobre un acta y roadmap ya aprobados; omite G1 (exige `--justification`).
- `cadence`: ciclo periódico; ejecuta solo G4 y G5 (omite G1, G2, G3 y G6; exige `--justification`). Usar un run nuevo por periodo (por ejemplo `2026-W43`).

## Control del run
Evidencia de `transition`: archivo existente; de `approve-gate`: archivo existente o referencia (URL o ID tipo `MR-12`). `python scripts/workflow.py init <run> --scenario initiative|iteration|cadence --workspace <raíz>`. El gate de entrada de cada tarea es el gate previo incluido; el de cierre es el propio. Cada gate se aprueba con `approve-gate --actor human:<nombre> --evidence <ref>`; los scripts no autentican identidad.

## Relación con otros packs
- **Entradas:** `business-knowledge` (BCP, BO, BCAP, BRISK), `requirements-engineering` (US, RCP, DSP, IMP), `architecture-design` (ASR, ADR) y `qa-design` (QDC).
- **Salidas:** issues en GitLab, informes y el cierre. Solo GitLab como gestor de trabajo.
- **Ejecución en repositorio:** `gsd-*` se invoca como herramienta; este pack no lo duplica ni lo mueve.

## Política de gates
READY, CONDITIONAL y NOT_READY son resultados técnicos; solo la aprobación de una persona autorizada habilita dependientes. Publicar en GitLab, hacer commit, merge, `ship` o cerrar milestones exige autorización explícita en el momento.

## Rutas
Operativo: `.comsatel/project-management/runs/<run-id>/`. Entregables en `management/`: `charters/`, `roadmaps/`, `sprints/`, `risks/`, `changes/`, `status-reports/` y `closure/` (ver `assets/pathmap.md`).

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate_okf.py <archivo.md>` desde la raíz del plugin (o el wrapper `scripts/validate.py`).
- La validación no equivale a aprobación humana. En `--publication` se rechazan tipos no aprobados.
- Para outputs operativos JSON/YAML en `.comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Enrutamiento obligatorio por `assets/pathmap.md` (v1.0.0)
Al iniciar G0, leer `assets/pathmap.md` y registrar la versión en el run. Para cada tarea, identificar `document_type`, resolver `output_dir`, emitir el contrato individual (`workspace_root`, `run_id`, `skill`, `document_type`, `output_dir`, `pathmap_version`, `override`, `gate`, `inputs`, `required_standard`) y entregarlo al skill. Comprobar con `scripts/validate_pathmap.py` los manifiestos reales y el frontmatter antes de dar por buena la salida técnica de G1 a G6. Bloquear tipos desconocidos, divergencias y cambios no autorizados.
