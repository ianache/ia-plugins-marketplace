---
name: biz-glossary-curator
description: Extraer y documentar conceptos, términos y siglas de negocio en un glosario TRM indexado alfabéticamente, con sinónimos, definición y fuentes con nivel. Usar para TRM; glosario; siglas; definir término.
---

# Business Glossary Curator

## Activación
Usar cuando se requiera producir TRM. Puede ejecutarse individualmente con sus precondiciones o por `biz-knowledge-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
BCP, STK y BCAP con sus gates aprobados; fuentes autorizadas del producto o dominio; glosario existente (se actualiza, no se reemplaza); acceso web solo para fuentes externas N1. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Declarar fuentes analizadas, alcance (producto o dominio) y consumidor.
2. Listar términos candidatos y conservar solo los que pasan la prueba de inclusión (abajo).
3. Para cada término, buscarlo en `business/terms/CTLG-TRM.md` por nombre, sinónimo y forma completa. Si existe, editar su archivo (fuentes, sinónimos, notas); si no, crearlo con `python scripts/glossary.py new <workspace>/business/terms "<Nombre>" --product <PRODUCTO>` y completar todos los `<...>`.
4. Asignar a cada fuente un nivel según `assets/source-levels.md`. Para significados definidos fuera de la organización (estándares, siglas técnicas, productos de terceros) consultar la fuente N1 y registrar URL y fecha de consulta.
5. Registrar contradicciones entre fuentes en **Notas** del término y como pregunta abierta; conservar ambas fuentes.
6. Ejecutar `python scripts/glossary.py build <dir>` (copia la Definición a `description`, deriva `sources` y regenera el catálogo `CTLG-TRM.md`; elimina el `index.md` obsoleto si existe) y luego `python scripts/glossary.py check <dir>` hasta 0 errores.
7. Emitir readiness y solicitar aprobación humana del gate G3.

## Salidas
No crear un glosario como documento libre con otro `type` (p. ej. `Business Glossary`, `GLS-*`). El glosario es solo `TRM-*.md` más `CTLG-TRM.md`, generados con `glossary.py`; `check` rechaza cualquier otro documento en `business/terms/`.
TRM; `business/terms/TRM-NNN-<slug>.md` por término y `business/terms/CTLG-TRM.md` (CTLG: índice alfabético con ID, término, sinónimos, estado y versión; sin definiciones). No se genera `index.md`. Los entregables van en `business/` (no en `comsatel/`); las evidencias de ejecución y de gate, en `.comsatel/business-knowledge/runs/<run-id>/`.

## Prueba de inclusión
Incluir un término cuando la fuente le da un significado de negocio específico: actores, entidades, productos, conceptos, estados, métricas, sistemas de negocio y las siglas que usan las fuentes.

Excluir: identificadores de artefactos (`BR-*`, `TRM-*`, `IMD-*`, `EVD-*`), vocabulario del método documental (READY, CONDITIONAL, confianza, clasificación) y palabras comunes con su sentido ordinario.

## Reglas
- El glosario es dueño de las definiciones y sinónimos: `biz-rules-modeler` y `biz-information-model-designer` enlazan a los términos y nunca los editan; un concepto nuevo se pide aquí como pregunta.
- Una definición sin fuente N1/N2 se clasifica `gap`. No usar conocimiento propio del modelo como fuente.
- Una sigla o abreviatura exige `Forma completa` (o `Desconocida`).

## Gate G3
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
