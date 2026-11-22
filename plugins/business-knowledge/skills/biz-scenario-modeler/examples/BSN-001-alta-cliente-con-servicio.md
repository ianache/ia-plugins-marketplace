---
type: BSN
id: "BSN-001"
title: "Escenario de negocio — alta de cliente con servicio activo"
description: "Recorrido de un operador que registra un cliente, le asigna un servicio vigente y deja su primera unidad lista para operar. Ejemplo ilustrativo con datos ficticios."
version: "0.1.0"
status: draft
owner: "team:ejemplo"
classification: internal
tags: [business, bsn, ejemplo]
product: "EJEMPLO"
pack: business-knowledge
skill: biz-scenario-modeler
generated:
  by: "biz-scenario-modeler/1.0.0"
  at: "2026-11-07T10:00:00-05:00"
sources:
  - id: EJ-1
    resource: "ejemplo-ilustrativo"
    title: "Caso ficticio para ilustrar el contrato BSN"
related:
  - "BR-001"
  - "BR-002"
  - "BR-003"
  - "TRM-001"
  - "BCAP-001"
  - "BO-001"
---
# Escenario de negocio — alta de cliente con servicio activo

## 1. Identificación
- **Actor principal:** STK-001 (operador del distribuidor).
- **Capacidad:** BCAP-001 (gestión de clientes y servicios).
- **Objetivo:** BO-001 (que cada cliente activo tenga al menos un servicio vigente).
- **Producto:** EJEMPLO.

## 2. Propósito y alcance
- **Disparador:** solicitud de alta de un cliente nuevo.
- **Inicio:** cliente no registrado.
- **Fin:** cliente registrado, con un servicio vigente y una unidad asignada.
- **Incluido:** registro del cliente, asignación del servicio y vigencia.
- **Excluido:** instalación física de dispositivos (otro escenario) y facturación.

## 3. Precondiciones
1. El distribuidor tiene al menos un servicio activo (BR-001).
2. El identificador tributario del cliente no existe en el distribuidor (BR-002).

## 4. Pasos del escenario
| Nº | Actor | Acción o evento | Regla (BR) | Resultado o estado siguiente | Excepción |
|---|---|---|---|---|---|
| 1 | STK-001 | Registra los datos del cliente | BR-002 | Cliente en estado Nuevo | EXC-01 |
| 2 | STK-001 | Asigna un servicio activo y su vigencia | BR-001 | Servicio vigente | — |
| 3 | STK-001 | Confirma el alta | BR-003 | Cliente activo | — |

## 5. Excepciones y alternativas
- **EXC-01:** identificador tributario duplicado. Regla BR-002. Resultado: el alta se rechaza y no se crea el cliente. Owner: PO del distribuidor.

## 6. Resultado y estados finales
- **Activo:** cuando se cumple BR-003 (servicio vigente y unidad asignada).
- **Rechazado:** cuando falla BR-002 (identificador duplicado).

## 7. Términos TRM
- TRM-001 (cliente).

## 8. Trazabilidad
Paso 1 → BR-002 → BCAP-001 → BO-001. Paso 2 → BR-001 → BCAP-001 → BO-001. Paso 3 → BR-003 → BO-001.

## 9. Clasificación de afirmaciones
| Afirmación | Clasificación | Fuente | Confianza |
|---|---|---|---|
| El distribuidor requiere un servicio activo para el alta | hecho | EJ-1 | alta |
| El identificador tributario es único por distribuidor | decisión | EJ-1 | media |
| La unidad se asigna en el mismo alta | supuesto | — | baja |

## 10. Preguntas abiertas
| ID | Pregunta | Owner | Bloquea |
|---|---|---|---|
| Q1 | ¿La unidad se asigna en el alta o en un escenario posterior? | PO del distribuidor | sí |

## 11. Readiness y aprobación
- **Readiness:** CONDITIONAL
- **Motivo:** la asignación de unidad en el alta es un supuesto pendiente de la pregunta Q1.
- **Aprobación humana:** pendiente. Este documento no está aprobado.
