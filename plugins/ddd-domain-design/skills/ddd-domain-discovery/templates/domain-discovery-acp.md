---
type: ACP
id: "<PRODUCT>-ACP-<NNN>"
title: "Descubrimiento de dominios — <Alcance>"
description: "<Una frase: dominios y subdominios identificados para el alcance, con evidencia y vacíos>"
version: "0.1.0"
status: draft
owner: "team:<responsable>"
classification: internal
product: "<PRODUCT>"
pack: ddd-domain-design
skill: ddd-domain-discovery
tags: [ddd, domain-discovery]
generated:
  by: "ddd-domain-discovery/2.1.1"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "<SRC-ID>"
    resource: "<RUTA-O-URI-REAL>"
    title: "<título de la fuente>"
related: []
---
# Descubrimiento de dominios — <Alcance>

> Plantilla. Sustituir todos los marcadores `<...>` con evidencia real. Run: `<run-id>`. Alcance: `<DSP-ID>`. No aprueba ningún gate; requiere revisión humana.

## 1. Fuentes y procedencia
| ID | Fuente | Estado de aprobación | Uso |
|---|---|---|---|
| <S1> | <ruta o URI> | <estado, declarado o verificado> | <uso> |

Las aprobaciones son declaraciones, no verificaciones. Declarar los artefactos ausentes (ASIS, ASR, ADR, SSP) y no usarlos.

## 2. Lenguaje ubicuo
- **<término>:** <definición> (<TRM-ID>).

## 3. Dominios y subdominios
Cada candidato cita su fuente. Todo lo que no tiene fuente se marca como hipótesis.

### D<n> · <Nombre>
- **Qué hace:** <descripción>.
- **Fuentes:** <IDs>.
- **Hechos:** <lo verificado en las fuentes>.
- **Inferencias:** <lo deducido, marcado como tal>.

## 4. Clasificación propuesta (no decidida)
Core, Supporting o Generic, con el criterio de inferencia. Requiere decisión humana.

## 5. Contradicciones y vacíos
- **V<n>:** <vacío>, con los dominios afectados.

## 6. Preguntas abiertas para revisión humana
1. <pregunta>.

## 7. Trazabilidad hacia el siguiente paso
<Qué debe decidir el siguiente documento: bounded contexts, context map o modelo táctico.>
