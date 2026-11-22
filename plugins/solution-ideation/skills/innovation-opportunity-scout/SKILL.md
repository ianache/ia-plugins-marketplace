---
name: innovation-opportunity-scout
description: Usar para explorar oportunidades y señales en iniciativas Greenfield, Brownfield o Evolution; producir opportunity-map.md y evidencia de G1 sin inventar validaciones.
---

# Explorar oportunidades y señales

## Cuándo activar
Activar por asignación del `solution-ideation-orchestrator` o ante una petición específica de explorar oportunidades y señales. No asumir aprobación de gates anteriores.

## Responsabilidad y límites
Mapa de oportunidades, tendencias, capacidades existentes, restricciones, señales, incertidumbres y fuentes verificables.

## Entradas obligatorias
- `initiative_id`, escenario (`greenfield|brownfield|evolution`), objetivo, producto o segmento, fuentes y restricciones.
- `.comsatel/solution-ideation/runs/<run-id>/execution-plan.json` y evidencias de gates precedentes, salvo ejecución exploratoria aislada declarada.
- Artefactos previos según `references/contract.md`.

## Método de trabajo
Buscar señales de clientes, mercado, producto, telemetría, procesos y tecnología; diferenciar evidencias, hipótesis y extrapolaciones. Evaluar valor estratégico y riesgos de privacidad; no confundir tendencia con necesidad demostrada.

## Salidas
- Documento conceptual `opportunity-map.md` en `design/ideation/<run-id>/` con frontmatter STD-OKF-001 v1.11.0-stable; tipo `SOL` (aprobado en v1.11.0-stable), **solo si** representa una propuesta de solución; para evidencia de exploración no propositiva usar registro operativo en `comsatel/` y referenciarlo desde el SOL final. No inventar tipos `IDE`, `OPP` u otros.
- `gate-evidence.json` con resultado técnico y referencias, sin `approved: true` automático.
- Inventario de señales y oportunidades con procedencia, grado de confianza y preguntas abiertas.

## Gate G1
Leer `references/gate-checklist.md`; `READY` no significa aprobado. El orchestrator bloquea dependientes hasta aprobación humana registrada.

## Validación y gobierno
Usar `python scripts/validate.py <ruta-documento.md>` desde este skill. Aplicar `standards/STD-OKF-001-v1.11.0-stable.md` de la raíz del plugin; `v1.11.0-stable` sigue siendo la baseline aprobada. No publicar automáticamente. No fabricar entrevistas, resultados, fuentes, firmas ni `verified`.

## Recursos del skill
- `references/contract.md`: contrato de datos y dependencias.
- `references/technical-guidance.md`: método y calidad.
- `references/gate-checklist.md`: checklist G1.
- `templates/deliverable.md`: plantilla conceptual OKF.
- `templates/gate-evidence.json`: evidencia operativa.
- `scripts/validate.py`: wrapper de validación.
- `examples/`: ejemplo sintético; `assets/`: convenciones de representación.
