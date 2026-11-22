---
name: creative-concept-explorer
description: Usar para generar alternativas divergentes en iniciativas Greenfield, Brownfield o Evolution; producir concept-portfolio.md y evidencia de G3 sin inventar validaciones.
metadata:
  version: "0.1.0"
---

# Generar alternativas divergentes

## Cuándo activar
Activar por asignación del `solution-ideation-orchestrator` o ante una petición específica de generar alternativas divergentes. No asumir aprobación de gates anteriores.

## Responsabilidad y límites
Portafolio diverso de conceptos, analogías, escenarios y combinaciones; no converger prematuramente.

## Entradas obligatorias
- `initiative_id`, escenario (`greenfield|brownfield|evolution`), objetivo, producto o segmento, fuentes y restricciones.
- `.comsatel/solution-ideation/runs/<run-id>/execution-plan.json` y evidencias de gates precedentes, salvo ejecución exploratoria aislada declarada.
- Artefactos previos según `references/contract.md`.

## Método de trabajo
Aplicar al menos tres técnicas entre How Might We, SCAMPER, analogías cross-industry, inversión de supuestos, Crazy 8s, combinatoria y futuros alternativos. Producir >=8 ideas distintas por defecto, incluidas una incremental, una disruptiva y una de bajo costo. No presentar IA como solución obligatoria. Registrar originalidad hipotética sin afirmar novedad mundial.

## Salidas
- Documento conceptual `concept-portfolio.md` en `design/ideation/<run-id>/` con frontmatter STD-OKF-001 v0.1.0-stable; tipo `SOL` (aprobado en v0.1.0-stable), **solo si** representa una propuesta de solución; para evidencia de exploración no propositiva usar registro operativo en `comsatel/` y referenciarlo desde el SOL final. No inventar tipos `IDE`, `OPP` u otros.
- `gate-evidence.json` con resultado técnico y referencias, sin `approved: true` automático.
- Portafolio de conceptos con valor, riesgos, dependencias, diferencias y contraargumentos.

## Gate G3
Leer `references/gate-checklist.md`; `READY` no significa aprobado. El orchestrator bloquea dependientes hasta aprobación humana registrada.

## Validación y gobierno
Usar `python scripts/validate.py <ruta-documento.md>` desde este skill. Aplicar `standards/STD-OKF-001-v0.1.0-stable.md` de la raíz del plugin; `v0.1.0-stable` sigue siendo la baseline aprobada. No publicar automáticamente. No fabricar entrevistas, resultados, fuentes, firmas ni `verified`.

## Recursos del skill
- `references/contract.md`: contrato de datos y dependencias.
- `references/technical-guidance.md`: método y calidad.
- `references/gate-checklist.md`: checklist G3.
- `templates/deliverable.md`: plantilla conceptual OKF.
- `templates/gate-evidence.json`: evidencia operativa.
- `scripts/validate.py`: wrapper de validación.
- `examples/`: ejemplo sintético; `assets/`: convenciones de representación.
