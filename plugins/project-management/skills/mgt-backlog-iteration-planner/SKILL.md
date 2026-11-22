---
name: mgt-backlog-iteration-planner
description: Priorizar el backlog, estimar esfuerzo y costo (humano y agente de IA, con QA manual y automatizado) y producir el Sprint Scope Pack (SSP) a partir de un DSP aprobado: Sprint Goal, historias, dependencias, riesgos, compromiso y control del Milestone. Usar para SSP; sprint; backlog; Sprint Goal.
metadata:
  version: "0.1.0"
---

# Backlog & Sprint Planner

## Activación
Usar cuando se requiera producir SSP. Puede ejecutarse individualmente con sus precondiciones o por `mgt-delivery-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
`PCH` y `RMP` con gate G1 aprobado; el `DSP` (Development Scope Pack) aprobado de `requirements-engineering`, que gobierna el alcance, y sus User Stories; capacidad y compromisos entregados por una persona. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Tomar el alcance del roadmap para la iteración y las User Stories candidatas; verificar que cada una cumple la Definition of Ready (criterios de aceptación, dependencias identificadas).
2. Priorizar con criterios explícitos y declarados (valor según los `BO`, riesgo, dependencia, esfuerzo si existe); registrar el criterio usado, no solo el orden.
3. Registrar capacidad y compromisos tal como los da la persona responsable; no estimar velocidad ni horas por cuenta propia. Si falta capacidad, dejar el compromiso en `Por definir`.
4. **Estimar esfuerzo y costo** con la práctica `references/estimation-practice.md` (v3, sobre la v2 aprobada): reunir criterios (`### AC-n`), factores y preguntas abiertas por historia, los TC manuales y automatizados de `qa-design` (campo `execution` de cada `TC`), días hábiles del Sprint, puestos y tipo de cambio; ejecutar `python scripts/estimate.py <entrada.json> --format text` (ejemplo en `examples/estimate-input.example.json`). Resultado: `/time` y `/cost` del humano (desarrollo con Superpowers más QA; S/ 30.00 por hora) y `/time_agent` y `/cost_agent` del agente de IA (suscripción USD 25.00 al mes prorrateada al Sprint). Son estimaciones de referencia: revisar los avisos (tallas L/XL, historias sin TC, coeficientes de QA y agente sin calibrar, tipo de cambio pendiente), dividir toda historia XL y no inventar el tipo de cambio.
5. Redactar el SSP (`templates/sprint-scope-pack.md`, `type: SSP`, con `dsp_id`): Sprint Goal, Scope (incluye, excluye, dependencias y riesgos), priorización con su criterio y Definition of Ready por historia, User Stories del DSP, referencia de esfuerzo y costo, compromiso, criterios de cierre del Sprint, trazabilidad, descripción del Milestone (cabecera `/project`, `/subproject`, `/cost`, `/time`, `/client`, `/group`, `/cost_agent`, `/time_agent` y texto del Sprint) y Sprint GitLab Control Pack. El SSP organiza el trabajo del DSP y no lo amplía: una historia fuera del DSP es un cambio (`CHG`), no una adición al SSP, y una historia que no cumple el DoR queda en Excluye con ese motivo.
6. Para trabajo dentro de un repositorio, el plan puede alimentar `gsd-plan-phase`; la revisión del backlog en el repositorio se hace con `gsd-review-backlog`.
7. Ejecutar `scripts/validate.py`, emitir readiness y solicitar aprobación humana del gate G2.

## Salidas
SSP. `management/sprints/SSP-NNN-<slug>.md`, un archivo por Sprint. Los entregables van en `management/` (no en `.comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/project-management/runs/<run-id>/`.

## Regla de compromiso
El compromiso de una iteración es una decisión humana. El skill propone, no compromete: el `SSP` queda en `status: draft` hasta que quien planifica lo apruebe en el gate.

## Gate G2
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
