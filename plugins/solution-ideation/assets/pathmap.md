# Solution Ideation — Pathmap

El mapeo de los entregables (`output_files`, `document_types` si aplica) y las raíces (`deliverable_root`, `orchestrator_root`) viven solo en [`pathmap.json`](pathmap.json); su versión está en `pathmap_version`. Este archivo no repite ese contenido. Las rutas son relativas a `workspace_root`, no al directorio de instalación del plugin.

## Reglas de ejecución

1. El orchestrator lee este archivo y `assets/pathmap.json` al iniciar G0 y resuelve la ruta de cada entregable antes de encargarlo.
2. Los skills especializados escriben solo bajo `deliverable_root` (con `{run_id}` sustituido), en la ruta relativa que `output_files` asigna a su skill. No escriben estado de ejecución allí.
3. El orchestrator guarda planes, estado, gates y evidencia exclusivamente bajo `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`); nunca los mezcla con los entregables.
4. Una salida sin mapeo queda BLOCKED. Solo una instrucción explícita del usuario permite otra ruta, registrada con texto original, ruta resuelta, actor y justificación; un skill no puede autorizarla.
5. No sobrescribir entregables existentes sin decisión explícita de evolución o versionado; no reutilizar un `run-id` existente.
6. Los Markdown conceptuales cumplen STD-OKF-001 v1.11.0-stable; los archivos operativos JSON/YAML no son documentos OKF.
7. Los scripts del plugin leen `pathmap.json`; no mantienen rutas propias.
