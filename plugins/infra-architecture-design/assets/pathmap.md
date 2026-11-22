# Infrastructure Architecture Design — Pathmap

El mapeo de cada artefacto a su directorio (`document_types`, `artifacts` con su skill propietario), la raíz de salida (`output_root`) la equivalencia de cada artefacto con su tipo OKF aprobado (`okf_types`: p. ej. `topology` → `ITP`, `baseline` → `IBL`) y la raíz del orchestrator (`orchestrator_root`, `orchestrator_files`) viven solo en [`pathmap.json`](pathmap.json); su versión está en `pathmap_version`. Este archivo no repite ese contenido. Las rutas son relativas a la raíz del proyecto, no al directorio de instalación del plugin.

## Reglas de ejecución

1. El orchestrator lee este archivo y `assets/pathmap.json` al iniciar y resuelve el directorio de cada artefacto por su tipo antes de encargarlo.
2. Cada skill especializado escribe solo en los directorios que `pathmap.json` asigna a sus artefactos.
3. El plan, el estado, los gates y la evidencia operativa no son documentos OKF conceptuales: van exclusivamente bajo `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`) y nunca bajo `output_root`. La CLI rechaza planes fuera de esa ruta.
4. Un artefacto sin mapeo queda BLOCKED. Solo una instrucción explícita del usuario permite otra ruta, registrada con justificación; un skill no puede autorizarla.
5. Los scripts del plugin leen `pathmap.json`; no mantienen rutas propias.
