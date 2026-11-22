---
type: CHG
id: "CHG-NNN"
title: "Solicitud de cambio — <resumen>"
description: "<Qué cambia y por qué, en una frase>"
version: "0.1.0"
status: draft
owner: "<team:responsable>"
classification: internal
tags: [management, chg]
product: "<PRODUCTO>"
pack: project-management
skill: mgt-risk-change-controller
generated:
  by: "mgt-risk-change-controller/1.0.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "<ID-FUENTE>"
    resource: "<RUTA-O-URI-REAL>"
    title: "<TÍTULO-DE-LA-FUENTE>"
related: []
change_state: proposed   # proposed | approved | rejected | deferred (estado de la decisión; `status` sigue el perfil: draft | stable | deprecated)
approved_by: null        # obligatorio ("human:<nombre>") cuando change_state sea approved
---

# Solicitud de cambio — <resumen>

## 1. Descripción y motivo
<Qué se pide cambiar y qué lo origina.>

## 2. Impacto
| Dimensión | Impacto | Fuente |
|---|---|---|
| Alcance | | |
| Plazo | | |
| Calidad | | |
| Riesgos | <enlaces a RSK> | |
| Requisitos / arquitectura | <enlace a IMP / ADR si existe> | |

## 3. Alternativas
| Alternativa | Pros | Contras |
|---|---|---|

## 4. Decisión
- **Estado:** proposed | approved | rejected | deferred (se refleja en `change_state` del frontmatter; nunca en `status`)
- **Decidido por:** <human:nombre — fecha> (debe coincidir con `approved_by`; mientras no exista, el estado es `proposed`)
- **Motivo:** <registrar al decidir>

## 5. Preguntas abiertas
| ID | Pregunta | Responsable | Prioridad |
|---|---|---|---|
