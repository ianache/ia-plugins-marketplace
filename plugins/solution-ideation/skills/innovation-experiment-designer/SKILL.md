---
name: innovation-experiment-designer
description: Usar para diseñar validación de hipótesis en iniciativas Greenfield, Brownfield o Evolution; producir experiment-plan.md y evidencia de G5 sin inventar validaciones.
metadata:
  version: "0.1.0"
---

# Diseñar validación de hipótesis

## Cuándo activar
Activar por asignación del `solution-ideation-orchestrator` o ante una petición específica de diseñar validación de hipótesis. No asumir aprobación de gates anteriores.

## Responsabilidad y límites
Matriz deseabilidad/viabilidad/factibilidad, experimentos, riesgos, métricas, umbrales y aprendizaje.

## Entradas obligatorias
- `initiative_id`, escenario (`greenfield|brownfield|evolution`), objetivo, producto o segmento, fuentes y restricciones.
- `.comsatel/solution-ideation/runs/<run-id>/execution-plan.json` y evidencias de gates precedentes, salvo ejecución exploratoria aislada declarada.
- Artefactos previos según `references/contract.md`.

## Método de trabajo
Priorizar supuestos más riesgosos. Diseñar experimentos de bajo costo (interviews, prototype, fake-door con consentimiento, concierge, PoC) con hipótesis falsables, métrica, umbral, tamaño/muestra razonado, ética y privacidad. No inventar resultados ni llamar validado a lo no ejecutado. Recomendar pivot/persevere/stop condicionado a evidencias.

## Salidas
- Documento conceptual `experiment-plan.md` en `design/ideation/<run-id>/` con frontmatter STD-OKF-001 v0.1.0-stable; tipo `SOL` (aprobado en v0.1.0-stable), **solo si** representa una propuesta de solución; para evidencia de exploración no propositiva usar registro operativo en `comsatel/` y referenciarlo desde el SOL final. No inventar tipos `IDE`, `OPP` u otros.
- `gate-evidence.json` con resultado técnico y referencias, sin `approved: true` automático.
- Plan de experimentos y decision log con estado not-tested/tested y riesgos residuales.

## Gate G5
Leer `references/gate-checklist.md`; `READY` no significa aprobado. El orchestrator bloquea dependientes hasta aprobación humana registrada.

## Validación y gobierno
Usar `python scripts/validate.py <ruta-documento.md>` desde este skill. Aplicar `standards/STD-OKF-001-v0.1.0-stable.md` de la raíz del plugin; `v0.1.0-stable` sigue siendo la baseline aprobada. No publicar automáticamente. No fabricar entrevistas, resultados, fuentes, firmas ni `verified`.

## Recursos del skill
- `references/contract.md`: contrato de datos y dependencias.
- `references/technical-guidance.md`: método y calidad.
- `references/gate-checklist.md`: checklist G5.
- `templates/deliverable.md`: plantilla conceptual OKF.
- `templates/gate-evidence.json`: evidencia operativa.
- `scripts/validate.py`: wrapper de validación.
- `examples/`: ejemplo sintético; `assets/`: convenciones de representación.
