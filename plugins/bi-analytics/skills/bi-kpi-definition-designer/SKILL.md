---
name: bi-kpi-definition-designer
description: Define KPI con fórmula, grano, dimensiones, owner, umbrales y trazabilidad a decisiones. Produce un documento KPI por indicador y un catálogo CTLG ordenado alfabéticamente.
---

# BI KPI Definition Designer

Rol: **specialist**. Ejecutar solo con autorización del orquestador.

## Activación
Tarea T-02 (gate G2), después de G1 aprobado. Produce el tipo **KPI** (KPI Definition), uno por indicador, y el tipo **CTLG** (catálogo), un único índice de los KPI del producto.

## Entradas
Autorización del orquestador, BIC aprobado, TRM de `business-knowledge` cuando exista (para nombres y definiciones de términos) y fuentes de definición del negocio.

## Procedimiento
1. Por cada decisión del BIC, proponer los KPI que la soportan o declarar que no hay KPI suficiente.
2. Para cada KPI definir: nombre, objetivo, fórmula en lenguaje de negocio y expresión formal, unidad, grano temporal y geográfico, dimensiones de corte, filtros obligatorios, owner y frecuencia de actualización.
3. Definir umbrales o metas solo si la fuente los documenta; si no, marcarlos como pendientes.
4. Registrar casos límite: divisiones por cero, datos tardíos, cambios de definición y periodos parciales.
5. Verificar que cada KPI referencia la decisión de BIC que soporta.
6. Redactar un documento `BI-KPI-NNN` por KPI, con toda su definición. Un KPI nunca se describe en otro documento.
7. Redactar el catálogo `BI-CTLG-001` después de todos los documentos KPI. Por cada KPI copiar solo cuatro campos del frontmatter del documento: nombre oficial, código, estado y versión. Ordenar las filas por nombre oficial (A a Z, sin distinguir mayúsculas ni tildes).
8. Verificar la consistencia antes de entregar: cada fila del catálogo tiene su documento, sus cuatro campos coinciden con el frontmatter, y el catálogo no contiene la definición de ningún KPI.

## Comportamiento por modo
- **GREENFIELD:** definir cada KPI desde cero; `artifact_action` = `CREATE` para cada documento KPI y para el catálogo.
- **BROWNFIELD:** inventariar los KPI que ya usan los reportes; conciliar cada definición existente con la propuesta y registrar las diferencias como preguntas abiertas en el documento del KPI. No elegir una definición en silencio. El catálogo es `CREATE` si no existe o `UPDATE` si existe.
- **EVOLUTION:** un cambio de fórmula o grano crea una versión nueva del documento del KPI y marca como afectados los KPI dependientes; no editar documentos de KPI no afectados (`NO_CHANGE`). El catálogo es `UPDATE` cuando cambie el nombre, código, estado o versión de algún KPI, y `NO_CHANGE` en otro caso.

## Salida
Dos tipos de documento, ambos en `./bi/kpis/`:

| Tipo | Archivo | Plantilla | Contenido |
|---|---|---|---|
| KPI | `BI-KPI-NNN-<slug>.md`, uno por indicador | `assets/artifact.md` | Definición completa: identificación, fórmula, gobierno, casos límite, cambios, trazabilidad, limitaciones y validación. |
| CTLG | `BI-CTLG-001-catalogo-kpi.md`, uno por producto | `assets/catalog.md` | Índice ordenado alfabéticamente: nombre oficial, código, estado, versión y enlace. Resumen y notas del catálogo. |

- Frontmatter KPI: `type: KPI`, `status: draft`, `id: BI-KPI-NNN`, `related` con el BIC de origen y `BI-CTLG-001`.
- Frontmatter CTLG: `type: CTLG`, `status: draft`, `id: BI-CTLG-001`, `related` con los `BI-KPI-NNN` indexados.

Secciones mínimas del KPI: propósito, fórmula, grano, dimensiones, owner, umbrales, casos límite, trazabilidad a BIC y TRM, supuestos y validación.

## Restricciones
- No inventar KPI, metas ni owners.
- Un nombre de KPI que coincide con un término del glosario se enlaza al término, no se redefine.
- Sin trazabilidad a una decisión de BIC, el KPI queda como `gap` y pregunta abierta en su propio documento.
- El catálogo no repite la definición de ningún KPI. Puede contener convenciones compartidas y registros transversales (decisiones, cobertura, cambios pendientes) que aplican a varios KPI, escritos una sola vez. Ante cualquier diferencia entre el catálogo y un documento KPI, prevalece el documento KPI y el catálogo se regenera.
- Un KPI sin documento `BI-KPI-NNN` no aparece en el catálogo.
