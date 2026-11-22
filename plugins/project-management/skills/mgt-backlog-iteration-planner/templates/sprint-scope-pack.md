---
type: SSP
id: "SSP-NNN"
title: "SSP-NNN — <nombre del Sprint>"
description: "<Sprint Goal en una frase>"
version: "0.1.0"
status: draft
owner: "<team:responsable>"
classification: internal
tags: [management, ssp]
product: "<PRODUCTO>"
pack: project-management
skill: mgt-backlog-iteration-planner
dsp_id: "DSP-NNN"
user_stories: ["US-NNN"]   # historias del DSP incluidas en el Sprint; obligatorio
generated:
  by: "mgt-backlog-iteration-planner/1.0.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: "dsp-nnn"
    resource: requirements/scope-packs/DSP-NNN-<slug>.md
    title: "<TÍTULO-DEL-DSP>"
related: []
---

# SSP-NNN — <nombre del Sprint>

Un SSP organiza el trabajo de un Sprint a partir de un DSP aprobado; no amplía su alcance.

## Sprint Goal
<Resultado observable al cierre del Sprint; enlace al criterio de éxito CE-nn del acta.>

## Scope
**Incluye:** <historias del DSP que entran en el Sprint.>

**Excluye:** <todo lo excluido en el DSP y lo que se deja fuera del Sprint, con motivo.>

**Dependencias:**
| Dependencia | Cobertura en el Sprint |
|---|---|

**Riesgos:**
| ID | Riesgo | Respuesta |
|---|---|---|

## Priorización y Definition of Ready
**Criterio de priorización aplicado:** <criterios declarados, por ejemplo valor según los BO, riesgo, dependencia, esfuerzo si existe; no solo el orden resultante.>

| Historia | Prioridad | Justificación según el criterio | DoR | Qué falta para cumplir el DoR |
|---|---|---|---|---|
| <US-ID> | <1..n> | <por qué ocupa ese lugar> | cumple / no cumple | <criterios de aceptación, dependencias identificadas, pregunta abierta> |

Una historia que no cumple el DoR no entra al Sprint: queda en Excluye con ese motivo.

## User Stories
Todas pertenecen al DSP de origen; ninguna excede su alcance.

| Historia | Issue | Título | Plataforma | Criterios | Prueba | Estimación (ref.) |
|---|---|---|---|---|---|---|
| <US-ID> | <enlace Issue GitLab o "por crear"> | <título> | <plataforma> | AC-1 a AC-n | <completa / parcial> | <dato entregado por la persona; si no existe, "Por definir"> |

Orden sugerido (DSP): <US-ID → US-ID>.

## Referencia de esfuerzo y costo
Estimación de **referencia** según `references/estimation-practice.md` (no es un compromiso). Salida de `scripts/estimate.py`; coeficientes: <versión y estado, p. ej. «3: aprobados por el PO; QA y agente sin calibrar»>.

| Historia | AC | Factores | Desarrollo h (humano) | Talla | Confianza | TC manual / automatizado | QA h (humano) | Total humano h | Agente h |
|---|---|---|---|---|---|---|---|---|---|
| <US-ID> | <n> | <E,S,V,F,D + Q> | <h> | S / M / L / XL | Alta / Media / Baja | <n / n> | <h> | <h> | <h> |

| Concepto | Valor | Base |
|---|---|---|
| `/time` (humano) | <h> | suma de horas humanas, desarrollo con Superpowers más QA |
| `/cost` (humano) | S/ <monto> | `/time` × tarifa S/ 30.00 por hora |
| `/time_agent` | <h> | horas de trabajo del agente de IA |
| `/cost_agent` | S/ <monto> (USD <monto>) | suscripción USD 25.00 al mes × puestos × días hábiles del Sprint / días hábiles del mes; tipo de cambio: <valor o PENDIENTE> |

**Avisos de la estimación:** <talla L/XL, historias sin TC, coeficientes sin calibrar, tipo de cambio pendiente>.

## Compromiso del Sprint
<Capacidad y compromiso tal como los da la persona responsable; si no existen, "Por definir". No estimar.>

## Criterios de cierre del Sprint
<Cómo se sabe que el Sprint terminó: historias en estado final acordado, pruebas ejecutadas, issues cerrados o reasignados, Milestone cerrado por una persona. Debe poder verificarse en GitLab; no autoevaluar.>

## Trazabilidad
- DSP: `DSP-NNN` (<ruta o enlace>)
- SSP: <ruta o enlace>
- Project ID / Project Issue: <id> / <enlace>
- Milestone: <id, iid y URL>

## Descripción del Milestone
Lo que se publica como descripción del Milestone sale del **primer bloque de código** de esta sección: `gitlab_milestone.py` lee sus comandos y los vuelca en `templates/milestone-description.md` (skill `mgt-work-publisher-synchronizer`). La descripción publicada contiene solo esos comandos, en este orden; el Sprint Goal, las historias y los enlaces viven en este SSP y no se envían. Reemplazar los valores de ejemplo; lo que ninguna persona informó se deja `PENDIENTE`, nunca se inventa. `/subproject` es el título del Milestone y no puede quedar `PENDIENTE`. `/project_end` es opcional (AAAA-MM-DD).

```text
/project PENDIENTE
/subproject PENDIENTE
/cost PENDIENTE
/time PENDIENTE
/client PENDIENTE
/group PENDIENTE
/cost_agent PENDIENTE
/time_agent PENDIENTE
```

El script rechaza una cabecera incompleta o fuera de orden y un `/subproject` pendiente.

# Sprint GitLab Control Pack

| Elemento | Estado |
|---|---|
| Milestone | <existe / por crear> |
| Mutaciones propuestas | <M-n: qué cambia, aprobada por quién, ejecutada o no> |
| Validación de la URL del SSP | <resuelve / no resuelve> |
| Issues de las historias | <creadas / por crear> |

## Preguntas abiertas
| ID | Pregunta | Responsable | Prioridad |
|---|---|---|---|

## Preparación y aprobación
- **Estado:** READY / CONDITIONAL / NOT_READY
- **Alcance y compromiso aprobados por:** <human:nombre — fecha> (no autoaprobar)

## Historial
| Fecha | Cambio |
|---|---|
