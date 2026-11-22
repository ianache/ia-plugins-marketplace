---
type: EXEC
title: "Test Execution"
description: "<una frase para recuperación e indexación>"
id: <PRODUCTO>-EXEC-001
version: "1.0.0"
status: draft
owner: team:quality-engineering
classification: internal
tags: [qa, exec]
pack: qa-sdlc-pack
skill: qa-agentic-test-engineer
generated:
  by: qa-agentic-test-engineer/1.5.0
  at: "<ISO-8601 con zona>"
sources:
  - id: dsp
    resource: "<ruta o URI del DSP>"
    title: "<DSP-ID>@<versión>"
execution_mode: MANUAL   # MANUAL | AUTOMATED_STANDALONE | AUTOMATED_CICD (pertenece a la EXEC, no al TC)
testcase_ref: TC-XXX
at_ref: null   # obligatorio en AUTOMATED_STANDALONE y AUTOMATED_CICD; MANUAL no requiere AT
tda_refs: []
environment: <entorno autorizado>
executor: <persona, agente o runtime>
runtime: {name: null, version: null}   # AUTOMATED_STANDALONE: herramienta autorizada y versión
result: PASSED   # PASSED | FAILED | ERROR | BLOCKED (el `status` del frontmatter es el estado documental)
oracle_evaluated: true
started_at: "<ISO-8601 con zona>"
finished_at: "<ISO-8601 con zona>"
rerun_of: null   # un re-run es una EXEC nueva que referencia a la anterior
failure_class: null   # FUNCTIONAL | PIPELINE | ENVIRONMENT | TEST_DATA | TOOLING | UNCLASSIFIED (obligatorio si FAILED o ERROR)
authorization_ref: null   # obligatorio si el entorno es PROD
ci:   # AUTOMATED_CICD: identificadores reales; null mientras no exista la ejecución (no inventar)
  provider: null   # GITLAB
  pipeline_id: null
  pipeline_url: null
  job_id: null
  job_name: null
  commit_sha: null
  ref: null
evidence_refs: [EVD-XXX]
---
# EXEC-XXX — <TC> (<modo>)
## Resumen
## Datos utilizados (TDA)
## Resultado frente al oracle
## Procedencia de la ejecución
MANUAL: ejecutor, entorno, observaciones. AUTOMATED_STANDALONE: runtime, versión, comando. AUTOMATED_CICD: pipeline, job, commit, rama o tag.
## Evidencia (EVD)
## Defectos candidatos
## Re-ejecución
Si es un re-run: EXEC anterior (`rerun_of`) y motivo. El historial se conserva.
