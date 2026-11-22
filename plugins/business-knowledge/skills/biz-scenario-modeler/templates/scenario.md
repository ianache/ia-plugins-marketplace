---
type: BSN
id: "BSN-NNN"
title: "Escenario de negocio — <nombre corto>"
description: "<Qué recorrido de negocio describe el escenario, en una frase verificable>"
version: "0.1.0"
status: draft
owner: "<team:responsable>"
classification: internal
tags: [business, bsn]
product: "<PRODUCTO>"
pack: business-knowledge
skill: biz-scenario-modeler
generated:
  by: "biz-scenario-modeler/1.0.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "<ID-FUENTE>"
    resource: "<RUTA-O-URI-REAL>"
    title: "<TÍTULO-DE-LA-FUENTE>"
related:
  - "<BR-NNN>"
  - "<TRM-NNN>"
  - "<BCAP-NNN>"
  - "<BO-NNN>"
---

# Escenario de negocio — <nombre corto>

## 1. Identificación
Indicar: actor principal (`STK-NNN`), capacidad (`BCAP-NNN`), objetivo (`BO-NNN`) y producto. Si un dato no existe en `business/`, escribir `[PENDIENTE: <responsable>]`.

## 2. Propósito y alcance
- **Disparador:** <evento o solicitud que inicia el escenario>.
- **Inicio:** <estado o situación desde la que parte>.
- **Fin:** <estado o situación en la que termina>.
- **Incluido:** <qué recorrido cubre>.
- **Excluido:** <qué queda fuera y en qué otro escenario o documento vive>.

## 3. Precondiciones
Lista numerada. Cada precondición indica la regla que la sustenta, con su ID (`BR-NNN`), o se marca como supuesto en la sección 9.

## 4. Pasos del escenario
Tabla. Una fila por paso, en orden.

| Nº | Actor | Acción o evento | Regla (BR) | Resultado o estado siguiente | Excepción |
|---|---|---|---|---|---|
| 1 | <STK-NNN o rol> | <acción> | <BR-NNN> | <estado> | <EXC-NN o —> |

Cada fila tiene al menos una `BR-NNN` existente en `business/rules/`.

## 5. Excepciones y alternativas
Una entrada por excepción: condición, regla (`BR-NNN`), resultado y owner. Identificador `EXC-NN`.

## 6. Resultado y estados finales
Estados finales posibles del escenario y la condición que lleva a cada uno. Referenciar los estados de las reglas por `BR-NNN`.

## 7. Términos TRM
Lista de términos usados en el escenario, con su `TRM-NNN`. Un término sin entrada en `business/terms/` se marca `[PENDIENTE: glosario]`.

## 8. Trazabilidad
Matriz: paso → BR → TRM → BCAP → BO. Señalar huecos: reglas sin uso en ningún escenario, o pasos sin regla.

## 9. Clasificación de afirmaciones
Tabla con cada afirmación relevante, su clasificación (hecho, inferencia, supuesto, hipótesis, decisión o vacío), su fuente y su confianza.

## 10. Preguntas abiertas
| ID | Pregunta | Owner | Bloquea (sí/no) |
|---|---|---|---|

## 11. Readiness y aprobación
- **Readiness:** <READY | CONDITIONAL | NOT_READY>
- **Motivo:** <una frase>
- **Aprobación humana:** pendiente. Este documento no está aprobado.
