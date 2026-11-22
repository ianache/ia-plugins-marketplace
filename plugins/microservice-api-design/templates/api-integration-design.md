---
type: API
id: "<<SERVICE_ID>>-API-001"
title: "Diseño de integración de API — <<SERVICE_ID>>"
description: "<<Una frase: operaciones que expone o consume el servicio>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, api, integration]
product: "<<PRODUCTO>>"
service_id: "<<SERVICE_ID>>"
pack: microservice-api-design
skill: api-integration-contract-designer
generated:
  by: "api-integration-contract-designer/<<VERSION>>"
  at: "<<ISO-8601-CON-ZONA>>"
sources:
  - id: "<<ID-FUENTE>>"
    resource: "<<RUTA-O-URI-REAL>>"
    title: "<<TÍTULO-DE-LA-FUENTE>>"
related:
  - "<<SVC-ID>>"
---
# Diseño de integración de API — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `API`. Reemplazar todos los marcadores `<<...>>`. El contrato OpenAPI vive en `codebase/<<servicio>>/src/main/resources/api.yaml`; este documento describe las operaciones y su integración.

## 1. Propósito y alcance
Obligatorio. Qué operaciones se diseñan y para qué consumidores.

## 2. Operaciones
Obligatorio. Tabla: `operationId` | método | ruta | propósito | autenticación | versión.
Cada `operationId` debe existir en el OpenAPI de la sección 7.

## 3. Modelo de errores
Obligatorio. Códigos HTTP usados, formato del cuerpo de error y el significado de cada código.

## 4. Seguridad y autenticación
Obligatorio. Mecanismo de autenticación, autorización por operación y datos sensibles que no se devuelven.

## 5. Versionado y compatibilidad
Obligatorio. Política de versiones, cambios compatibles e incompatibles y fecha de retiro de cada versión.

## 6. Consumidores y proveedores
Obligatorio. Servicios que llaman a este servicio y servicios a los que llama, con su contrato.

## 7. Contrato OpenAPI
Obligatorio. Ruta del archivo `api.yaml`, versión de OpenAPI y resultado de la validación del archivo.

## 8. Trazabilidad
Obligatorio. Enlaces a SVC, ADR y historias que originan cada operación.

## 9. Preguntas abiertas
Obligatorio. Cada pregunta con responsable.

## Reglas de validación
- Frontmatter con `type: API` y `service_id`.
- Cada `operationId` de la sección 2 existe en el OpenAPI.
- `related` enlazado en el cuerpo con enlace Markdown.
