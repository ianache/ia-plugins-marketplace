---
type: EPC
id: "RCP-NNN-EPC-NNN"   # RCP-NNN del RCP de origen; asignar con scripts/us_ids.py (numeración propia de épicas); global y no reutilizable
title: "Épica — <alcance>"
description: "<Resultado de negocio que entrega la épica, en una frase>"
version: "0.1.0"
status: draft
owner: "<team:responsable>"
classification: internal
tags: [requirements, epic, <producto>]
product: "<PRODUCTO>"   # opcional; código del producto en MAYÚSCULAS; metadato, no forma parte del ID
# legacy_id: "<ID-PREVIO>"   # solo si la épica ya tenía otro identificador
pack: requirements-engineering
skill: af-user-story-designer
generated:
  by: "af-user-story-designer/<version>"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "RCP-NNN"
    resource: "<RUTA-O-URI-REAL-DEL-RCP>"
    title: "<TÍTULO-DEL-RCP>"
related: ["RCP-NNN-US-NNN"]   # IDs de las historias que agrupa; una US pertenece como máximo a una épica
---

# Épica — <alcance>

## Objetivo de la épica
<Resultado de negocio observable que entrega el conjunto de historias. Referenciar BR o KPI del RCP; no inventar métricas.>

## Criterio de agrupación
<Por qué estas historias van juntas: actor, flujo, entidad o regla compartida. Sin este criterio la épica no es válida.>

## Historias incluidas
| ID | Título | Actor | Rol en la épica | Preparación (DoR) |
| :--- | :--- | :--- | :--- | :--- |

## Historias candidatas o excluidas
| ID | Motivo |
| :--- | :--- |

## Reglas de negocio de referencia
<IDs de BR del RCP que aplican a la épica, sin redefinirlas.>

## Orden sugerido y dependencias
<Orden interno sugerido, dependencias entre historias y dependencias externas. No asignar Sprint: eso lo hace el SSP.>

## Criterios de aceptación de la épica
<Comportamiento de extremo a extremo en Given/When/Then. Cada criterio se traza a al menos un criterio de las historias incluidas.>

| ID | Criterio (Given/When/Then) | Historias que lo cubren |
| :--- | :--- | :--- |

## Riesgos y preguntas abiertas
| ID | Pregunta o riesgo | Responsable | Prioridad |
| :--- | :--- | :--- | :--- |

## Definición de terminado de la épica
<Condiciones de terminado: historias incluidas en estado terminado y evidencia de extremo a extremo de sus criterios.>

## Trazabilidad
<RCP de origen, historias, BR y evidencia que respaldan la épica.>

## Historial
| Fecha | Cambio |
| :--- | :--- |
