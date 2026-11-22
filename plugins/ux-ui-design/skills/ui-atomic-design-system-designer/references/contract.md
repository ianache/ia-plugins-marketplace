# Contrato — ui-atomic-design-system-designer

**Producer:** `ui-atomic-design-system-designer` · **Gate:** `G3`.

## Inputs requeridos
SCR, estándares corporativos, librerías Figma y restricciones de plataforma.

- Cada referencia debe incluir ID, versión o commit, ruta/URI, estado y procedencia.
- Entradas ausentes: bloquear si impiden trazabilidad; no sustituir con supuestos presentados como hechos.

## Outputs contractuales
design-system/atomic-component-catalog.md; design-system/design-tokens.md; design-system/platform-adaptation.md.

- Cada documento conceptual contiene frontmatter OKF y se ubica bajo `design/ux-ui/<run-id>/`.
- El estado del gate, aprobaciones y plan pertenecen a `.comsatel/ux-ui-design/runs/<run-id>/`.

## Resultado de ejecución
Informar al orchestrator: `skill`, `run_id`, `inputs`, `outputs`, `gate`, `issues`, `decision_requested`. Nunca declarar aprobado sin evidencia del aprobador.

## Condiciones de salida
CMP/TKN con IDs, variantes, estados, accesibilidad y versionado; sin Angular/Flutter.
