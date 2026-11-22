---
type: DSM
title: "Data Source Map — <alcance>"
description: "<una frase: fuentes, linaje y calidad esperada para los KPI del alcance>"
id: BI-DSM-000
version: "1.0.0"
status: draft
classification: internal
owner: "<team:rol o human:nombre>"
product: "<producto o iniciativa>"
pack: bi-analytics
skill: bi-data-source-mapper
tags: [bi, analytics, data-sources]
generated:
  by: bi-data-source-mapper/1.0.0
  at: "<ISO 8601 con zona>"
sources:
  - id: src-001
    resource: "<URI o ruta de la documentación del sistema origen>"
    title: "<título>"
related: ["BI-BIC-000", "BI-KPI-000"]
---
# Data Source Map — <alcance>

> **Definición:** inventario de los sistemas origen que alimentan los KPI, con su linaje, frecuencia, calidad esperada y clasificación. Se elabora a partir de documentación; no se conecta a los sistemas.
> **Regla:** calidad sin evidencia se declara `gap`, no se afirma.

## 1. Propósito
> **Contenido mínimo:** alcance de los KPI cubiertos y sistemas incluidos.

## 2. Inventario de fuentes
> **Definición:** un registro por sistema origen o archivo.
> **Contenido mínimo por fila:** ID de fuente, sistema, tipo, owner técnico, owner de negocio, frecuencia, latencia, volumen estimado, clasificación de datos y forma de acceso (sin credenciales ni cadenas de conexión).

| ID | Sistema | Tipo (BD, API, archivo, hoja) | Owner técnico | Owner de negocio | Frecuencia | Latencia | Volumen | Clasificación | Acceso |
|---|---|---|---|---|---|---|---|---|---|
| S-01 | | | | | | | | | |

## 3. Linaje
> **Definición:** camino de los datos desde la fuente hasta el modelo dimensional.
> **Contenido mínimo:** diagrama Mermaid que renderiza, y una lista de transformaciones conocidas por fuente. Sin transformaciones documentadas, «Pendiente».

```mermaid
flowchart LR
  S-01[Sistema origen] --> T[Transformación conocida] --> M[Modelo DMD]
```

## 4. Calidad esperada
> **Definición:** controles de calidad previstos por fuente.
> **Contenido mínimo:** por dimensión (completitud, unicidad, oportunidad, conciliación) el control previsto y si existe evidencia de su funcionamiento.

| Fuente | Dimensión | Control previsto | Evidencia |
|---|---|---|---|
| S-01 | Completitud | | Sin evidencia / ref. |

## 5. Matriz KPI-fuente
> **Definición:** qué fuente aporta cada elemento que necesita cada KPI.
> **Contenido mínimo:** una fila por elemento. Si no hay fuente, estado `gap` con pregunta abierta.

| KPI | Elemento necesario | Fuente | Estado |
|---|---|---|---|
| KPI-NNN | | S-01 | Cubierto / gap |

## 6. Datos personales y sensibles
> **Definición:** datos de identificación personal o sensibles presentes en las fuentes y su tratamiento.
> **Contenido mínimo:** lista de campos afectados, base de tratamiento y restricción de acceso. Si no hay, «No identificados» con la revisión realizada.

## 7. Limitaciones y pendientes
> **Contenido mínimo:** gaps abiertos, fuentes no verificadas y responsable de cada uno.

## 8. Validación
- [ ] Cada fuente tiene owner técnico y de negocio
- [ ] Ninguna cadena de conexión ni credencial aparece en el documento
- [ ] Cada elemento de KPI tiene fuente o gap
- [ ] Diagrama de linaje renderiza
- [ ] Clasificación de datos declarada por fuente
