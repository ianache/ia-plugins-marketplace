---
name: solution-concept-architect
description: Usar para sintetizar conceptos y opciones en iniciativas Greenfield, Brownfield o Evolution; producir solution-concepts.md y evidencia de G4 sin inventar validaciones.
---

# Sintetizar conceptos y opciones

## Cuándo activar
Activar por asignación del `solution-ideation-orchestrator` o ante una petición específica de sintetizar conceptos y opciones. No asumir aprobación de gates anteriores.

## Responsabilidad y límites
Concept cards, storyboards, service blueprint ligero, mapa de capacidades y opciones de solución.

## Entradas obligatorias
- `initiative_id`, escenario (`greenfield|brownfield|evolution`), objetivo, producto o segmento, fuentes y restricciones.
- `.comsatel/solution-ideation/runs/<run-id>/execution-plan.json` y evidencias de gates precedentes, salvo ejecución exploratoria aislada declarada.
- Artefactos previos según `references/contract.md`.

## Método de trabajo
Agrupar y refinar ideas sin forzar selección; bosquejar experiencia, propuesta de valor, capabilities, integraciones probables y dependencias; distinguir arquitectura hipotética de decisiones ADR. Para Brownfield describir impacto preliminar y compatibilidad.

## Salidas
- Documento conceptual `solution-concepts.md` en `design/ideation/<run-id>/` con frontmatter STD-OKF-001 v1.11.0-stable; tipo `SOL` (aprobado en v1.11.0-stable), **solo si** representa una propuesta de solución; para evidencia de exploración no propositiva usar registro operativo en `comsatel/` y referenciarlo desde el SOL final. No inventar tipos `IDE`, `OPP` u otros.
- `gate-evidence.json` con resultado técnico y referencias, sin `approved: true` automático.
- Conceptos viables comparables y escenarios de uso, sin fingir diseño detallado ni requisitos aprobados.

## Gate G4
Leer `references/gate-checklist.md`; `READY` no significa aprobado. El orchestrator bloquea dependientes hasta aprobación humana registrada.

## Validación y gobierno
Usar `python scripts/validate.py <ruta-documento.md>` desde este skill. Aplicar `standards/STD-OKF-001-v1.11.0-stable.md` de la raíz del plugin; `v1.11.0-stable` sigue siendo la baseline aprobada. No publicar automáticamente. No fabricar entrevistas, resultados, fuentes, firmas ni `verified`.

## Recursos del skill
- `references/contract.md`: contrato de datos y dependencias.
- `references/technical-guidance.md`: método y calidad.
- `references/gate-checklist.md`: checklist G4.
- `templates/deliverable.md`: plantilla conceptual OKF.
- `templates/gate-evidence.json`: evidencia operativa.
- `scripts/validate.py`: wrapper de validación.
- `examples/`: ejemplo sintético; `assets/`: convenciones de representación.
