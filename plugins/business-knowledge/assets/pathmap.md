# Business Knowledge — Workspace Output Pathmap

**Workspace root:** directorio de trabajo donde se invoca el plugin, no su directorio de instalación.
**Alcance:** los siete skills especializados y el orchestrator.

## Reglas obligatorias

1. El orchestrator lee este archivo al comenzar G0 y resuelve cada entregable por el `type` de su frontmatter OKF **antes de encargar su generación**.
2. Cada entregable va en el directorio que `pathmap.json` fija para su tipo. Los archivos operativos del orchestrator van exclusivamente a `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`). Ninguna ruta canónica incluye `<run-id>`.
3. La ruta no se deduce del nombre del skill ni de la extensión; se deriva del tipo documental. Un tipo sin mapping queda **BLOCKED** hasta resolverlo y registrar la decisión.
4. Solo una instrucción explícita del usuario permite sobrescribir la ruta. El orchestrator registra texto original, ruta resuelta, actor, justificación y alcance; los skills no pueden autoautorizar excepciones.
5. No sobrescribir documentos existentes sin decisión explícita de evolución o versionado. Preservar links, IDs y provenance.
6. Cada skill valida `type`, `output_dir`, existencia y conformidad de frontmatter según `STD-OKF-001-v0.1.0-stable` antes de reportar un entregable listo. Solo se admiten tipos registrados en el estándar.
7. Los archivos JSON/YAML de evidencia o contratos operativos no son documentos OKF; se guardan junto al entregable que respaldan o en `<orchestrator_root>/<run-id>/`.

## Mapeo por document type

El mapeo de cada tipo documental a su directorio (y los metadatos de cada artefacto) vive solo en [`pathmap.json`](pathmap.json), bajo `document_types` y `artifacts`; su versión está en `pathmap_version`. Este archivo no repite ese contenido.

**Prefijo del archivo = `id` del frontmatter.** `validate_pathmap.py` rechaza un archivo cuyo nombre no comience con su `id`.

**Catálogos CTLG:** cada tipo indexado (`BR`, `TRM`) tiene un único catálogo `type: CTLG` en su directorio (`CTLG-BR.md`, `CTLG-TRM.md`), declarado en `catalogs` de `pathmap.json`. Un catálogo lista ID, título, estado y versión de cada documento con enlace, y nunca repite sus definiciones. No se genera `index.md`: es un archivo reservado que el contrato de la KB ya no usa. `validate_pathmap.py --check-catalog BR|TRM` verifica la correspondencia 1:1 entre documentos y filas.

El handoff y la matriz de trazabilidad se incorporan como secciones del `BCP` final tipado. `gate-report` y evidencia de ejecución son registros operativos: solo el orchestrator los persiste en `<orchestrator_root>/<run-id>/` a partir del resultado estructurado del especialista.

## Gates

- **G0:** cargar pathmap, registrar versión y generar contratos de rutas.
- **G1–G5:** validar los entregables de cada skill y bloquear tipos o rutas no resueltos.
- **G6:** revalidar rutas, metadatos e índices con `check_pack.py`, verificar aprobación humana y preparar el handoff sin publicar automáticamente.
