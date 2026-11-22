---
name: biz-context-objectives-analyst
description: Construir el Business Context Pack con problema u oportunidad, objetivos y KPI, alcance, restricciones, supuestos, riesgos y preguntas abiertas. Usar para BCP; BO; business-context; KPI.
metadata:
  version: "0.1.0"
---

# Business Context & Objectives Analyst

## Activación
Usar cuando se requiera producir BCP, BO. Puede ejecutarse individualmente con sus precondiciones o por `biz-knowledge-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Fuentes gobernadas de negocio (estrategia, planes, PRD, visión, actas, procesos, políticas, contratos) y alcance del run (G0 aprobado). No requiere salidas previas de este pack. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Inventariar fuentes y vacíos; registrar identidad, referencia, fecha o versión y relevancia de cada fuente.
2. Extraer hechos explícitos; separar hechos, inferencias, supuestos, hipótesis y decisiones humanas.
3. Identificar problema u oportunidad, objetivos con resultado e indicador (KPI con línea base y meta si la fuente los da), alcance y exclusiones, restricciones, dependencias, riesgos, supuestos y preguntas abiertas.
4. Preservar los conflictos entre fuentes; no reconciliarlos en silencio.
5. Crear un `BO` por objetivo (plantilla `templates/business-objective.md`) y componer el `BCP` (plantilla `templates/business-context-pack.md`) enlazando los `BO`. Restricciones, supuestos, riesgos y preguntas abiertas son secciones del BCP, no documentos propios.
6. Aplicar `references/validation-rules.md` y `scripts/validate.py`; evaluar `BUSINESS_CONTEXT_READY` con `references/business-context-ready.md`.
7. Emitir readiness y solicitar aprobación humana del gate G1.

## Salidas
BCP; BO. `business/context-packs/BCP-NNN-<slug>.md` y `business/objectives/BO-NNN-<slug>.md`. Los entregables van en `business/` (no en `comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/business-knowledge/runs/<run-id>/`.

## Frontera
Este skill termina en contexto de negocio. Si una fuente sugiere una funcionalidad o requisito, registrar la necesidad de negocio o una pregunta abierta y entregarla al análisis de requisitos; no redactar User Stories, requisitos funcionales, especificaciones de UI, ASR, ADR ni diseños.

## Consumidores
- `requirements-engineering` (Requirement Context Pack), `ux-ui-design` (contexto UX) y `architecture-design` (Architecture Context Pack).
- Linaje: `BO -> Requisito -> User Story -> UXR -> Flujo -> Pantalla -> Criterio de aceptación`.

## Gate G1
READY, CONDITIONAL y NOT_READY **no equivalen a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no se habilitan tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar actores, objetivos, KPI, reglas, estados, relaciones, dependencias ni criterios de aceptación.
- Diferenciar hechos, inferencias, supuestos, hipótesis, vacíos y decisiones humanas; preservar fuentes contradictorias.
- Markdown OKF v0.2 con STD-OKF-001 vigente; `status: draft`; no asignar `verified` ni `stable` sin autorización.
- No crear commits, MR ni publicar la KB sin autorización explícita.
- Si falta un input requerido, registrar el bloqueo y una pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate.py <archivo.md>` (usa `scripts/validate_okf.py` de la raíz del plugin).
- La validación no equivale a aprobación humana ni a publicación. Con STD-OKF-001 v0.1.0-stable, `TRM BCP BO STK BCAP BR IMD` son tipos aprobados; en `--publication` se rechazan los tipos no registrados en el catálogo.
- Para JSON/YAML operativos en `comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas
Leer `assets/pathmap.md` de la raíz del plugin. Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` e `id` del frontmatter contra el contrato y guardar en el destino resuelto con `scripts/validate_pathmap.py`. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato.
