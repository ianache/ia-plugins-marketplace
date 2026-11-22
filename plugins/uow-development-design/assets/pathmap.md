# Pathmap — uow-development-design

El mapeo de cada tipo documental (`UCX`, `UOW`, `UCB`, `UCM`, `UAP`, `UWR`), el manifiesto `uow-package.yaml`, los insumos de solo lectura y el estado operativo vive solo en [`pathmap.json`](pathmap.json), bajo `document_types`, `artifacts`, `manifest`, `inputs_read_only` y `orchestrator_root`. Este archivo no repite ese contenido.

## Reglas de ejecución

1. El orchestrator lee este archivo y `assets/pathmap.json` en G0 y resuelve el destino de cada documento por su tipo antes de encargarlo.
2. Los documentos no llevan `run-id` en su ruta canónica; el estado operativo (plan, gates, eventos y evidencia) se guarda solo bajo `orchestrator_root`.
3. Los insumos de otros packs son de solo lectura y se citan por ID y versión; este pack no los escribe.
4. Las rutas de código del repositorio no se fijan aquí: las resuelve cada ADR y el `UCM`.
5. Un tipo sin mapeo queda BLOCKED. Solo una instrucción explícita del usuario permite otra ruta, con registro de la excepción; un skill no puede autorizarla.
