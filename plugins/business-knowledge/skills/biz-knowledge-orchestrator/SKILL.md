---
name: biz-knowledge-orchestrator
description: Planifica, coordina y controla los seis skills de conocimiento de negocio (contexto y objetivos, actores y capacidades, glosario, reglas, modelo de información, validación y handoff), sus contratos, dependencias, gates y rutas bajo ./business.
metadata:
  version: "0.1.0"
---

# Business Knowledge Orchestrator

## Activación
Usar ante iniciativas Greenfield, Brownfield o Evolution que requieran construir o actualizar la línea base de conocimiento de negocio (contexto, objetivos, actores, capacidades, glosario, reglas y modelo de información), o para retomar un run con gates pendientes. No reemplaza a los skills especializados.

## Responsabilidad
1. Identificar escenario, alcance, producto, fuentes y resultados requeridos.
2. Crear `.comsatel/business-knowledge/runs/<run-id>/` con plan, ledger de tareas y registro de gates.
3. Seleccionar pasos según escenario y entregables solicitados, sin omitir precondiciones.
4. Encargar el trabajo al skill correspondiente con un contrato de rutas; validar sus salidas contra `references/workflow-contract.md`.
5. Detener dependientes cuando un gate previo esté pendiente o bloqueado. No aprobar gates.
6. Consolidar trazabilidad y preparar el handoff para aprobación y publicación gobernada.

## Flujo base
G0 alcance y fuentes -> G1 contexto y objetivos (`biz-context-objectives-analyst`: BCP, BO) -> G2 actores y capacidades (`biz-stakeholder-capability-mapper`: STK, BCAP) -> G3 glosario (`biz-glossary-curator`: TRM) -> G4 reglas (`biz-rules-modeler`: BR) -> G5 modelo de información (`biz-information-model-designer`: IMD; `biz-scenario-modeler`: BSN) -> G6 validación y handoff (`biz-pack-validator-publisher`).

El orden no es arbitrario: reglas y modelo de información usan términos del glosario, y el modelo cita las reglas. (El plan generado por `workflow.py` es el mismo en Greenfield, Brownfield y Evolution; partir de la línea base existente depende de estas instrucciones y de la revisión humana, sin tarea ni gate de línea base. La evidencia de `transition` y `approve-gate` debe ser un archivo existente dentro del workspace.) Brownfield y Evolution parten de la búsqueda de artefactos existentes en `business/`: se actualizan, no se reemplazan. El escenario `incremental` actualiza una línea base ya aprobada y omite G1 y G2 (exige `--justification`).

## Control del run
Para un cambio que no toca el modelo de información, `init ... --omit G5 --justification "<motivo>"` omite T05 y T07 (IMD y BSN) y G5. `python scripts/workflow.py init <run> --scenario greenfield|brownfield|evolution|incremental --workspace <raíz>`. El gate de entrada de cada tarea es el gate previo incluido; el de cierre es el propio. `check` rechaza ciclos de gates. Cada gate se aprueba con `approve-gate --actor human:<nombre> --evidence <ref>`; los scripts no autentican identidad.

## Política de gates
READY, CONDITIONAL y NOT_READY son resultados técnicos; solo la aprobación de una persona autorizada habilita dependientes. No afirmar que un registro JSON autentica identidad. No commit, merge ni publicación automáticos.

## Relación con requirements-engineering
Este pack es dueño de BR, IMD y TRM. `requirements-engineering` consume la línea base de negocio: su gate G2 se aprueba con evidencia del handoff G6 de este pack (o con una decisión humana explícita de continuar sin él).

## Rutas
Operativo: `.comsatel/business-knowledge/runs/<run-id>/`. Entregables en `business/`: `context-packs/`, `objectives/`, `stakeholders/`, `capabilities/`, `terms/`, `rules/` e `information-model/` (ver `assets/pathmap.md`).

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate_okf.py <archivo.md>` desde la raíz del plugin (o el wrapper `scripts/validate.py`).
- La validación no equivale a aprobación humana ni a publicación. En `--publication` se rechazan tipos no aprobados.
- Para outputs operativos JSON/YAML en `comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Enrutamiento obligatorio por `assets/pathmap.md` (v1.0.0)
Al iniciar G0, leer `assets/pathmap.md` y registrar la versión en el run. Para cada tarea, identificar `document_type`, resolver `output_dir`, emitir el contrato individual (`workspace_root`, `run_id`, `skill`, `document_type`, `output_dir`, `pathmap_version`, `override`, `gate`, `inputs`, `required_standard`) y entregarlo al skill. Comprobar con `scripts/validate_pathmap.py` los manifiestos reales y el frontmatter antes de dar por buena la salida técnica de G1 a G6. Bloquear tipos desconocidos, divergencias y cambios no autorizados. Solo una instrucción explícita del usuario habilita una excepción registrada. No inferir aprobaciones humanas ni tipos documentales.
