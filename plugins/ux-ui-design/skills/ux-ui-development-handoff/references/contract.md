# Contrato — ux-ui-development-handoff

**Producer:** `ux-ui-development-handoff` · **Gate:** `G6`.

## Inputs requeridos
artefactos aprobados, revisiones, referencias Figma y contratos funcionales.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
handoff/ux-ui-handoff.md; handoff/screen-component-mapping.md; handoff/change-request-register.md.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
HOF consumible por Web/Mobile; baseline, cambios y pendientes explícitos.
