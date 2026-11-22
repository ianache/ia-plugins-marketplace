# DDD Domain Design — Output Pathmap

**Base:** raíz del workspace, no la carpeta de instalación del plugin.

## Mapeo por `type` OKF

El mapeo de cada tipo documental y de cada salida auxiliar a su directorio vive solo en [`pathmap.json`](pathmap.json) (`document_types`, `auxiliary` y `orchestrator_root`; versión en `pathmap_version`). Este archivo no repite ese contenido.

## Archivos exclusivos del orchestrator

En `orchestrator_root` de `pathmap.json` (`<run-id>/`): `execution-plan.yaml`, `task-ledger.yaml`, `gate-register.yaml`, `scope-manifest.yaml`, `run-status.md`, evidencias y reportes de ejecución.

## Reglas de ejecución

1. En G0, el orchestrator lee este archivo y `assets/pathmap.json`, comprueba coherencia y resuelve el destino de **cada** output.
2. Transmite a cada skill `workspace_root`, `run_id`, `document_type` (o nombre auxiliar), `output_path`, `pathmap_version` y `gate`.
3. Cada skill escribe directamente en la ruta asignada; no añade `<run-id>` a los documentos de KB. Para evitar colisiones usa IDs y nombres versionados y nunca sobrescribe silenciosamente.
4. El orchestrator valida existencia, ubicación y tipo de cada salida antes de `DONE` o de aprobar un gate.
5. Tipo sin mapeo: `BLOCKED`. No inventar una carpeta de destino.
6. Una ruta alternativa solo procede por instrucción **explícita del usuario**, registrada en el plan con justificación y evidencia; nunca por decisión autónoma de un skill.
7. Los documentos Markdown de dominio cumplen STD-OKF-001 v1.9.0-stable. Las salidas operativas del orchestrator no se clasifican como OKF.

**Gobierno:** las rutas aquí definidas son convenciones de este plugin; su homologación corporativa requiere aprobación.

`CFR-domain-validation.md` es un `CFR` y pasa por `okf_validate.py`. `domain-design-pack.md` lo produce T07 (orchestrator), por lo que es un artefacto operativo excluido del perfil documental.
