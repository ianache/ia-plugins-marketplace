# Workflow contract

| Orden | Skill | Gate | Consumidor |
|---|---|---|---|
| 1 | innovation-opportunity-scout | G1 | problem-framing-researcher |
| 2 | problem-framing-researcher | G2 | creative-concept-explorer |
| 3 | creative-concept-explorer | G3 | solution-concept-architect |
| 4 | solution-concept-architect | G4 | innovation-experiment-designer |
| 5 | innovation-experiment-designer | G5 | innovation-requirements-handoff |
| 6 | innovation-requirements-handoff | G6 | requirements-engineering |

## Gate control
Outcome técnico READY/CONDITIONAL/NOT_READY; `approved=false` por defecto. Dependientes no avanzan sin aprobación humana de gates requeridos. Registros locales no autentican aprobadores.

## Handoff interoperable
`handoff.json` debe incluir: `initiative_id`, `scenario`, `selected_concept_id`, `sol_path`, `evidence_refs`, `hypotheses`, `experiment_results` (vacío si no ejecutados), `open_questions`, `constraints`, `stakeholders`, `success_metrics`, `rejected_alternatives`, `human_decision`, `requested_next_skill: af-requirements-orchestrator`.

`af-evidence-context-designer` debe evaluar fuentes y producir su propio RCP; `af-business-rules-modeler` y `af-user-story-designer` son posteriores. La transferencia no afirma que Requirements haya aceptado el handoff.
