---
type: C4
id: "<<SERVICE_ID>>-C4-001"
title: "Arquitectura C4 — <<SERVICE_ID>>"
description: "<<Una frase: qué niveles C4 documenta este archivo y para qué código>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, c4, architecture]
product: "<<PRODUCTO>>"
service_id: "<<SERVICE_ID>>"
pack: microservice-api-design
skill: c4-product-component-documenter
generated:
  by: "c4-product-component-documenter/<<VERSION>>"
  at: "<<ISO-8601-CON-ZONA>>"
sources:
  - id: "<<ID-FUENTE>>"
    resource: "<<RUTA-O-URI-REAL>>"
    title: "<<TÍTULO-DE-LA-FUENTE>>"
related:
  - "<<SVC-ID>>"
---
# Arquitectura C4 — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `C4`. Reemplazar todos los marcadores `<<...>>`. Este archivo vive en `codebase/<<servicio>>/docs/`.

## 1. Contexto (C1)
Obligatorio. Sistema, actores y sistemas externos, con su relación y protocolo.

## 2. Contenedores (C2)
Obligatorio. Contenedores desplegables (servicios, bases de datos, colas), con tecnología y responsabilidad.

## 3. Componentes (C3)
Obligatorio. Componentes de cada contenedor, con su responsabilidad y su puerto.

## 4. Código (C4)
Obligatorio. Referencia a rutas reales del repositorio (`codebase/<<servicio>>/...`). No incluir diagramas de clases sin ruta.

## 5. Escenarios de secuencia
Obligatorio. Al menos un flujo end-to-end, con cada paso y su componente.

## 6. Fuentes y trazabilidad
Obligatorio. Fuentes de cada elemento del diagrama (ASIS, SVC, código) con su ID.

## Reglas de validación
- Frontmatter con `type: C4` y `service_id`.
- Cada ruta de la sección 4 existe en `codebase/<<servicio>>/`.
- `related` enlazado en el cuerpo con enlace Markdown.
