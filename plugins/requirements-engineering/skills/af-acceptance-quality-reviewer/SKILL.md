---
name: af-acceptance-quality-reviewer
description: Revisar criterios Given/When/Then, negativos, observabilidad y testabilidad. Usar para revisión de aceptación incorporada en US/RCP; métricas de cobertura y DoR devueltas como payload al orchestrator.
---

# af-acceptance-quality-reviewer

## Activación
Usar cuando revisar criterios given/when/then, negativos, observabilidad y testabilidad. Puede ejecutarse individualmente con sus precondiciones o por `af-requirements-orchestrator`.

## Entradas obligatorias
HU (G3) y reglas BR de la línea base de negocio (G2, plugin `business-knowledge`). Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Delimitar producto, iniciativa, alcance y consumidor del resultado.
2. Inspeccionar fuentes autorizadas y versionadas; registrar provenance y clasificación de cada afirmación.
3. Consultar `references/technical-guidance.md`.
4. Elaborar artefactos conforme a `references/okf-v1.3-profile.md` y `templates/deliverable.md`; preservar los templates originales de cada capacidad.
5. Verificar completitud, contradicciones, IDs, fuentes, preguntas, owners y trazabilidad.
6. Ejecutar `scripts/validate.py` sobre el documento, emitir evidencia y solicitar aprobación humana G4.

## Salidas
revisión de aceptación incorporada en US/RCP; métricas de cobertura y DoR devueltas como payload al orchestrator. Publicar borradores bajo `requirements/` en la KB de producto; payloads de ejecución devueltos al orchestrator; solo el orchestrator persiste evidencias y estado bajo `.comsatel/requirements-engineering/runs/<run-id>/`.

## Gate G4
Estado `READY`, `CONDITIONAL` o `NOT_READY` **no equivale a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no habilitar tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar actores, reglas, dependencias, prioridades, comportamientos ni criterios de aceptación.
- Diferenciar hechos, inferencias, supuestos, hipótesis, vacíos y decisiones humanas.
- Una User Story por archivo. El ID es `RCP-NNN-US-NNN` y es globalmente único (ver `af-user-story-designer`); un ID previo (`HU-NN-NN`, `US-001`) va en `legacy_id`, no en `id`. Reutilizar preguntas y EVD existentes.
- Markdown OKF v0.2 con STD-OKF-001 vigente; no asignar `verified` ni `stable` sin autorización.
- No crear commits, MR ni publicar KB sin autorización explícita.
- Si el input requerido no existe, registrar bloqueo y pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate_okf.py <archivo.md>` desde la raíz del plugin (o el wrapper local `scripts/validate.py`).
- El resultado de validación no equivale a aprobación humana ni a publicación. En `--publication`, rechazar tipos no aprobados y metadatos inválidos.
- Aplicar STD-OKF-001 v1.9.0-stable como perfil objetivo; usar el catálogo aprobado de la versión vigente.
- Para outputs operativos JSON/YAML en `.comsatel/`, usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas (v1.5.0)
Leer `../../assets/pathmap.md` desde el directorio del skill (o `assets/pathmap.md` desde la raíz del plugin). Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` del frontmatter contra el contrato y guardar en el destino resuelto. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato. Nunca escribir documentos especializados en `.comsatel/`. Ejecutar validación OKF v1.9.0-stable.
