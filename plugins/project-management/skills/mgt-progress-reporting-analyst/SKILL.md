---
name: mgt-progress-reporting-analyst
description: Medir avance, esfuerzo (horas /spend) y KPI contra el plan y emitir el informe de estado del periodo. Usar para STR; informe de estado; avance; KPI; horas.
---

# Progress & Reporting Analyst

## Activación
Usar cuando se requiera producir STR. Puede ejecutarse individualmente con sus precondiciones o por `mgt-delivery-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Plan e iteraciones (`SSP`), riesgos y cambios (`RSK`, `CHG`) con G4 aprobado, y datos reales de GitLab (issues, milestones, timelogs) del periodo. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Definir periodo y fuentes; los datos se extraen con scripts deterministas, no de memoria: `report-userstory-testcase` (historias y casos), `gitlab-ai-kpi-semanal` (horas y KPI de uso de IA) e `informe-mensual-horas-proyecto` (horas del mes por proyecto), además de `gsd-progress` y `gsd-stats` para el avance dentro del repositorio.
2. Calcular avance contra el plan: hecho / total por iteración e hito, y desvíos; las horas negativas son correcciones y restan.
3. Comparar esfuerzo real con el plan solo si el plan tiene horas dadas por una persona; si no, informar el real sin juicio.
4. Evaluar los KPI definidos en los `BO` con su definición original; no redefinirlos.
5. Clasificar la calidad de datos (horas excluidas, issues sin etiqueta, sin estimación) y declararla en el informe.
6. Asignar el estado (verde, ámbar, rojo) solo con umbrales definidos por la organización; sin umbrales, informar `sin umbral definido` y los datos.
7. Redactar el informe (`templates/status-report.md`) con avance, hitos, riesgos y cambios abiertos (enlazando `RSK` y `CHG`), decisiones requeridas y próximos pasos. Para dashboards usar los skills `dataviz` o `docx`.
8. Ejecutar `scripts/validate.py`, emitir readiness y solicitar aprobación humana del gate G5.

## Salidas
STR. `management/status-reports/STR-NNN-<periodo>.md`, uno por periodo. Los entregables van en `management/` (no en `.comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/project-management/runs/<run-id>/`.

## Cadencia
Es el gate que más se repite: semanal o mensual según la cadencia. El escenario `cadence` del orchestrator ejecuta solo G4 y G5 para un periodo nuevo.

## Datos y credenciales
Los datos de GitLab requieren `GITLAB_PAT` (lectura) en el entorno; nunca pedirlo ni mostrarlo. Las horas negativas restan; solo cuentan issues con las etiquetas definidas por el skill de extracción.

## Gate G5
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
