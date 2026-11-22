---
name: bi-decision-context-analyst
description: Define preguntas de negocio, decisiones soportadas, audiencias y alcance analítico. Produce BIC.
---

# BI Decision Context Analyst

Rol: **specialist**. Ejecutar solo con autorización del orquestador.

## Activación
Tarea T-01 (gate G1). Produce el tipo **BIC** (BI Decision Context).

## Entradas
Autorización del orquestador, objetivo de negocio, fuentes autorizadas (entrevistas, actas, reportes actuales) y, si existen, TRM y BR de `business-knowledge`.

## Procedimiento
1. Declarar fuentes analizadas, alcance y audiencias.
2. Para cada decisión de negocio, registrar: pregunta que responde, decisor, frecuencia, horizonte temporal y acción que dispara.
3. Clasificar audiencias (ejecutiva, táctica, operativa) y su necesidad de detalle.
4. Delimitar alcance: dominios, procesos, unidades y periodos incluidos y excluidos.
5. Separar hechos, inferencias, supuestos y vacíos; los vacíos se formulan como preguntas abiertas.
6. Redactar el BIC con un diagrama Mermaid de decisiones y audiencias cuando aporte claridad.

## Comportamiento por modo
- **GREENFIELD:** derivar preguntas y decisiones del objetivo y las fuentes; `artifact_action` = `CREATE`.
- **BROWNFIELD:** incluir una sección *As-Is* con los reportes y decisiones que hoy existen; lo no documentado es supuesto o gap. `CREATE` o `UPDATE` según exista el BIC.
- **EVOLUTION:** actualizar solo las decisiones o audiencias afectadas por el cambio indicado; no reescribir el resto. Si no hay cambio, `NO_CHANGE`.

## Salida
Plantilla obligatoria: `assets/artifact.md` (estructura, definición y contenido mínimo de cada sección).
`BI-BIC-NNN-<slug>.md` en `./bi/context/`, con frontmatter OKF (`type: BIC`, `status: draft`, `id: BI-BIC-NNN`, `sources` no vacío salvo justificación, `generated`).

Secciones mínimas: propósito, alcance, insumos, preguntas de negocio con decisión asociada, audiencias, supuestos, vacíos, decisiones humanas pendientes y validación.

## Restricciones
- No inventar decisiones, audiencias ni objetivos que no aparezcan en las fuentes.
- No asignar `verified` ni `stable`; el estado documental lo decide una persona.
- Sin aprobación del gate G1, los skills dependientes no arrancan.
