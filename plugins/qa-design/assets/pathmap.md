# QA Design — Pathmap

El mapeo de cada tipo documental QA (`document_types`, `artifacts`), la raíz de entregables (`deliverable_root`) y la raíz del estado operativo (`orchestrator_root`, `orchestrator_files`) viven solo en [`pathmap.json`](pathmap.json); su versión está en `pathmap_version`. Este archivo no repite ese contenido.

## Reglas de ejecución

1. El orchestrator (`qa-sdlc-orchestrator`) es el único escritor del estado operativo; lo guarda en `orchestrator_root/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`). Cada run tiene su propia carpeta: dos ejecuciones nunca comparten `plan.yaml`, estado ni evidencia.
2. Los skills especializados no escriben en `orchestrator_root`; entregan al orchestrator y este registra la evidencia.
3. Los entregables QA van a `testing/<DSP-ID>/` (y `testing/<DSP-ID>/<SSP-ID>/` si el diseño es para un sprint), sin versión: las pruebas pertenecen a un DSP y un SSP concretos. Cada documento se escribe en el subdirectorio que `pathmap.json` asigna a su `type`, relativo a esa raíz. El `kb_local_path` de la entrada fija solo el destino de publicación en la KB. Un tipo sin mapeo queda BLOCKED: no se inventan rutas.
4. Solo una instrucción explícita del usuario permite otra ruta, registrada con justificación; un skill no puede autorizarla.
5. Los scripts del plugin leen `pathmap.json`; no mantienen rutas propias.
