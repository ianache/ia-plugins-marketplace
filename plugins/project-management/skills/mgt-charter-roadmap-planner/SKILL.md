---
name: mgt-charter-roadmap-planner
description: Elaborar el acta de la iniciativa (alcance, criterios de éxito, restricciones, actores) y su roadmap con hitos y dependencias. Usar para PCH; RMP; charter; roadmap; hitos.
metadata:
  version: "0.1.0"
---

# Charter & Roadmap Planner

## Activación
Usar cuando se requiera producir PCH, RMP. Puede ejecutarse individualmente con sus precondiciones o por `mgt-delivery-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Alcance del run (G0 aprobado) y, si existen, la línea base de negocio (`BCP`, `BO`, `BCAP` de `business-knowledge`), el contexto de requisitos (RCP, paquetes de alcance `DSP`) y las decisiones de arquitectura (ASR, ADR). Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Inventariar fuentes y vacíos; registrar identidad, referencia y fecha de cada fuente.
2. Enlazar el acta con los objetivos de negocio (`BO`) y las capacidades (`BCAP`) que la justifican; si no existen, registrarlo como vacío y pedir su creación en `business-knowledge`.
3. Redactar el acta (`templates/charter.md`): propósito, alcance y exclusiones, criterios de éxito medibles ligados a KPI de los `BO`, restricciones, supuestos, partes interesadas y responsables, y hitos de alto nivel. Presupuesto, fechas y capacidad solo si una fuente o una persona los da.
4. Delimitar el alcance candidato; cuando haya RCP y User Stories validados, apoyarse en `development-scope-pack-builder` (produce un `DSP`) en lugar de redactar el alcance a mano.
5. Construir el roadmap (`templates/roadmap.md`): fases e hitos con criterio de salida, dependencias entre hitos y con terceros, y el orden propuesto. Marcar como inferencia todo lo que no venga de fuente.
6. Para trabajo de implementación dentro de un repositorio, el roadmap puede mapearse a los hitos y fases de `gsd-new-project` y `gsd-new-milestone`; esos skills ejecutan, este skill planifica.
7. Ejecutar `scripts/validate.py`, emitir readiness y solicitar aprobación humana del gate G1.

## Salidas
PCH; RMP. `management/charters/PCH-NNN-<slug>.md` y `management/roadmaps/RMP-NNN-<slug>.md`. Los entregables van en `management/` (no en `.comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/project-management/runs/<run-id>/`.

## Frontera
No define requisitos, historias de usuario, arquitectura ni diseño; planifica la entrega. Una fecha, un costo o una capacidad sin fuente es una pregunta abierta con responsable, nunca un dato.

## Gate G1
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
