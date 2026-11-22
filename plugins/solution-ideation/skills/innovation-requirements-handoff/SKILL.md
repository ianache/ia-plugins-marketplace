---
name: innovation-requirements-handoff
description: Usar para preparar transferencia a requirements engineering en iniciativas Greenfield, Brownfield o Evolution; producir requirements-handoff.md y evidencia de G6 sin inventar validaciones.
metadata:
  version: "0.1.0"
---

# Preparar transferencia a Requirements Engineering

## Cuándo activar
Activar por asignación del `solution-ideation-orchestrator` o ante una petición específica de preparar transferencia a requirements engineering. No asumir aprobación de gates anteriores.

## Responsabilidad y límites
Opportunity brief, concepto seleccionado, hipótesis, límites, evidencia, riesgos y contrato de handoff.

## Entradas obligatorias
- `initiative_id`, escenario (`greenfield|brownfield|evolution`), objetivo, producto o segmento, fuentes y restricciones.
- `.comsatel/solution-ideation/runs/<run-id>/execution-plan.json` y evidencias de gates precedentes, salvo ejecución exploratoria aislada declarada.
- Artefactos previos según `references/contract.md`.

## Método de trabajo
Producir propuesta SOL draft conforme OKF y handoff JSON consumible por af-requirements-orchestrator / af-evidence-context-designer. Mantener las ideas no seleccionadas en backlog. No producir User Stories ni Business Rules como si estuvieran validadas. Explicitar preguntas abiertas y criterios de entrada al Requirements Context Pack.

## Salidas
- Documento conceptual `requirements-handoff.md` en `design/ideation/<run-id>/` con frontmatter STD-OKF-001 v0.1.0-stable; tipo `SOL` (aprobado en v0.1.0-stable), **solo si** representa una propuesta de solución; para evidencia de exploración no propositiva usar registro operativo en `comsatel/` y referenciarlo desde el SOL final. No inventar tipos `IDE`, `OPP` u otros.
- `gate-evidence.json` con resultado técnico y referencias, sin `approved: true` automático.
- Paquete de entrada versionado con provenance, trazabilidad, decisiones humanas y pendientes.

## Gate G6
Leer `references/gate-checklist.md`; `READY` no significa aprobado. El orchestrator bloquea dependientes hasta aprobación humana registrada.

## Validación y gobierno
Usar `python scripts/validate.py <ruta-documento.md>` desde este skill. Aplicar `standards/STD-OKF-001-v0.1.0-stable.md` de la raíz del plugin; `v0.1.0-stable` sigue siendo la baseline aprobada. No publicar automáticamente. No fabricar entrevistas, resultados, fuentes, firmas ni `verified`.

## Recursos del skill
- `references/contract.md`: contrato de datos y dependencias.
- `references/technical-guidance.md`: método y calidad.
- `references/gate-checklist.md`: checklist G6.
- `templates/deliverable.md`: plantilla conceptual OKF.
- `templates/gate-evidence.json`: evidencia operativa.
- `scripts/validate.py`: wrapper de validación.
- `examples/`: ejemplo sintético; `assets/`: convenciones de representación.
