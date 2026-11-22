---
type: ASIS
id: "<<SERVICE_ID>>-ASIS-001"
title: "As-Is — <<SERVICE_ID>>"
description: "<<Una frase verificable: qué servicio se reconstruye, desde qué commit>>"
version: "0.1.0"
status: draft
owner: "team:<<RESPONSABLE>>"
classification: internal
tags: [microservices, as-is]
product: "<<PRODUCTO>>"
service_id: "<<SERVICE_ID>>"
pack: microservice-api-design
skill: microservice-reconstruction-analyzer
generated:
  by: "microservice-reconstruction-analyzer/<<VERSION>>"
  at: "<<ISO-8601-CON-ZONA>>"
sources:
  - id: "<<ID-FUENTE>>"
    resource: "<<RUTA-O-URI-REAL>>"
    title: "<<TÍTULO-DE-LA-FUENTE>>"
related: []
---
# As-Is — <<SERVICE_ID>>

> PLANTILLA. Contrato del tipo `ASIS`. Reemplazar todos los marcadores `<<...>>` con evidencia real. Un marcador sin reemplazar invalida el documento.

## 1. Alcance
Obligatorio. Qué parte del servicio se reconstruye, qué queda fuera y por qué.

## 2. Evidencia (archivo y commit)
Obligatorio. Tabla. Cada fila es una fuente verificable.

| ID | Archivo | Commit | Fragmento o línea | Tipo (hecho / inferencia) |
|---|---|---|---|---|
| E-01 | <<ruta en el repositorio>> | <<sha completo>> | <<líneas>> | hecho |

Regla: todo hecho cita al menos una fila de esta tabla. Sin commit no hay evidencia.

## 3. Componentes
Obligatorio. Un componente por fila: nombre, responsabilidad observada, evidencia (ID de la sección 2).

## 4. Dependencias
Obligatorio. Dependencias entrantes y salientes, con protocolo (HTTP, evento, base de datos) y evidencia.

## 5. Hechos
Obligatorio. Afirmaciones verificadas, cada una con su ID de evidencia.

## 6. Inferencias
Obligatorio si aplica. Afirmaciones no observadas directamente. Cada una declara su razonamiento y su evidencia de apoyo.

## 7. Incertidumbres y preguntas
Obligatorio. Lo que no se pudo verificar. Cada pregunta indica responsable.

## Reglas de validación
- Frontmatter con `type: ASIS`, `service_id` y `pack`.
- Ninguna afirmación sin evidencia en la sección 2.
- `related` enlazado en el cuerpo con enlace Markdown.
