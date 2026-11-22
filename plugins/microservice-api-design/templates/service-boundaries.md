---
type: SVC
id: "<<SERVICE_ID>>-SVC-001"
title: "Límites del servicio — <<SERVICE_ID>>"
description: "<<Una frase: responsabilidad principal y límite del servicio>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, to-be, boundaries]
product: "<<PRODUCTO>>"
service_id: "<<SERVICE_ID>>"
pack: microservice-api-design
skill: microservice-boundary-architecture-designer
generated:
  by: "microservice-boundary-architecture-designer/<<VERSION>>"
  at: "<<ISO-8601-CON-ZONA>>"
sources:
  - id: "<<ID-FUENTE>>"
    resource: "<<RUTA-O-URI-REAL>>"
    title: "<<TÍTULO-DE-LA-FUENTE>>"
related:
  - "<<BC-ID>>"
---
# Límites del servicio — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `SVC` (límites). Reemplazar todos los marcadores `<<...>>`.

## 1. Responsabilidades
Obligatorio. Lista de responsabilidades. Cada una cita su fuente (BC/CTX o historia).

## 2. Límites
Obligatorio. Bounded context al que pertenece (`related`, enlazado), agregados que contiene y lo que NO contiene, con el servicio que sí lo contiene.

## 3. Ownership
Obligatorio. Equipo responsable de cada responsabilidad. Sin responsable no se entrega el documento.

## 4. Dependencias
Obligatorio. Dependencias sincrónicas y asíncronas con el servicio del otro lado y su contrato (API o EVT).

## 5. Trazabilidad
Obligatorio. Enlaces a BC/CTX y ADR. Un ADR no citado aquí no aplica a este servicio.

## 6. NFR asociados
Obligatorio. Requisitos no funcionales con medida y fuente. Sin medida, el NFR va a preguntas abiertas.

## 7. Preguntas abiertas
Obligatorio. Cada pregunta con responsable.

## Reglas de validación
- Frontmatter con `type: SVC` y `service_id`.
- `related` enlazado en el cuerpo con enlace Markdown.
- Cada responsabilidad tiene fuente.
