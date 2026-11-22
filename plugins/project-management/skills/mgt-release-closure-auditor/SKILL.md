---
name: mgt-release-closure-auditor
description: Auditar el hito o la iniciativa contra el acta, verificar preparación de entrega y emitir el cierre con lecciones aprendidas. Usar para CLS; cierre; auditoría de hito; release readiness; lecciones aprendidas.
---

# Release & Closure Auditor

## Activación
Usar cuando se requiera producir CLS. Puede ejecutarse individualmente con sus precondiciones o por `mgt-delivery-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Todos los entregables de G1 a G5, la decisión de calidad (`QDC`) del pack de QA cuando exista, y el estado real de issues, cambios y riesgos. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Ejecutar `python scripts/check_management.py --workspace <raíz>`: valida OKF y ruta de cada documento, enlaces, IDs de `related` y que no queden `CHG` pendientes de decisión ni `RSK` abiertos sin dueño.
2. Auditar el hito o la iniciativa contra los criterios de éxito del `PCH` y los KPI de los `BO`; para el repositorio apoyarse en `gsd-audit-milestone`.
3. Verificar la preparación de entrega: calidad (`QDC` humana), issues abiertos, cambios y riesgos residuales; `gsd-ship` y `gsd-pr-branch` solo preparan la entrega y no se invocan sin autorización humana.
4. Redactar el cierre (`templates/closure-report.md`): resultado frente a los criterios de éxito, desvíos de alcance, plazo y esfuerzo, riesgos y cambios finales, lecciones aprendidas y transferencia a operación.
5. Emitir READY, CONDITIONAL o NOT_READY y solicitar aprobación humana del gate G6. No cerrar milestones, hacer merge ni publicar de forma automática.

## Salidas
CLS. `management/closure/CLS-NNN-<slug>.md`. Los entregables van en `management/` (no en `.comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/project-management/runs/<run-id>/`.

## Límites de la validación
`check_management.py` verifica estructura, rutas, enlaces e IDs; no certifica veracidad de las cifras, la calidad ni la aprobación humana. Con STD-OKF-001 v1.9.0-stable estos tipos están aprobados y ya no se emiten avisos `type propuesto`.

## Gate G6
READY, CONDITIONAL y NOT_READY **no equivalen a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no se habilitan tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar fechas, costos, capacidad, estimaciones, probabilidades, impactos, umbrales ni decisiones; lo que no tenga fuente es una pregunta abierta con responsable.
- Diferenciar hechos, inferencias, supuestos y decisiones humanas; las decisiones (compromiso, cambio, cierre) son siempre humanas.
- Markdown OKF v0.2 con STD-OKF-001 vigente; `status: draft`; no asignar `verified` ni `stable` sin autorización.
- Operaciones sobre sistemas externos (GitLab, repositorios) y commits, merges o cierres de milestone solo con autorización explícita en el momento.
- Si falta un input requerido, registrar el bloqueo y una pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate.py <archivo.md>` (usa `scripts/validate_okf.py` de la raíz del plugin).
- La validación no equivale a aprobación humana ni a publicación. Con STD-OKF-001 v1.9.0-stable, `PCH RMP SSP STR RSK CHG CLS` son tipos aprobados; en `--publication` se rechazan los tipos no registrados en el catálogo.
- Para JSON/YAML operativos en `.comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas
Leer `assets/pathmap.md` de la raíz del plugin. Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` e `id` del frontmatter contra el contrato y guardar en el destino resuelto con `scripts/validate_pathmap.py`. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato.
