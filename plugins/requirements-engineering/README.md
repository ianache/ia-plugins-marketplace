# Requirements Engineering — Claude Code Plugin v2.1.1

Un orchestrator (`af-requirements-orchestrator`) y cinco skills especializados, con contratos, gates humanos G0–G6 y trazabilidad.

Instalación local (Claude Code): usar el directorio raíz como plugin local; manifiesto en `.claude-plugin/plugin.json`, skills en `skills/<name>/SKILL.md`.

**No** se declara validación real en Claude Code ni aprobación humana de gates. Los scripts verifican estructura, no semántica OKF completa ni identidad del aprobador.

## Secuencia y gates
G0 alcance y fuentes → G1 RCP (`af-evidence-context-designer`) → G2 línea base de negocio (gate humano; BR, IMD y TRM los produce `business-knowledge`) → G3 historias US y épicas EPC opcionales (`af-user-story-designer`) → G4 criterios (`af-acceptance-quality-reviewer`) → G5 impacto IMP (`af-functional-impact-mapper`) → G6 handoff `DSP` (`af-requirements-pack-publisher`).

**Evidencia:** `transition` (a `NEEDS_REVIEW`/`DONE`) y `approve-gate` exigen `--evidence` con un archivo existente dentro del workspace; se guarda su ruta relativa. El texto libre o los archivos fuera del workspace se rechazan. **Alcance de `brownfield` y `evolution`:** el plan de tareas y gates es el mismo que el de `greenfield` (`workflow.py` no genera tareas distintas por escenario). Lo propio de Brownfield y Evolution (buscar lo existente, comparar As-Is/To-Be, partir de la línea base) vive en las instrucciones de los SKILL y depende de la revisión humana en cada gate; no hay tarea ni gate de línea base. 

El run se controla con `scripts/workflow.py` (`init`, `check`, `status`, `transition`, `approve-gate`). Cada tarea tiene un gate de entrada (el gate previo) y un gate de cierre; `check` falla con "gate cycle" si el de entrada no es anterior al de cierre. Escenarios: `greenfield`, `brownfield`, `evolution` (G0–G6) e `impact-only` (omite G3 y G4 con justificación obligatoria). `approve-gate` exige un actor `human:<nombre>` y evidencia.

## Conformidad OKF
Los documentos conceptuales cumplen STD-OKF-001 v0.1.0-stable. Tipos usados: `RCP`, `US`, `DSP` (aprobados en v1.2.0), `IMP` (aprobado en v1.3.0) y `EPC` (épica; sigla aprobada por el responsable, registrada en STD-OKF-001 v1.7.0). `BR`, `IMD` y `TRM` los produce `business-knowledge`.

## Output Pathmap v1.5.0
Ver `assets/pathmap.md` y `OUTPUT-PATH-POLICY.md`. Mapeados: RCP, US, IMP y DSP (`requirements/scope-packs/`). La línea base de negocio (`business/`: BR, IMD, TRM) es de solo lectura para este pack. Validar con `scripts/validate_pathmap.py`.

Ver `COVERAGE-MATRIX.md` y `VALIDATION.md`.

## IDs de User Stories
`RCP-NNN-US-NNN` (RCP que origina la historia), globalmente únicos (ver `assets/pathmap.md`). `python scripts/us_ids.py next --workspace . --rcp RCP-002` asigna el siguiente (solo recorre `requirements/`; `--exclude <glob>` omite rutas, p. ej. `requirements/examples/*`); `python scripts/us_ids.py check --workspace . --git-ref origin/develop [--also <otra-KB>]` verifica formato, nombre de archivo y duplicados entre KB y ramas. La asignación es local: la unicidad entre ramas depende de ejecutar `check --git-ref` antes de integrar. El código de producto (`product`, opcional) es metadato y no forma parte del ID.

## Cambio v1.4.0
`af-business-rules-modeler` (BR, IMD, glosario) se movió al plugin `business-knowledge` como `biz-rules-modeler`, junto con los nuevos `biz-glossary-curator` y `biz-information-model-designer`. G2 pasó a ser un gate humano de línea base de negocio sin tarea; las tareas del run son T01 (RCP), T02 (US), T03 (criterios), T04 (impacto) y T05 (handoff). Pathmap 1.4.0.
