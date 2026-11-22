# Matriz de cobertura

| Capacidad | Skill | Tipo | Gate | Dónde se preserva |
|---|---|---|---|---|
| Contexto de negocio, objetivos y KPI, restricciones, supuestos, riesgos | `biz-context-objectives-analyst` | BCP, BO | G1 | `references/` y plantillas del skill |
| Partes interesadas | `biz-stakeholder-capability-mapper` | STK | G2 | plantilla `stakeholder.md` |
| Capacidades y procesos AS-IS | `biz-stakeholder-capability-mapper` | BCAP | G2 | plantilla `business-capability.md` |
| Glosario, sinónimos, siglas, niveles de fuente | `biz-glossary-curator` | TRM | G3 | `scripts/glossary.py`, `assets/source-levels.md` |
| Reglas, estados, validaciones, permisos y excepciones | `biz-rules-modeler` | BR | G4 | `assets/evidence-schema.md`, plantillas |
| Modelo de información conceptual, relaciones y estados | `biz-information-model-designer` | IMD | G5 | `scripts/check_model.py`, plantilla |
| Escenarios de negocio: secuencias de reglas BR con precondiciones, pasos, excepciones y resultado | `biz-scenario-modeler` | BSN | G5 | `templates/scenario.md`, `scripts/check_scenario.py` |
| Coherencia, trazabilidad y handoff | `biz-pack-validator-publisher` | handoff (operativo) | G6 | `scripts/check_pack.py` |
| Planificación, gates y control del run | `biz-knowledge-orchestrator` | operativo | G0-G6 | `scripts/workflow.py` |
