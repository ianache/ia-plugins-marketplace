---
name: af-requirements-orchestrator
description: Planifica, coordina y controla los cinco skills de ingeniería de requisitos, sus contratos, dependencias, gates y handoff, preservando cobertura AF-101/102/103.
metadata:
  version: "0.1.0"
---

# Requirements Engineering Orchestrator

## Activación
Usar ante iniciativas de requisitos Greenfield, Brownfield o Evolution, o para retomar un run con gates pendientes. No reemplaza a los skills especializados.

## Responsabilidad
1. Identificar escenario, alcance, fuentes y resultados requeridos.
2. Crear `.comsatel/requirements-engineering/runs/<run-id>/` con plan, estado y gate-register.
3. Seleccionar pasos según escenario y entregables solicitados, sin omitir precondiciones.
4. Encargar trabajo al skill correspondiente; validar outputs contra `references/workflow-contract.md`.
5. Detener dependientes cuando gate previo esté pendiente o bloqueado. No aprobar gates.
6. Consolidar traceability E2E y preparar handoff para aprobación y publicación gobernada.

## Flujo base
G0 alcance y fuentes -> G1 evidencia/RCP -> G2 línea base de negocio (gate humano; la produce `business-knowledge`) -> G3 HU y épicas (EPC, opcionales) -> G4 criterios -> G5 impactos -> G6 validación y handoff.

(El plan generado por `workflow.py` es el mismo en Greenfield, Brownfield y Evolution; la búsqueda de lo existente y el As-Is/To-Be dependen de estas instrucciones y de la revisión humana, sin tarea ni gate de línea base. La evidencia de `transition` y `approve-gate` debe ser un archivo existente dentro del workspace.) Brownfield y Evolution requieren búsqueda de artefactos existentes, comparación As-Is/To-Be y análisis de impacto; una solicitud de análisis de impacto aislado puede activar G1, el gate G2 y G5 sin generar HU nuevas, documentando la excepción.

## Línea base de negocio (G2)
Las reglas de negocio (`BR`), el modelo de información (`IMD`) y el glosario (`TRM`) los produce el plugin `business-knowledge` (`biz-knowledge-orchestrator`). G2 no tiene tarea ni skill: una persona autorizada lo aprueba (`approve-gate --gate G2 --actor human:<nombre> --evidence <ref>`) citando el handoff G6 aprobado de ese pack, o registrando una decisión explícita de continuar sin línea base. Si faltan BR, IMD o TRM que el RCP o las HU necesitan, registrar el bloqueo y solicitar su creación en `business-knowledge`; no redactarlos aquí. Los skills de este pack referencian esos documentos por ID.

## Control del run
Usar `python scripts/workflow.py init <run> --scenario greenfield|brownfield|evolution|impact-only` (`impact-only` exige `--justification` y omite G3/G4). El gate de entrada de cada tarea es el gate previo; el de cierre es el propio. `check` rechaza ciclos de gates. Cada gate se aprueba con `approve-gate --actor human:<nombre> --evidence <ref>`; los scripts no autentican identidad.

## IDs de User Stories
Los IDs de US son `RCP-NNN-US-NNN` (RCP de origen) y globalmente únicos. Las épicas (`RCP-NNN-EPC-NNN`) se revisan en G3: cada una cita historias existentes en `related`, ninguna historia pertenece a dos épicas y el criterio de agrupación es explícito; `us_ids.py check` verifica las referencias. Al emitir el contrato de G3 al skill de historias, incluir las otras KB (`--also`) y las ramas abiertas (`--git-ref`) que deben considerarse; verificar con `python scripts/us_ids.py check` antes de aprobar G3 y de nuevo en G6. Un ID duplicado bloquea el gate; no se resuelve renumerando historias ya publicadas sin decisión humana y actualización de sus issues.

## Política de gates
READY, CONDITIONAL y NOT_READY son resultados técnicos; solo `approved: true` por humano autorizado habilita dependientes. No afirmar que un registro JSON autentica identidad. No commit/merge/publicación automática.

## Rutas
Operativo: `.comsatel/requirements-engineering/runs/<run-id>/`. Entregables: `requirements/` en KB de producto, preservando rutas canónicas existentes, particularmente `requirements/context-packs/user-stories/`.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate_okf.py <archivo.md>` desde la raíz del plugin (o el wrapper local `scripts/validate.py`).
- El resultado de validación no equivale a aprobación humana ni a publicación. En `--publication`, rechazar tipos no aprobados y metadatos inválidos.
- Aplicar STD-OKF-001 v0.1.0-stable como perfil objetivo; usar el catálogo aprobado de la versión vigente.
- Para outputs operativos JSON/YAML en `.comsatel/`, usar contratos operativos; no forzar frontmatter OKF.

## Enrutamiento obligatorio por `assets/pathmap.md` (v1.5.0)
Al iniciar G0, leer `assets/pathmap.md` y registrar versión en `.comsatel/requirements-engineering/runs/<run-id>/`. Para cada tarea, identificar `document_type` OKF, resolver `output_dir`, emitir contrato individual (`workspace_root`, `run_id`, `skill`, `document_type`, `output_dir`, `pathmap_version`, `override`, `gate`, `inputs`, `required_standard`) y entregarlo al skill especializado. Comprobar con `scripts/validate_pathmap.py` los manifiestos reales y el frontmatter antes de aprobar la salida técnica de G1–G6. Bloquear tipos desconocidos, divergencias y cambios no autorizados. Solo una instrucción explícita del usuario habilita una excepción registrada. No inferir aprobaciones humanas ni tipos documentales.
