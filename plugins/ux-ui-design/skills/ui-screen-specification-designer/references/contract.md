# Contrato — ui-screen-specification-designer

**Producer:** `ui-screen-specification-designer` · **Gate:** `G2`.

## Inputs requeridos
UXR, FLW aprobados, restricciones de producto, plataformas.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
screens/screen-specifications.md; screens/navigation-map.md; screens/state-matrix.md.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
SCR vinculadas a FLW, loading/empty/error, permisos y responsive.
