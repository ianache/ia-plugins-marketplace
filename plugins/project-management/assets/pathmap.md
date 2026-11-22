# Project Management — Workspace Output Pathmap

**Workspace root:** directorio de trabajo donde se invoca el plugin, no su directorio de instalación.
**Alcance:** los seis skills especializados y el orchestrator.

## Reglas obligatorias

1. El orchestrator lee este archivo al comenzar G0 y resuelve cada entregable por el `type` de su frontmatter OKF **antes de encargar su generación**.
2. Cada entregable va en el directorio que `pathmap.json` fija para su tipo. Los archivos operativos del orchestrator van exclusivamente a `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`). Ninguna ruta canónica incluye `<run-id>`.
3. La ruta no se deduce del nombre del skill ni de la extensión; se deriva del tipo documental. Un tipo sin mapping queda **BLOCKED** hasta resolverlo y registrar la decisión.
4. Solo una instrucción explícita del usuario permite sobrescribir la ruta; se registra texto original, ruta resuelta, actor, justificación y alcance. Los skills no pueden autoautorizar excepciones.
5. No sobrescribir documentos existentes sin decisión explícita de evolución o versionado. Preservar links, IDs y provenance.
6. Cada skill valida `type`, `output_dir`, existencia y conformidad de frontmatter según `STD-OKF-001-v0.1.0-stable` antes de reportar un entregable listo.
7. Los JSON/YAML de evidencia y los contratos operativos no son documentos OKF; se guardan en `<orchestrator_root>/<run-id>/`.

## Mapeo por document type

El mapeo de cada tipo documental a su directorio (y los metadatos de cada artefacto) vive solo en [`pathmap.json`](pathmap.json), bajo `document_types` y `artifacts`; su versión está en `pathmap_version`. Este archivo no repite ese contenido.

**Prefijo del archivo = `id` del frontmatter.** `validate_pathmap.py` rechaza un archivo cuyo nombre no comience con su `id`.

**Un `RSK` por iniciativa** (registro con filas de riesgos, dependencias y bloqueos); **un `CHG` por solicitud de cambio**; **un `SSP` por Sprint (con `dsp_id` del DSP aprobado)**; **un `STR` por periodo**.

El resultado de publicación GitLab es un payload de ejecución que el especialista devuelve al orchestrator; solo el orchestrator persiste manifiestos, `gate-report` y evidencia bajo `<orchestrator_root>/<run-id>`. Si el resultado se presenta en un documento para lectores, se incorpora a un `STR` o `CLS` tipado existente.

## Documentos de otros packs (solo lectura)
`business/` (BCP, BO, BCAP, BR, TRM, IMD) de `business-knowledge`; `requirements/` (US, RCP, IMP y DSP en `requirements/scope-packs/`) de `requirements-engineering`. Este pack los cita por ID en `related` y `sources`, sin escribirlos.

## Gates
- **G0:** cargar pathmap, registrar versión y generar contratos de rutas.
- **G1–G5:** validar los entregables de cada skill y bloquear tipos o rutas no resueltos.
- **G6:** revalidar rutas, metadatos y enlaces con `check_management.py`, verificar aprobación humana y preparar el cierre sin publicar ni cerrar automáticamente.
