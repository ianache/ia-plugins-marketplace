# Mapa de rutas de salida — ssp-closure

La única fuente de mapeo por tipo es [`pathmap.json`](pathmap.json). El orchestrator lee `orchestrator_root` al inicializar cada run. Los especialistas no inventan destinos.

- `STR`: un informe consolidado por periodo, `management/status-reports/STR-<ID>.md`.
- `CLS`: un informe de cierre por SSP, `management/closure/CLS-<ID>.md`.
- Agendas, payloads, propuestas de gate e integración GitLab son operativos y no reciben `type` OKF. Se guardan en `task-results/` o `evidence/<GATE>/` bajo la raíz del run.
- Todo documento OKF lleva el ID como prefijo del nombre de archivo y usa la plantilla del tipo.
- No sobrescribir un STR/CLS existente sin versionado o instrucción explícita. Los artefactos se relacionan al SSP/periodo con sus referencias y fuentes.
- Solo se acepta la ruta canónica; un override requiere una instrucción explícita del usuario y queda registrado en el run.

La separación es deliberada: `.comsatel` contiene control de ejecución y payloads operativos; `management/` contiene documentos de gestión conceptuales persistentes.
