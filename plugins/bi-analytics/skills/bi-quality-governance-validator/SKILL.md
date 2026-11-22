---
name: bi-quality-governance-validator
description: Valida trazabilidad KPI-modelo-dashboard, calidad de datos, acceso por rol y completitud del handoff. Produce BIQ.
---

# BI Quality and Governance Validator

Rol: **specialist**. Ejecutar solo con autorización del orquestador.

## Activación
Tarea T-06 (gate G6), después de G2 a G5 aprobados. Produce el tipo **BIQ** (BI Quality and Governance Report). Su gate es `MANDATORY_HIL`.

## Entradas
Autorización del orquestador y los entregables aprobados BIC, KPI, DSM, DMD y DSH.

## Procedimiento
1. Construir la matriz de trazabilidad BIC -> KPI -> medida (DMD) -> fuente (DSM) -> visualización (DSH) y señalar huérfanos en cualquier dirección.
2. Verificar que cada KPI es calculable con las fuentes declaradas y que cada gap tiene dueño y pregunta abierta.
3. Revisar calidad de datos: controles de completitud, unicidad, oportunidad y conciliación previstos, y si cada uno tiene evidencia.
4. Revisar gobierno: owners asignados, clasificación de datos, acceso por rol y tratamiento de datos personales.
5. Verificar frontmatter OKF, `type` registrado, `status: draft` y referencias válidas de todos los entregables.
6. Emitir el veredicto por criterio (`PASS`, `FAIL`, `BLOCKED`) con evidencia y las decisiones humanas necesarias.
7. Redactar el handoff con el resumen de alcance, riesgos y decisiones abiertas, sin marcarlo como aprobado.

## Comportamiento por modo
- **GREENFIELD:** validar la trazabilidad completa de los seis entregables.
- **BROWNFIELD:** validar también el As-Is reconstruido y los gaps de la reconstrucción.
- **EVOLUTION:** validar los elementos reabiertos y confirmar que los `NO_CHANGE` siguen siendo coherentes con ellos. Un huérfano hacia un elemento reabierto bloquea G6.

## Salida
Plantilla obligatoria: `assets/artifact.md` (estructura, definición y contenido mínimo de cada sección).
`BI-BIQ-NNN-<slug>.md` en `./bi/governance/`, con frontmatter OKF (`type: BIQ`, `status: draft`, `id: BI-BIQ-NNN`).

Secciones mínimas: alcance validado, matriz de trazabilidad, huérfanos, calidad de datos, gobierno y acceso, veredictos por criterio, riesgos, decisiones humanas pendientes y handoff.

## Restricciones
- No declarar PASS por la existencia de archivos; cada criterio requiere evidencia verificable.
- La aprobación del gate G6 la da una persona autorizada, no este skill.
- Un huérfano o un KPI sin fuente bloquea G6.
