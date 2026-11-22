---
name: biz-information-model-designer
description: Crear y mantener el modelo de información conceptual de negocio (conceptos, relaciones, cardinalidades, reglas y estados) previo a cualquier modelo lógico o físico. Usar para IMD; modelo conceptual; ER de negocio.
---

# Business Information Model Designer

## Activación
Usar cuando se requiera producir IMD. Puede ejecutarse individualmente con sus precondiciones o por `biz-knowledge-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Glosario TRM (G3) y reglas BR (G4) aprobados, BCAP y fuentes funcionales autorizadas; el modelo existente del dominio, si lo hay (se actualiza, no se reemplaza). Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Declarar fuentes, alcance (producto o dominio) y consumidor.
2. Abrir el modelo del alcance; si no existe, crearlo desde `templates/conceptual-model-template.md` con el siguiente `IMD-NNN`.
3. Extraer conceptos candidatos y conservar los que pasan la prueba de concepto; cada uno debe corresponder a un TRM. Si no lo tiene, mantener el concepto y abrir una pregunta para `biz-glossary-curator`; no escribir la definición en el modelo.
4. Extraer relaciones (ID `R-NN`, lenguaje de negocio, cardinalidad, clasificación FACT/INFERENCE/UNKNOWN, fuente, pregunta). Separar conceptos derivados y externos.
5. Dibujar los `erDiagram` de Mermaid (dividir si pasan de ~15 conceptos; marcar `(inf.)` las inferencias) y, para conceptos con ciclo de vida relevante, `stateDiagram-v2` con tablas de estados y transiciones ECA que citen `BR-*`.
6. Listar las reglas BR que actúan sobre cada concepto (sección 6).
7. Ejecutar `python scripts/check_model.py <modelo.md> --extract <tmp>` y corregir errores; si hay `npx`, renderizar cada diagrama con `@mermaid-js/mermaid-cli` para confirmar la sintaxis (rutas absolutas en Windows).
8. Ejecutar `scripts/validate.py`, emitir readiness (sección 10) y solicitar aprobación humana del gate G5.

## Salidas
IMD; `business/information-model/IMD-NNN-<slug>.md`, un archivo por modelo. Los entregables van en `business/` (no en `comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/business-knowledge/runs/<run-id>/`.

## Prueba de concepto
Un concepto pertenece al modelo cuando el negocio lo nombra y se cumple al menos una: se registra, se decide sobre él, tiene reglas u otros conceptos lo refieren. Los actores solo si el negocio registra algo sobre ellos; pantallas, reportes y KPI no son conceptos; los identificadores de artefactos nunca lo son.

## Prueba de estado
Un concepto tiene diagrama de estados cuando el negocio reconoce estados distintos **y** algo decide o controla el paso entre ellos. Cada transición es una regla ECA (Evento, Condición, Acción) con ID `T-<CONCEPTO>-NN` estable. Un estado sin fuente es UNKNOWN más una pregunta `IM-Qn`; no inventar estados.

## Reglas de modelado
- Solo lenguaje de negocio: sin tablas, claves, tipos de dato, índices ni nulabilidad; eso es `LDM`/`PDM` (`data-modeling-database-design`, que toma este modelo como entrada).
- La cardinalidad viene de la fuente; si se infiere, se clasifica INFERENCE con su razonamiento; si no, `UNKNOWN`.
- IDs estables: relaciones `R-NN`, preguntas `IM-Qn`, transiciones `T-<CONCEPTO>-NN`; nunca renumerar (lo retirado queda como `RETIRADA`).
- El glosario es dueño de definiciones y sinónimos; el modelo los enlaza.

## Gate G5
READY, CONDITIONAL y NOT_READY **no equivalen a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no se habilitan tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar actores, objetivos, KPI, reglas, estados, relaciones, dependencias ni criterios de aceptación.
- Diferenciar hechos, inferencias, supuestos, hipótesis, vacíos y decisiones humanas; preservar fuentes contradictorias.
- Markdown OKF v0.2 con STD-OKF-001 vigente; `status: draft`; no asignar `verified` ni `stable` sin autorización.
- No crear commits, MR ni publicar la KB sin autorización explícita.
- Si falta un input requerido, registrar el bloqueo y una pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate.py <archivo.md>` (usa `scripts/validate_okf.py` de la raíz del plugin).
- La validación no equivale a aprobación humana ni a publicación. Con STD-OKF-001 v1.9.0-stable, `TRM BCP BO STK BCAP BR IMD` son tipos aprobados; en `--publication` se rechazan los tipos no registrados en el catálogo.
- Para JSON/YAML operativos en `comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas
Leer `assets/pathmap.md` de la raíz del plugin. Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` e `id` del frontmatter contra el contrato y guardar en el destino resuelto con `scripts/validate_pathmap.py`. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato.
