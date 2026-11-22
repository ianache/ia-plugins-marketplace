---
type: IMD
id: "IMD-NNN"
title: "Modelo de información conceptual de <producto o dominio>"
description: "<Qué dominio cubre el modelo y para qué sirve, en una frase>"
version: "0.1.0"
status: draft
owner: "<team:responsable>"
classification: internal
tags: [business, imd]
product: "<PRODUCTO>"
pack: business-knowledge
skill: biz-information-model-designer
generated:
  by: "biz-information-model-designer/1.0.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "<ID-FUENTE>"
    resource: "<RUTA-O-URI-REAL>"
    title: "<TÍTULO-DE-LA-FUENTE>"
related: []
---

# IMD-NNN — Modelo de información conceptual de <producto o dominio>

> **Qué es y qué no es:** es un modelo **conceptual**. Muestra qué conceptos de negocio existen y cómo se relacionan. **No** es un modelo de datos: no define tablas, atributos técnicos, identificadores ni persistencia (eso corresponde a `data-modeling-database-design`).
>
> **Procedencia:** <fuentes y su estado>. En los diagramas, las relaciones marcadas **(inf.)** son inferencias. El detalle de cada relación está en la sección 5.

## 1. Vista general

<Bloques de conceptos, en lenguaje de negocio, y la idea que los une.>

## 2. Diagrama — <bloque u horizonte>

```mermaid
erDiagram
    CONCEPTO_A ||--o{ CONCEPTO_B : "verbo de negocio"
    CONCEPTO_B }o--|| CONCEPTO_C : "verbo de negocio (inf.)"
```

**Conceptos derivados** (se calculan, no se registran):
- <Concepto derivado: cómo se calcula, fuente>

## 3. Diagrama — <otro bloque u horizonte, si hace falta>

<Otro diagrama con la misma convención. Indica qué conceptos son externos y en qué sistema viven.>

## 4. Conceptos

| Concepto | Nombre en diagrama | Qué es | Bloque | Glosario | Fuente | Horizonte |
|---|---|---|---|---|---|---|
| <Término del glosario> | <CONCEPTO_A> | <una frase en lenguaje de negocio> | <bloque> | <enlace a TRM-NNNN, o "Sin término" + pregunta> | <archivo:Lnn o BR-…> | <H1…> |

En "Nombre en diagrama" van uno o más nombres separados por coma. Un concepto derivado lleva `— (derivado)`.

## 5. Relaciones

Clasificación: **FACT** (lo dice la fuente), **INFERENCE** (deducción razonada desde fuentes citadas), **UNKNOWN** (necesario pero sin respaldo) y **RETIRADA** (ya no aplica, con motivo).

| ID | Relación | Cardinalidad | Clasificación | Fuente | Pregunta |
|---|---|---|---|---|---|
| R-01 | <Un A tiene B> | <1 : N, N : M, 0..1 : 1, UNKNOWN> | <FACT / INFERENCE / UNKNOWN, con el motivo si no es FACT> | <archivo:Lnn o BR-…> | <ID de la pregunta o —> |

## 6. Reglas que actúan sobre el modelo

| Regla | Sobre qué concepto | Qué impone |
|---|---|---|
| <BR-…> | <concepto> | <restricción en lenguaje de negocio> |

## 7. Diagrama de Estados

Solo los conceptos con un ciclo de vida relevante para el negocio (el negocio decide o controla en qué estado está). Una subsección por concepto, titulada con el nombre del concepto. Si ningún concepto lo tiene, escribe "No aplica" y el motivo.

### <Nombre del concepto>

```mermaid
stateDiagram-v2
    [*] --> ESTADO_A : evento de alta
    ESTADO_A --> ESTADO_B : evento (inf.)
    ESTADO_B --> [*] : evento de cierre
```

**Estados**

| Estado | Nombre en diagrama | Descripción | Tipo | Fuente |
|---|---|---|---|---|
| <Estado en lenguaje de negocio> | <ESTADO_A> | <una frase: qué significa para el negocio> | <Inicial / Intermedio / Final> | <archivo:Lnn o BR-…> |

**Transiciones (reglas ECA: Evento – Condición – Acción)**

| ID | Origen | Destino | Evento | Condición (constraints) | Acción | Clasificación | Fuente | Pregunta |
|---|---|---|---|---|---|---|---|---|
| T-<CONCEPTO>-01 | <ESTADO_A o [*]> | <ESTADO_B o [*]> | <qué ocurre que dispara el cambio> | <qué debe cumplirse; cita BR-… o "ninguna"> | <qué efecto de negocio produce> | <FACT / INFERENCE / UNKNOWN, con el motivo si no es FACT> | <archivo:Lnn o BR-…> | <ID de la pregunta o —> |

## 8. Preguntas abiertas del modelo

| ID | Pregunta | Afecta a | Responsable | Prioridad |
|---|---|---|---|---|
| IM-Q1 | <pregunta concreta> | <R-NN, concepto o T-…> | <rol> | Alta / Media / Baja |

## 9. Historial de cambios del modelo

| Fecha | Cambio | Relaciones, conceptos o transiciones afectados | Fuente |
|---|---|---|---|
| <AAAA-MM-DD> | <alta, cambio o retiro> | <R-NN, concepto, T-…> | <fuente o decisión> |

## 10. Preparación y validación

- **Estado:** READY / CONDITIONAL / NOT READY para pasar a `data-modeling-database-design`
- **Motivo:** <inferencias sin validar y preguntas que bloquean>
- **Validación por bloque:**
  - [ ] <Bloque> — <responsable> — <preguntas que debe responder>
- **Inferencias a aceptar o rechazar:** <R-NN, …>
