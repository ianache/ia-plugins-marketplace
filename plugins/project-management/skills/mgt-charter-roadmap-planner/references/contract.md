# Contrato mgt-charter-roadmap-planner

- Gate de cierre: G1 (gate de entrada: G0)
- Inputs: Alcance del run (G0 aprobado) y, si existen, la línea base de negocio (`BCP`, `BO`, `BCAP` de `business-knowledge`), el contexto de requisitos (RCP, paquetes de alcance `DSP`) y las decisiones de arquitectura (ASR, ADR).
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: PCH; RMP. `management/charters/PCH-NNN-<slug>.md` y `management/roadmaps/RMP-NNN-<slug>.md`.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, decisión humana pendiente (compromiso, cambio, cierre) o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
