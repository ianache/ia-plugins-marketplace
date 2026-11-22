# Contrato biz-scenario-modeler

- Tipo documental: `BSN` (Business Scenario), registrado en STD-OKF-001 v0.1.0-stable.
- Gate de cierre: no asignado. Pendiente de decisión del orchestrator sobre su encadenamiento.
- Inputs: reglas `BR` (en `business/rules/`), términos `TRM` (en `business/terms/`), `BCAP` y `BO` del alcance.
- Precondición: las reglas y términos citados existen en `business/` con su ID; el escenario tiene actor, capacidad y disparador.
- Output: `business/scenarios/BSN-NNN-<slug>.md`, con las once secciones de `templates/scenario.md`.
- Postcondición: cada paso referencia una `BR` existente; cada término referencia un `TRM` existente; las preguntas abiertas tienen responsable.
- Readiness: READY / CONDITIONAL / NOT_READY, declarado en la sección 11.
- Bloqueo: regla o término citado inexistente, actor sin definir, contradicción crítica entre reglas, o falta de disparador.
- Evidence: fuente, clasificación, confianza y owner de cada afirmación (sección 9).
- Handoff: ID del escenario, rutas, versión y lista de reglas y términos usados.
