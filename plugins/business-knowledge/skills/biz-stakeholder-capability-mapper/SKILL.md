---
name: biz-stakeholder-capability-mapper
description: Mapear partes interesadas, capacidades, cadenas de valor y procesos de negocio AS-IS vinculados a objetivos. Usar para STK; BCAP; capability-map; value-stream.
metadata:
  version: "0.1.0"
---

# Stakeholder & Capability Mapper

## Activación
Usar cuando se requiera producir STK, BCAP. Puede ejecutarse individualmente con sus precondiciones o por `biz-knowledge-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
BCP y BO con gate G1 aprobado, más fuentes de organización, procesos, políticas y roles. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Identificar actores y partes interesadas con rol, interés, responsabilidad e influencia, solo si una fuente los respalda.
2. Identificar capacidades y procesos de negocio impactados; describir su estado AS-IS y los actores que participan.
3. Vincular cada capacidad a uno o más `BO` y a sus actores (`related`); marcar vínculos inferidos.
4. Crear un `STK` por parte interesada y un `BCAP` por capacidad o proceso con las plantillas de `templates/`.
5. Registrar conflictos, vacíos y responsables; no inventar actores, procesos ni organigramas.
6. Ejecutar `scripts/validate.py` y emitir readiness; solicitar aprobación humana del gate G2.

## Salidas
STK; BCAP; mapa de capacidades y procesos como secciones de los BCAP. `business/stakeholders/` y `business/capabilities/`. Los entregables van en `business/` (no en `comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/business-knowledge/runs/<run-id>/`.

## Alcance de BCAP
Un `BCAP` cubre una capacidad, una cadena de valor o un proceso de negocio y su relación con objetivos y actores. No describe sistemas, componentes ni flujos de pantalla (eso pertenece a arquitectura y UX).

## Gate G2
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
