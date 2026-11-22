# Changelog

## [Sin publicar]

## [3.1.0] - 2026-11-21

### Cambiado

- Copia del estándar STD-OKF-001 propagada desde el maestro `v1.11.0-stable`: añade el tipo `IRP` (Informe o Reporte genérico) a la lista de tipos del validador; `QTD` pasa a cobertura, trazabilidad, TSN y TC, con estrategia y plan en `QTP`; incorpora la aclaración v1.9.0 sobre salidas de especialistas.


### Cambiado
- Aplicación de `plugin-skills-guideline.md`: estructura, README, VALIDATION, pathmap, contratos, modos y registro operativo bajo `.comsatel/ux-design/runs/<run-id>/`.
- El pack mantiene un orchestrator y nueve especialistas; documenta por qué supera el máximo recomendado de seis.
- Se conserva STD-OKF-001 v1.9.0 como perfil; los outputs usan tipos aprobados y las herramientas/payloads sin tipo se mantienen operativos.
- El resumen UXS pasa de `CTLG` a payload operativo de run; los conceptos externos STP, prompts GEN y briefs de alternativas dejan de presentarse como tipos OKF independientes.
- Se alinean tipos de handoff y accesibilidad en el validador y las fixtures.

### Migración
- Mover registros operativos previos desde ubicaciones ad hoc al nuevo `.comsatel/ux-design/runs/`; el initializer no migra runs existentes.
- Revisar cualquier documento `CTLG` con `catalog_role` y asegurar que indexa documentos de un mismo tipo aprobado.
- Cambios incompatibles de skill names/tipos/rutas deben registrarse como migración antes de publicar la versión mayor.
