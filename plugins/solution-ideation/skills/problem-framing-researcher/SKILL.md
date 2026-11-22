---
name: problem-framing-researcher
description: Usar para investigar problemas y necesidades en iniciativas Greenfield, Brownfield o Evolution; producir problem-framing.md y evidencia de G2 sin inventar validaciones.
metadata:
  version: "0.1.0"
---

# Investigar problemas y necesidades

## Cuándo activar
Activar por asignación del `solution-ideation-orchestrator` o ante una petición específica de investigar problemas y necesidades. No asumir aprobación de gates anteriores.

## Responsabilidad y límites
Problem framing, Jobs-to-be-Done, actores, segmentos, pains/gains, proceso actual y baseline.

## Entradas obligatorias
- `initiative_id`, escenario (`greenfield|brownfield|evolution`), objetivo, producto o segmento, fuentes y restricciones.
- `.comsatel/solution-ideation/runs/<run-id>/execution-plan.json` y evidencias de gates precedentes, salvo ejecución exploratoria aislada declarada.
- Artefactos previos según `references/contract.md`.

## Método de trabajo
Formular problema sin fijar solución; entrevistar o solicitar evidencia cuando falte; separar usuario, comprador y operador; documentar As-Is, métricas base, restricciones y supuestos. En Evolution mapear fricciones y capacidades existentes.

## Salidas
- Documento conceptual `problem-framing.md` en `design/ideation/<run-id>/` con frontmatter STD-OKF-001 v0.1.0-stable; tipo `SOL` (aprobado en v0.1.0-stable), **solo si** representa una propuesta de solución; para evidencia de exploración no propositiva usar registro operativo en `comsatel/` y referenciarlo desde el SOL final. No inventar tipos `IDE`, `OPP` u otros.
- `gate-evidence.json` con resultado técnico y referencias, sin `approved: true` automático.
- Problemas priorizados, JTBD, actores, evidencia, hipótesis y criterios de éxito.

## Gate G2
Leer `references/gate-checklist.md`; `READY` no significa aprobado. El orchestrator bloquea dependientes hasta aprobación humana registrada.

## Validación y gobierno
Usar `python scripts/validate.py <ruta-documento.md>` desde este skill. Aplicar `standards/STD-OKF-001-v0.1.0-stable.md` de la raíz del plugin; `v0.1.0-stable` sigue siendo la baseline aprobada. No publicar automáticamente. No fabricar entrevistas, resultados, fuentes, firmas ni `verified`.

## Recursos del skill
- `references/contract.md`: contrato de datos y dependencias.
- `references/technical-guidance.md`: método y calidad.
- `references/gate-checklist.md`: checklist G2.
- `templates/deliverable.md`: plantilla conceptual OKF.
- `templates/gate-evidence.json`: evidencia operativa.
- `scripts/validate.py`: wrapper de validación.
- `examples/`: ejemplo sintético; `assets/`: convenciones de representación.
