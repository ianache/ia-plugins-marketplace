---
type: UAP
title: "UOW Agent Execution Plan"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-UAP-001
version: "1.0.0"
status: draft
owner: team:engineering
classification: internal
tags: [uow, uap]
product: <PRODUCTO>
pack: uow-development-design
skill: uow-agent-execution-planner
generated:
  by: uow-agent-execution-planner/1.1.0
  at: "<ISO-8601 con zona>"
sources:
  - id: us
    resource: "<ruta o URI de la US>"
    version: "<versión>"
    title: "<US-ID>@<versión>"
uow_ref: UOW-001
authored_by: [<persona o agente>]
profile: neutral   # neutral | claude-code-superpowers
steps: []   # [{id, kind: test|impl|migration|docs, goal, files, test_first, verify, expected}]
stop_conditions: []
deviation_protocol: {escalate_to: <persona>, record_in: <ruta o issue>}
definition_of_done: []   # [{id, check, verify}]
---
# UAP-XXX — <título>
## Perfil de ejecución
## Preparación del entorno
## Pasos
<!-- Tabla de pasos con archivos, prueba primero, verificación y resultado esperado. -->
| STEP | Tipo | Objetivo | Archivos | Prueba primero | Verificación | Resultado esperado |
|---|---|---|---|---|---|---|
| S-01 | test | <objetivo> | <ruta permitida> | sí | <comando> | <resultado> |
## Verificación y criterios de terminado
## Condiciones de parada
## Protocolo de desviaciones
## Guardrails
## Entrega
