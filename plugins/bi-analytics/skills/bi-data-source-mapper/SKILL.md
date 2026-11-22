---
name: bi-data-source-mapper
description: Inventaría fuentes de datos, sistemas origen, linaje, frecuencia y calidad esperada sin conectarse a sistemas. Produce DSM.
metadata:
  version: "0.1.0"
---

# BI Data Source Mapper

Rol: **specialist**. Ejecutar solo con autorización del orquestador.

## Activación
Tarea T-03 (gate G3), después de G1 aprobado. Produce el tipo **DSM** (Data Source Map).

## Entradas
Autorización del orquestador, BIC aprobado, documentación de sistemas origen autorizada y, en BROWNFIELD o EVOLUTION, el inventario existente de fuentes.

## Procedimiento
1. Listar sistemas origen candidatos a partir de los datos que requieren los KPI del BIC.
2. Para cada fuente: sistema, owner técnico y de negocio, tipo (base de datos, API, archivo, hoja de cálculo), frecuencia de extracción, latencia, volumen estimado, clasificación de datos y acceso.
3. Describir el linaje: fuente, transformaciones conocidas y destino previsto.
4. Declarar calidad esperada (completitud, unicidad, oportunidad) y los controles documentados; si no hay evidencia, marcar `gap`.
5. Identificar datos personales o sensibles y el tratamiento requerido.
6. Mapear cada elemento necesario de KPI a su fuente, o registrar el faltante.
7. Incluir un diagrama Mermaid de linaje cuando aporte claridad.

## Comportamiento por modo
- **GREENFIELD:** mapear fuentes candidatas desde los datos que requieren los KPI; `artifact_action` = `CREATE`.
- **BROWNFIELD:** reconstruir de qué fuente sale cada reporte existente (origen real, no el documentado) y marcar las discrepancias.
- **EVOLUTION:** actualizar solo las fuentes nuevas o con cambios de frecuencia, calidad o clasificación; el resto queda `NO_CHANGE`.

## Salida
Plantilla obligatoria: `assets/artifact.md` (estructura, definición y contenido mínimo de cada sección).
`BI-DSM-NNN-<slug>.md` en `./bi/sources/`, con frontmatter OKF (`type: DSM`, `status: draft`, `id: BI-DSM-NNN`).

Secciones mínimas: propósito, inventario de fuentes, linaje, calidad esperada, clasificación de datos, matriz KPI-fuente, gaps, supuestos y validación.

## Restricciones
- No conectarse a sistemas ni ejecutar consultas contra fuentes productivas.
- No afirmar calidad de datos sin evidencia; sin evidencia es `gap`.
- Las credenciales y cadenas de conexión no se documentan.
