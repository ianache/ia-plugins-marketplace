---
name: bi-dimensional-model-designer
description: Diseña hechos, dimensiones, grano, jerarquías y reglas de cambio histórico a partir de KPI y DSM. Produce DMD.
---

# BI Dimensional Model Designer

Rol: **specialist**. Ejecutar solo con autorización del orquestador.

## Activación
Tarea T-04 (gate G4), después de G2 y G3 aprobados. Produce el tipo **DMD** (Dimensional Model Design).

## Entradas
Autorización del orquestador, KPI y DSM aprobados, IMD de `business-knowledge` cuando exista (para alinear conceptos).

## Estándar de modelado

Aplicar de forma obligatoria [`resources/fact-dim-modelling-standard.md`](../../resources/fact-dim-modelling-standard.md) a nombres de tablas, campos, claves, restricciones, índices y demás objetos. La plantilla DMD debe usar nombres canónicos `fact_` y `dim_`, declarar claves sustitutas y FKs por rol, documentar medidas y reglas de unicidad, y marcar como `TBD` las decisiones físicas dependientes de una plataforma aún no definida. En Brownfield, conservar el nombre existente y registrar la desviación; no renombrar sin autorización.

## Procedimiento
1. Declarar el proceso de negocio que modela cada tabla de hechos y su **grano** (una fila representa exactamente un evento o estado).
2. Derivar hechos aditivos, semiaditivos o no aditivos para cada medida de KPI, y justificar la agregación.
3. Definir dimensiones conformadas, sus atributos, jerarquías y claves sustitutas.
4. Para cada dimensión, elegir el tipo de cambio histórico (SCD 0, 1, 2 o 3) y justificarlo.
5. Verificar que cada KPI es calculable desde el modelo y que cada medida tiene una fuente en DSM o un `gap`.
6. Describir reglas de carga y de calidad a nivel de modelo, sin escribir código de ETL.
7. Incluir un diagrama Mermaid `erDiagram` o de estrella cuando aporte claridad.
8. Nombrar tablas, columnas, claves, constraints e índices según el estándar; declarar nombres lógicos y justificar candidatos de índices sin escribir DDL.

## Comportamiento por modo
- **GREENFIELD:** diseñar el modelo desde KPI y DSM; `artifact_action` = `CREATE`.
- **BROWNFIELD:** reconstruir el modelo existente (tablas, grano actual) y documentar las desviaciones respecto del grano que requieren los KPI.
- **EVOLUTION:** cambiar solo las tablas o dimensiones afectadas. Un cambio de grano exige nueva versión del DMD y reabre el DSH.

## Salida
Plantilla obligatoria: `assets/artifact.md` (estructura, definición y contenido mínimo de cada sección).
`BI-DMD-NNN-<slug>.md` en `./bi/model/`, con frontmatter OKF (`type: DMD`, `status: draft`, `id: BI-DMD-NNN`).

Secciones mínimas: propósito, procesos y grano, tablas de hechos, dimensiones, jerarquías, SCD, matriz KPI-medida-fuente, reglas de carga, nombres y objetos, gaps, diagrama y validación.

## Restricciones
- Un KPI no calculable desde el modelo bloquea G4.
- No mezclar grano en una misma tabla de hechos.
- No generar DDL ni scripts de ETL en este skill; si se requiere, se trata en otro pack. El estándar prescribe nombres y candidatos lógicos, no sintaxis física específica de motor.
