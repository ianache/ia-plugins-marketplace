# Output Pathmap — Microservice & API Design

Versión: 0.7.0. Este archivo fija las **reglas de ejecución**. El mapeo de cada tipo de documento a su ruta (tipos, archivos de salida, OpenAPI, marcadores `{service}` y `{codebase_service}`) vive solo en [`pathmap.json`](pathmap.json). Las rutas son relativas a `workspace_root` (la raíz del proyecto), **no** al directorio de instalación del plugin.

## Reglas de ejecución

1. El orchestrator **DEBE** leer `assets/pathmap.md` y `assets/pathmap.json` antes de planificar G0, resolver el `document_type` y pasar a cada skill `workspace_root`, `run_id`, `document_type`, `output_path`, `pathmap_version`, `gate` y `override_reason` si corresponde.
2. Los seis skills especializados **DEBEN** escribir únicamente en la ruta que resuelve `pathmap.json`, salvo instrucción explícita del usuario. No añadir `<run-id>` a la ruta de diseño; usar IDs estables en nombres de archivo para evitar colisiones.
3. El orchestrator **DEBE** registrar sus propios archivos en `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`); nunca mezclar ledger, planes ni gates con documentos de diseño. `workspace_root` nunca puede estar dentro de esa carpeta.
4. Si el tipo no está mapeado, bloquear la generación hasta que exista una asignación aprobada. No inferir rutas silenciosamente. Registrar overrides expresos y validar que no escapen del workspace.
5. Si una ruta depende de `codebase/<servicio>` y esa carpeta no existe, solicitar al humano la carpeta del servicio; no inventarla.
6. Validar pathmap (`scripts/validate_pathmap.py`) y frontmatter STD-OKF-001 v0.1.0-stable para Markdown conceptual. Usar un tipo registrado en el estándar; bloquear la publicación si el tipo no consta.
7. El destino de publicación KB `codebase/<MICROSERVICIO>/docs/functionalities/` es distinto del output local y requiere MR autorizado.
