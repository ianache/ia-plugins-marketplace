---
name: architecture-context-and-evidence-designer
description: Use when descubrimiento, contexto y evidencia is required in a governed
  architecture workflow; consumes evidence and produces traceable architecture artifacts
  under STD-OKF-001 v1.11.0-stable.
---

# architecture-context-and-evidence-designer

## Propósito y límites
Descubrimiento, contexto y evidencia. No asumir aprobación, no inventar fuentes, no convertir hipótesis en hechos.

## Entradas obligatorias
- Requirements Context Pack, US/BR, product KB, existing ADR/ASR/C4, repos and evidence links
- Scope, assumptions, source provenance, decisions and approvals from prior gates
- Contrato anterior y evidencia de gate aprobada cuando corresponda.

## Procedimiento
1. Leer `references/contract.md`, `references/technical-guidance.md` y `references/gate-checklist.md`.
2. Inspeccionar las capacidades originales listadas abajo y ejecutar sus procedimientos especializados según el escenario, sin omitir criterios de aceptación.
3. Separar FACT / INFERENCE / ASSUMPTION / UNKNOWN, con procedencia trazable.
4. Generar entregables conceptuales en `architecture/`; utilizar `templates/okf-artifact.md` para cada Markdown conceptual.
5. Registrar decisiones operativas, tareas y evidencias de gate en `.comsatel/architecture-design/runs/<run-id>/`.
6. Ejecutar `scripts/validate.py` sobre los Markdown; detener publicación ante incumplimientos.
7. Solicitar revisión humana de G1; el skill no se autoaprueba.

## Contrato de salida
- `output-manifest.json` con `producer`, `inputs`, `outputs`, `sources`, `open_questions`, `gate`, `status`.
- Tipos OKF preferentes: RCP, C4.
- Si el tipo no está aprobado, conservar `draft` y bloquear publicación estable.

## Capacidades integradas
Procedimientos de los skills originales fusionados en este skill: `architecture-discovery`, `architecture-knowledge-researcher`, `as-is-architecture-reconstructor`, `architecture-impact-analyzer`, `architecture-context-builder`, `architecture-context-critic`.

## Gate
G1: comprobar trazabilidad, suficiencia de evidencia, decisiones pendientes y aprobación explícita del arquitecto.

## Política obligatoria de rutas y contrato de ejecución

Leer `assets/pathmap.md` y `OUTPUT-PATH-POLICY.md` en la raíz del plugin. **No inferir el destino por nombre del skill ni usar `architecture/<run-id>/`.** Antes de producir cada documento, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y gate; validar que `output_dir` coincida con el mapeo de tipo OKF. ADR → `./architecture/adrs/`; ASR → `./architecture/asrs/`; los demás tipos usan el mapa. Si falta la ruta, bloquear y solicitar decisión al orchestrator. Solo una instrucción explícita del usuario permite override documentado. Verificar ruta real con `scripts/validate_pathmap.py` y metadatos con `scripts/validate_okf.py`. Entregar manifest de archivos producidos y evidencia para el gate. **Los entregables especializados nunca van a `./comsatel/`.**
