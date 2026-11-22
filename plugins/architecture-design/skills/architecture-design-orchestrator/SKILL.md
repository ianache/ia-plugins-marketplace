---
name: architecture-design-orchestrator
description: Use when planificar, encadenar y controlar gates g0–g6 is required in
  a governed architecture workflow; consumes evidence and produces traceable architecture
  artifacts under STD-OKF-001 v1.11.0-stable.
---

# architecture-design-orchestrator

## Propósito y límites
Planificar, encadenar y controlar gates G0–G6. No asumir aprobación, no inventar fuentes, no convertir hipótesis en hechos.

## Entradas obligatorias
- Requirements Context Pack, US/BR, product KB, existing ADR/ASR/C4, repos and evidence links
- Scope, assumptions, source provenance, decisions and approvals from prior gates
- Contrato anterior y evidencia de gate aprobada cuando corresponda.

## Procedimiento
1. Leer `references/contract.md`, `references/technical-guidance.md` y `references/gate-checklist.md`.
2. Inspeccionar las capacidades originales listadas abajo y ejecutar sus procedimientos especializados según el escenario, sin omitir criterios de aceptación.
3. Separar FACT / INFERENCE / ASSUMPTION / UNKNOWN, con procedencia trazable.
4. No genera documentos OKF. Sus salidas son planes, estado y registros de gate operativos bajo `.comsatel/architecture-design/runs/<run-id>/`.
5. Registrar decisiones operativas, tareas y evidencias de gate en `.comsatel/architecture-design/runs/<run-id>/`.
6. Ejecutar `scripts/validate.py` sobre los Markdown; detener publicación ante incumplimientos.
7. Solicitar revisión humana de G0–G6; el skill no se autoaprueba.

## Contrato de salida
- `output-manifest.json` con `producer`, `inputs`, `outputs`, `sources`, `open_questions`, `gate`, `status`.
- Tipos OKF preferentes: ninguno; planes y gates operativos JSON/YAML.
- Si el tipo no está aprobado, conservar `draft` y bloquear publicación estable.

## Gate
G0–G6: comprobar trazabilidad, suficiencia de evidencia, decisiones pendientes y aprobación explícita del arquitecto.

## Coordinación
- G0: aprobar alcance, escenarios Greenfield/Brownfield/Evolution/Continuous Governance, fuentes y plan.
- G1: context-and-evidence-designer.
- G2: asr-and-solution-designer.
- G3: decision-governor.
- G4: conformance-assessor (si hay baseline/código verificable).
- G5: evolution-governor (si hay cambio, drift o deuda).
- G6: development-handoff (solo con artefactos aprobados).
- Las tareas G4/G5 son condicionales, pero omisiones se justifican en el plan.
- Escenarios (`python scripts/workflow.py init --scenario <s>`): `greenfield` = G1, G2, G3, G6; `brownfield` = G1, G2, G3, G4, G6 (omite G5); `evolution` = G1 a G6; `continuous-governance` es alias de `evolution`. Los gates omitidos quedan en `omissions` del plan y G6 exige su justificación (`justify-omission`).
- Cada tarea entra por el gate anterior al que cierra. Mover una tarea a `NEEDS_REVIEW`/`DONE` exige el `output-manifest.json` del skill (`producer` y `gate` coherentes). Los gates los aprueba solo un actor `human:<nombre>`.
- Revisión humana independiente en cada gate; no registrar `approved` por ejecución de script.

## Política obligatoria de rutas y contrato de ejecución

Leer `assets/pathmap.md` y `OUTPUT-PATH-POLICY.md` en la raíz del plugin. **No inferir el destino por nombre del skill ni usar `architecture/<run-id>/`.** Antes de producir cada documento, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y gate; validar que `output_dir` coincida con el mapeo de tipo OKF. ADR → `./architecture/adrs/`; ASR → `./architecture/asrs/`; los demás tipos usan el mapa. Si falta la ruta, bloquear y solicitar decisión al orchestrator. Solo una instrucción explícita del usuario permite override documentado. Verificar ruta real con `scripts/validate_pathmap.py` y metadatos con `scripts/validate_okf.py`. Entregar manifest de archivos producidos y evidencia para el gate. **Los entregables especializados nunca van a `./comsatel/`.**

### Obligaciones específicas del orchestrator

En G0 leer `assets/pathmap.md`, registrar versión y generar `routing-contracts.json` en `.comsatel/architecture-design/runs/<run-id>/`, con `document_type` y `output_dir` para cada tarea/artefacto. Antes de invocar cada skill, entregar su contrato de rutas y bloquear tipos no mapeados. En G1–G6 comprobar manifest, rutas reales, OKF y aprobación humana; registrar excepciones solicitadas explícitamente por el usuario. Solo el orchestrator escribe planes, estados y registros de gates en `.comsatel/architecture-design/runs/<run-id>/`. No modificar el pathmap unilateralmente.
