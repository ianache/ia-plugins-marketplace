---
type: BIC
title: "BI Decision Context — <alcance analítico>"
description: "<una frase: decisiones y audiencias que cubre este contexto>"
id: BI-BIC-000
version: "1.0.0"
status: draft
classification: internal
owner: "<team:rol o human:nombre>"
product: "<producto o iniciativa>"
pack: bi-analytics
skill: bi-decision-context-analyst
tags: [bi, analytics, bic]
generated:
  by: bi-decision-context-analyst/1.0.0
  at: "<ISO 8601 con zona>"
sources:
  - id: src-001
    resource: "<URI o ruta de la fuente>"
    title: "<título de la fuente>"
related: []
---
# BI Decision Context — <alcance analítico>

> **Definición:** fija las preguntas de negocio, las decisiones que soportan, las audiencias y el alcance analítico de una iniciativa, antes de definir KPI o datos.
> **Alcance del documento:** una iniciativa o producto por documento.

## 1. Propósito
> Qué decisiones habilita este contexto y para qué iniciativa. Una a tres frases.
> **Contenido mínimo:** objetivo de negocio y decisión principal que el análisis debe servir.

## 2. Alcance
> Dominios, procesos, unidades y periodos incluidos y excluidos.
> **Contenido mínimo:** una tabla con al menos una fila incluida y, si aplica, una excluida, cada una con su motivo.

| Incluido | Excluido | Motivo |
|---|---|---|
| | | |

## 3. Insumos y evidencias
> Fuentes consultadas (entrevistas, actas, reportes actuales). Los IDs deben coincidir con `sources` del frontmatter.
> **Contenido mínimo:** cada fuente con su ID, tipo y fecha de consulta.

| ID | Fuente | Tipo | Fecha de consulta |
|---|---|---|---|
| src-001 | | | |

## 4. Desarrollo

### 4.1 Decisiones de negocio
> **Definición:** cada decisión que el análisis debe soportar.
> **Contenido mínimo por fila:** pregunta que responde, decisor, frecuencia, horizonte temporal, acción que dispara y fuente. Sin acción disparada, la decisión no es válida.

| ID | Decisión / pregunta de negocio | Decisor | Frecuencia | Horizonte | Acción disparada | Fuente |
|---|---|---|---|---|---|---|
| D-01 | | | | | | src-001 |

### 4.2 Audiencias
> **Definición:** personas o roles que consumen el análisis y las decisiones que atienden.
> **Contenido mínimo:** clasificación (ejecutiva, táctica u operativa), nivel de detalle requerido y al menos una decisión (ID de 4.1) por audiencia.

| Audiencia | Rol | Clasificación | Nivel de detalle | Decisiones (IDs) |
|---|---|---|---|---|
| | | | | |

### 4.3 Hechos, supuestos y vacíos
> **Definición:** clasificación de cada afirmación del documento. Un vacío se formula como pregunta abierta, no como respuesta.
> **Contenido mínimo:** tipo (hecho, inferencia, supuesto o vacío), descripción, pregunta abierta cuando el tipo sea vacío y fuente.

| ID | Tipo | Descripción | Pregunta abierta | Fuente |
|---|---|---|---|---|
| H-01 | hecho | | | src-001 |

### 4.4 Diagrama (opcional)
> **Definición:** mapa de decisiones y audiencias, solo si aclara la relación entre ellas.
> **Contenido mínimo:** bloque Mermaid que renderiza sin errores, o «No aplica» con motivo.

## 5. Decisiones humanas pendientes
> **Definición:** decisiones que solo una persona autorizada puede tomar antes de aprobar el gate G1.
> **Contenido mínimo:** descripción, responsable y referencia al vacío que la origina.

## 6. Relaciones
> **Definición:** documentos relacionados, con enlace Markdown y su ID.
> **Contenido mínimo:** entradas de `business-knowledge` usadas (TRM, BR, IMD) y otros documentos BI-* relacionados. Si no hay, «Ninguna».

## 7. Limitaciones y pendientes
> **Definición:** qué no cubre el documento y qué falta para aprobarlo.
> **Contenido mínimo:** lista de limitaciones y de pendientes con responsable.

## 8. Validación
- [ ] Frontmatter OKF y perfil COMSATEL válidos
- [ ] Cada decisión tiene acción disparada y fuente
- [ ] Cada audiencia está enlazada a al menos una decisión
- [ ] Cada vacío tiene pregunta abierta
- [ ] Enlaces relativos válidos
