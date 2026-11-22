---
type: CTLG
title: "Catálogo de KPI — <producto o iniciativa>"
description: "<una frase: qué KPI indexa el catálogo y de qué producto>"
id: BI-CTLG-001
version: "1.0.0"
status: draft
classification: internal
owner: "<team:rol o human:nombre>"
product: "<producto o iniciativa>"
pack: bi-analytics
skill: bi-kpi-definition-designer
tags: [bi, analytics, kpi, catalogo]
generated:
  by: bi-kpi-definition-designer/1.2.0
  at: "<ISO 8601 con zona>"
sources:
  - id: src-001
    resource: "<ruta del documento BI-KPI-NNN-<slug>.md>"
    title: "<código y nombre oficial del KPI>"
related: ["BI-KPI-NNN"]
---
# Catálogo de KPI — <producto o iniciativa>

> **Definición:** índice de los KPI de un producto, ordenado alfabéticamente por nombre oficial. Un KPI se define únicamente en su documento `BI-KPI-NNN`.
> **Regla:** este documento no repite la definición de ningún KPI (fórmulas, grano, dimensiones, filtros, owner, umbrales, casos límite, trazabilidad ni preguntas de un KPI concreto). Esa información vive solo en el documento del KPI. Aquí figuran el índice, las convenciones que aplican a varios KPI y los registros transversales.

## 1. Índice de KPI
> **Definición:** lista de KPI ordenada por nombre oficial (A a Z, sin distinguir mayúsculas ni tildes).
> **Contenido mínimo:** nombre oficial, código, estado, versión y enlace al documento. Solo se copian estos cuatro campos del frontmatter del documento del KPI.

| Nombre oficial | Código | Estado | Versión | Documento |
|---|---|---|---|---|
| | KPI-NNN | draft | 1.0.0 | [BI-KPI-NNN](./BI-KPI-NNN-slug.md) |

## 2. Resumen
> **Definición:** conteos calculados sobre el índice.
> **Contenido mínimo:** total de KPI y total por estado.

- **Total de KPI:**
- **Por estado:** draft N · stable N · deprecated N

## 3. Notas del catálogo
> **Definición:** información que aplica al catálogo completo y no a un KPI concreto.
> **Contenido mínimo:** alcance (productos y ámbitos incluidos), criterio de orden y KPI excluidos del catálogo con su motivo. Si no hay exclusiones, indicarlo.
> **Opcional:** convenciones compartidas, cobertura de decisiones, registro de decisiones del owner, preguntas abiertas y cambios pendientes fuera del pack, cuando aplican a varios KPI. Cada uno se escribe una sola vez; los documentos KPI lo referencian.

## 4. Validación
- [ ] Cada fila del índice enlaza a un documento `BI-KPI-NNN` existente
- [ ] Nombre, código, estado y versión coinciden con el frontmatter de cada documento
- [ ] Orden alfabético verificado por nombre oficial
- [ ] El catálogo no contiene la definición de ningún KPI concreto
- [ ] Resumen calculado sobre el índice actual
