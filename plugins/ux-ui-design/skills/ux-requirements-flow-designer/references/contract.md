# Contrato — ux-requirements-flow-designer

**Producer:** `ux-requirements-flow-designer` · **Gate:** `G1`.

## Inputs requeridos
US, BR, RCP, permisos, actores, journeys existentes.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
requirements/ux-requirements.md; flows/user-flows.md; flows/traceability.md.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
trazabilidad US→UXR→FLW, casos alternos, sin inventar reglas.
