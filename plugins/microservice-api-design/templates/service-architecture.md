---
type: SVC
id: "<<SERVICE_ID>>-SVC-002"
title: "Arquitectura del servicio — <<SERVICE_ID>>"
description: "<<Una frase: arquitectura hexagonal To-Be del servicio>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, to-be, architecture]
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
  - "<<ADR-ID>>"
---
# Arquitectura del servicio — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `SVC` (arquitectura). Reemplazar todos los marcadores `<<...>>`.

## 1. Núcleo y puertos
Obligatorio. Núcleo de dominio, puertos de entrada y puertos de salida, con su nombre y su contrato.

## 2. Adaptadores
Obligatorio. Adaptador por puerto: tecnología, protocolo y ADR que lo justifica.

## 3. Dependencias externas
Obligatorio. Sistemas externos, su tipo de acoplamiento y su contrato.

## 4. Vista C4
Obligatorio. Enlace a `docs/c4-architecture.md` del servicio en `codebase/<<servicio>>/`.

## 5. NFR
Obligatorio. Requisitos no funcionales con medida y fuente.

## 6. Trazabilidad
Obligatorio. Enlaces a ADR, límites (`service-boundaries.md`) y APIs o eventos que expone.

## Reglas de validación
- Frontmatter con `type: SVC` y `service_id`.
- Cada puerto de salida tiene adaptador declarado.
- `related` enlazado en el cuerpo con enlace Markdown.
