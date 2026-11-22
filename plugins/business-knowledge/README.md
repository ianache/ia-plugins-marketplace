# Business Knowledge — Claude Code Plugin v2.0.0

Un orchestrator (`biz-knowledge-orchestrator`) y siete skills especializados que construyen y mantienen la línea base de conocimiento de negocio de un producto o iniciativa, con contratos, gates humanos G0–G6 y trazabilidad. Los consumen `requirements-engineering`, `ux-ui-design`, `architecture-design`, `ddd-domain-design` y `data-modeling-database-design`.

Instalación local (Claude Code): usar el directorio raíz como plugin local; manifiesto en `.claude-plugin/plugin.json`, skills en `skills/<name>/SKILL.md`.

**No** se declara validación real en Claude Code ni aprobación humana de gates. Los scripts verifican estructura, no semántica OKF completa ni identidad del aprobador.

## Secuencia y gates
G0 alcance y fuentes -> G1 contexto y objetivos `BCP`, `BO` (`biz-context-objectives-analyst`) -> G2 actores y capacidades `STK`, `BCAP` (`biz-stakeholder-capability-mapper`) -> G3 glosario `TRM` (`biz-glossary-curator`) -> G4 reglas `BR` (`biz-rules-modeler`) -> G5 modelo de información `IMD` (`biz-information-model-designer`) -> G6 validación y handoff (`biz-pack-validator-publisher`).

**Evidencia:** `transition` (a `NEEDS_REVIEW`/`DONE`) y `approve-gate` exigen `--evidence` con un archivo existente dentro del workspace; se guarda su ruta relativa. El texto libre o los archivos fuera del workspace se rechazan. **Alcance de `brownfield` y `evolution`:** el plan de tareas y gates es el mismo que el de `greenfield` (`workflow.py` no genera tareas distintas por escenario). Lo propio de Brownfield y Evolution (buscar lo existente, comparar As-Is/To-Be, partir de la línea base) vive en las instrucciones de los SKILL y depende de la revisión humana en cada gate; no hay tarea ni gate de línea base. 

`init --omit G5 --justification "<motivo>"` omite T05/G5 (IMD) cuando el cambio no toca el modelo de información (p. ej. solo una regla y un término); sin `--justification` se rechaza y T06 pasa a depender de G4.

El run se controla con `scripts/workflow.py` (`init`, `check`, `status`, `transition`, `approve-gate`). Escenarios: `greenfield`, `brownfield`, `evolution` (G0–G6) e `incremental` (omite G1 y G2 con justificación obligatoria; actualiza una línea base aprobada). `approve-gate` exige un actor `human:<nombre>` y evidencia.

## Origen de los skills
| Skill | Capacidad original |
|---|---|
| `biz-context-objectives-analyst` | `business-context-builder` (skill suelto) |
| `biz-stakeholder-capability-mapper` | stakeholders y capacidades de `business-context-builder`; mapa de procesos nuevo |
| `biz-glossary-curator` | `af-business-glossary-curator` (skill suelto), adaptado al tipo `TRM` |
| `biz-rules-modeler` | `af-business-rules-modeler`, **movido desde `requirements-engineering`**, más `af-business-rule-extractor` |
| `biz-information-model-designer` | `af-conceptual-model-designer` (skill suelto) |
| `biz-pack-validator-publisher` | nuevo (`check_pack.py`) |
| `biz-scenario-modeler` | nuevo en 2.1.0: tipo `BSN` (escenario de negocio), con contrato de contenido en `templates/scenario.md` y verificación con `scripts/check_scenario.py` |

## Conformidad OKF
Los documentos cumplen STD-OKF-001 v1.9.0-stable. Tipos aprobados en esa versión y usados aquí: `TRM`, `BCP`, `BO`, `STK`, `BCAP`, `IMD`, `BR` y `BSN` (escenario de negocio, aprobado en v1.8.0). `python scripts/validate_okf.py documento.md` valida el frontmatter; `--publication` es la revisión estricta y rechaza los tipos no registrados.

## Output Pathmap v1.0.0
Ver `assets/pathmap.md` y `OUTPUT-PATH-POLICY.md`. Todos los entregables van bajo `./business/`; los registros operativos, en `.comsatel/business-knowledge/runs/<run-id>/`. Validar con `scripts/validate_pathmap.py` y, para el conjunto, `skills/biz-pack-validator-publisher/scripts/check_pack.py`.

Ver `COVERAGE-MATRIX.md` y `VALIDATION.md`.
