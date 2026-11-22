# Contrato — ui-design-quality-validator

**Producer:** `ui-design-quality-validator` · **Gate:** `G5`.

## Inputs requeridos
UXR/FLW/SCR/CMP/TKN, prototipos y criterios de aceptación.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
quality/design-review.md; quality/accessibility-review.md; quality/coverage-matrix.md.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
hallazgos priorizados, WCAG aplicable, consistencia y evidencias reales.
