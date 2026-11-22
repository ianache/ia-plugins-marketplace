---
name: mgt-risk-change-controller
description: Mantener el registro de riesgos, dependencias y bloqueos, y tramitar solicitudes de cambio con su impacto. Usar para RSK; CHG; riesgos; dependencias; control de cambios.
---

# Risk & Change Controller

## Activación
Usar cuando se requiera producir RSK, CHG. Puede ejecutarse individualmente con sus precondiciones o por `mgt-delivery-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Plan e iteraciones aprobados (G1 a G3), riesgos de negocio (`BRISK` en el `BCP`), ASR/ADR de arquitectura, análisis de impacto (`IMP`), decisión de calidad (`QDC`) cuando exista, y el estado real del trabajo. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Consolidar riesgos desde las fuentes: descripción causa-evento-consecuencia, probabilidad e impacto según la fuente o la persona responsable, dueño, respuesta, disparador y estado.
2. Registrar dependencias y bloqueos con responsable y fecha límite si la fuente la da; distinguir bloqueo actual de riesgo potencial.
3. Por cada solicitud de cambio crear un `CHG` (`templates/change-request.md`): qué cambia, por qué, impacto en alcance, plazo, calidad y riesgos (apoyarse en `IMP` cuando haya), alternativas y decisión pendiente.
4. La decisión sobre un `CHG` es humana: registrar quién decide y cuándo; mientras no exista, `change_state` es `proposed`. Al aprobar, completar `approved_by: human:<nombre>`; el `status` del frontmatter sigue el perfil de la KB (`draft`, `stable`, `deprecated`) y nunca toma el valor `approved`. No modificar el roadmap ni el plan por cuenta propia.
5. Para salud del repositorio y causas de fallos pueden usarse `gsd-health` y `gsd-forensics` como fuentes de evidencia.
6. Actualizar `RSK` (`templates/risk-register.md`) en el mismo cambio que cualquier `CHG` que toque riesgos.
7. Ejecutar `scripts/validate.py`, emitir readiness y solicitar aprobación humana del gate G4.

## Salidas
RSK; CHG. `management/risks/RSK-NNN-<slug>.md` (un registro por iniciativa) y `management/changes/CHG-NNN-<slug>.md` (uno por solicitud). Los entregables van en `management/` (no en `.comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/project-management/runs/<run-id>/`.

## Escalas
Usar las escalas de probabilidad e impacto que defina la organización; si no hay, registrar `Por definir` y abrir una pregunta. No inventar puntuaciones.

## Gate G4
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
