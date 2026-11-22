---
name: biz-rules-modeler
description: Extraer reglas de negocio, estados, validaciones, permisos y excepciones con trazabilidad a fuentes y términos del glosario. Usar para BR; reglas de negocio; rules-traceability.
metadata:
  version: "0.1.0"
---

# Business Rules Modeler

## Activación
Usar cuando se requiera producir BR. Puede ejecutarse individualmente con sus precondiciones o por `biz-knowledge-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Glosario TRM con gate G3 aprobado, BCP/BO/BCAP con sus gates aprobados y fuentes funcionales autorizadas (visión, procesos, políticas, User Stories, decisiones registradas). Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Delimitar producto, iniciativa, alcance y consumidor del resultado.
2. Inspeccionar fuentes autorizadas y versionadas; registrar provenance y clasificación (hecho, inferencia, supuesto, hipótesis, decisión, vacío) de cada afirmación.
3. Antes de numerar, buscar en `business/rules/` las reglas existentes por título y enunciado. Si una regla ya existe, reutilizar su `BR-NNN` y no crear otra; el ID local de un documento fuente (p. ej. `BR-01`) no es un ID del workspace. Extraer reglas, estados, validaciones, permisos y excepciones en un JSON (lista de objetos; formato en la cabecera de `scripts/rules.py`). Generar un `BR-NNN.md` por regla con `python scripts/rules.py from-json <workspace>/business/rules <reglas.json> --product <PRODUCTO>`: el lote es todo o nada. Cada regla enlaza los TRM que usa; una regla sin fuente exige pregunta abierta.
4. Preservar contradicciones, vacíos y owners; absence of evidence es un vacío, no prueba de inexistencia.
5. Regenerar el catálogo con `python scripts/rules.py build <workspace>/business/rules`: `CTLG-BR.md` (CTLG) con una fila por regla y sin enunciados. Alta o baja de una regla exige volver a generarlo en el mismo cambio.
6. Ejecutar `python scripts/rules.py check <workspace>/business/rules` (cada BR, texto de plantilla y correspondencia 1:1 con el catálogo), `scripts/validate.py` sobre cada regla y `python <plugin>/scripts/validate_pathmap.py --check-catalog BR --workspace <raíz>`.
7. Emitir readiness y solicitar aprobación humana del gate G4.

## Salidas
BR; `business/rules/BR-NNN.md` (uno por regla) y `business/rules/CTLG-BR.md` (CTLG); matriz de trazabilidad de reglas como sección de cada BR. Los entregables van en `business/` (no en `comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/business-knowledge/runs/<run-id>/`.

## Trazabilidad
Cada BR declara en `related` los TRM, BCAP y BO a los que aplica, y en `sources` la evidencia. Las reglas viven en un solo lugar: `requirements-engineering`, `ddd-domain-design` y `data-modeling-database-design` las referencian por ID y no las redefinen.

## Catálogos narrativos de reglas
Un catálogo narrativo (p. ej. un documento por producto o módulo) es `type: CTLG` con `indexes: BR` y su propio `id` `CTLG-<NOMBRE>`. Vive en `business/rules/`, enlaza cada regla a su archivo `BR-NNN.md` y no duplica su enunciado. `CTLG-BR.md` sigue siendo el índice único generado por `rules.py build`. Tipos no registrados como `BRC` o `business-rules-catalog` no se usan: el catálogo es `CTLG`.

## Migración de documentos heredados
Para migrar un catálogo o documento anterior al perfil, seguir `references/migracion-documentos-heredados.md`. La migración no cambia el enunciado de las reglas.

## Evidencia
Usar `assets/evidence-schema.md` para el registro de evidencia. Las reglas sin fuente se registran como pregunta abierta con responsable y marcan el resultado CONDITIONAL o NOT_READY.

## Gate G4
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
