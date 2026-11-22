# Contrato — ux-ui-design-orchestrator

**Producer:** `ux-ui-design-orchestrator` · **Gate:** `G0–G6`.

## Inputs requeridos
solicitud de diseño, escenario, fuentes, roles aprobadores.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
.comsatel/ux-ui-design/runs/<run-id>/plan.yaml; .comsatel/ux-ui-design/runs/<run-id>/gate-register.json.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
G0 alcance; G1 requerimientos; G2 pantallas; G3 sistema visual; G4 prototipo; G5 calidad; G6 handoff.
