# Contrato — ui-prototype-generator

**Producer:** `ui-prototype-generator` · **Gate:** `G4`.

## Inputs requeridos
SCR/CMP/TKN, decisiones de herramienta, accesos reales a herramientas.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
prototypes/prototype-brief.md; prototypes/tool-manifest.md; prototypes/review-log.md.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
enlaces/IDs reales si existen; sin simular generación o acceso; fidelidad con SCR.
