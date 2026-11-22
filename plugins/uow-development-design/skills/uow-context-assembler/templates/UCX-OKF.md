---
type: UCX
title: "UOW Context Pack"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-UCX-001
version: "1.0.0"
status: draft
owner: team:engineering
classification: internal
tags: [uow, ucx]
product: <PRODUCTO>
pack: uow-development-design
skill: uow-context-assembler
generated:
  by: uow-context-assembler/1.1.0
  at: "<ISO-8601 con zona>"
sources:
  - id: us
    resource: "<ruta o URI de la US>"
    version: "<versión>"
    title: "<US-ID>@<versión>"
us_ref: US-XXX
mode: GREENFIELD   # GREENFIELD | BROWNFIELD | EVOLUTION
baseline: {ref: null, commit: null}   # obligatorio en BROWNFIELD y EVOLUTION
acceptance_criteria: [AC-1]   # criterios de la US
---
# UCX-XXX — <título>
## Alcance y modo
## Insumos
| ID | Tipo | Versión | Ruta | Estado |
|---|---|---|---|---|
| <ID> | <US/FDT/API/LDM/...> | <versión> | <ruta> | <aprobado/borrador> |
## Hechos
<!-- Solo lo evidenciado, cada hecho con su fuente y versión. -->
| ID | Hecho | Fuente |
|---|---|---|
| F-01 | <hecho> | <ID@versión> |
## Inferencias
<!-- Deducciones marcadas como tales, con su base. -->
## Supuestos
<!-- Lo que se asume sin evidencia; cada uno con quién lo valida. -->
## Desconocidos y preguntas abiertas
<!-- Tabla ID, pregunta, responsable, prioridad. Si no hay, escribir Ninguno. -->
## Conflictos entre fuentes
## Línea base
## Provenance
