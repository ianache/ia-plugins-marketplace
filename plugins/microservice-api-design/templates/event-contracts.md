---
type: EVT
id: "<<SERVICE_ID>>-EVT-001"
title: "Contratos de eventos — <<SERVICE_ID>>"
description: "<<Una frase: eventos que publica o consume el servicio>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, events]
product: "<<PRODUCTO>>"
bounded_context_id: "<<BC-ID>>"
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
  - "<<BC-ID>>"
---
# Contratos de eventos — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `EVT`. Reemplazar todos los marcadores `<<...>>`. Los eventos del dominio se definen con su bounded context (`bounded_context_id`).

## 1. Propósito
Obligatorio. Qué hechos de negocio comunica el servicio.

## 2. Eventos
Obligatorio. Tabla: nombre | productor | consumidores | tópico | versión | clave de partición.

## 3. Esquema por evento
Obligatorio. Por evento: campos obligatorios y opcionales, tipo de cada campo y un ejemplo sin datos reales.

## 4. Entrega y garantías
Obligatorio. Semántica de entrega, orden garantizado (o no), idempotencia y cómo la implementa el consumidor.

## 5. Versionado del esquema
Obligatorio. Cambios compatibles e incompatibles, y la versión que los contiene.

## 6. Errores y reintentos
Obligatorio. Política de reintentos, cola de mensajes fallidos y responsable de su revisión.

## 7. Trazabilidad
Obligatorio. Enlaces a BC/AGG/VO del dominio y a las historias o FDT que originan cada evento.

## 8. Preguntas abiertas
Obligatorio. Cada pregunta con responsable.

## Reglas de validación
- Frontmatter con `type: EVT`, `bounded_context_id`, `service_id` y `pack`.
- Cada evento de la sección 2 tiene esquema en la sección 3.
- `related` enlazado en el cuerpo con enlace Markdown.
