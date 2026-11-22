---
type: IMP
id: "<<SERVICE_ID>>-IMP-001"
title: "Análisis de impacto — <<SERVICE_ID>>"
description: "<<Una frase: qué cambio evoluciona el servicio y su impacto>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, evolution, impact]
product: "<<PRODUCTO>>"
service_id: "<<SERVICE_ID>>"
pack: microservice-api-design
skill: microservice-evolution-planner
generated:
  by: "microservice-evolution-planner/<<VERSION>>"
  at: "<<ISO-8601-CON-ZONA>>"
sources:
  - id: "<<ID-FUENTE>>"
    resource: "<<RUTA-O-URI-REAL>>"
    title: "<<TÍTULO-DE-LA-FUENTE>>"
related:
  - "<<ASIS-ID>>"
  - "<<SVC-ID>>"
---
# Análisis de impacto — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `IMP`. Reemplazar todos los marcadores `<<...>>`. Parte de la diferencia entre As-Is (`ASIS`) y To-Be (`SVC`).

## 1. Cambios propuestos
Obligatorio. Tabla: cambio | As-Is | To-Be | origen (ASIS/SVC).

## 2. Compatibilidad
Obligatorio. Cambios incompatibles de API o de eventos, versión afectada y si hay versión anterior mantenida.

## 3. Consumidores
Obligatorio. Consumidores afectados por cada cambio, con su contrato y su responsable. Sin consumidor identificado, se declara como pregunta abierta.

## 4. Migración
Obligatorio. Pasos ordenados, datos afectados y verificación de cada paso.

## 5. Rollout
Obligatorio. Fases, criterio de paso a la siguiente fase y ventana de cambio.

## 6. Rollback
Obligatorio. Condiciones que disparan el rollback y pasos exactos para revertir, incluido el estado de los datos.

## 7. Riesgos
Obligatorio. Tabla: riesgo | probabilidad | impacto | mitigación | responsable.

## Reglas de validación
- Frontmatter con `type: IMP` y `service_id`.
- Todo cambio incompatible tiene consumidor y rollback.
- `related` enlazado en el cuerpo con enlace Markdown.
