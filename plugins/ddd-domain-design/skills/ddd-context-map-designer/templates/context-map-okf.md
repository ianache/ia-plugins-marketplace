---
type: CTX
id: "<PRODUCT>-CTX-<NNN>"
title: "Context Map — <Alcance>"
description: "<Una frase: qué relaciones entre contextos describe este mapa>"
version: "0.1.0"
status: draft
owner: "team:<responsable>"
classification: internal
product: "<PRODUCT>"
pack: ddd-domain-design
skill: ddd-context-map-designer
tags: [ddd, context-map]
generated:
  by: "ddd-context-map-designer/2.1.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "<SRC-ID>"
    resource: "<RUTA-O-URI-REAL>"
    title: "<título de la fuente>"
related: []
---
# Context Map — <Alcance>

> Plantilla. Sustituir todos los marcadores `<...>` con evidencia real. Los patrones son propuestas hasta su decisión humana.

## Contextos participantes
<Enlaces a los BC del mapa, cada uno con su tipo: interno o externo.>

## Relaciones
Para cada relación:
- **Par:** <contexto A> ↔ <contexto B>.
- **Dirección:** upstream y downstream.
- **Patrón propuesto:** <Published Language, ACL, Customer/Supplier, Conformist, Shared Kernel, OHS u otro>.
- **Alternativas y trade-offs:** <al menos dos cuando la decisión no esté tomada>.
- **Estado:** <propuesta, decidida con fecha y actor declarado>.

## Sistemas externos
<Sistemas fuera del alcance y cómo se encapsulan.>

## Riesgos y decisiones pendientes
<Riesgos por relación y decisiones humanas abiertas.>

## Trazabilidad
<Fuentes por ID, bounded contexts de origen y decisiones de frontera.>
